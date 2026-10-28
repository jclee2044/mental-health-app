import { test } from 'node:test'
import assert from 'node:assert/strict'
import { Dictation, MAX_RECORDING_BYTES } from '../dictation.js'
import { useChat } from '../useChat.js'
import { bindVoiceLifecycle, interruptVoice } from '../lifecycle.js'
import { deferred, flush, harness, streamOf, Track, Target } from './fakes.js'

function setup() {
  const track = new Track(), timers = new Map(), texts = [], uploads = []
  let id = 0
  const recorder = {
    mimeType: 'audio/webm;codecs=opus', state: 'inactive', starts: 0, stops: 0,
    start() { this.starts++; this.state = 'recording' },
    stop() {
      this.stops++; this.state = 'inactive'
      this.ondataavailable?.({ data: new Blob(['fictional audio']) }); this.onstop?.()
    },
  }
  const environment = {
    getUserMedia: async () => streamOf(track), createRecorder: () => recorder,
    encode: async () => 'fictional-base64',
    setTimeout(callback) { timers.set(++id, callback); return id }, clearTimeout: timer => timers.delete(timer),
  }
  const transcribe = async (...args) => { uploads.push(args); return { text: 'A small win' } }
  const dictation = new Dictation({ environment, transcribe, appendText: text => texts.push(text) })
  return { environment, transcribe, track, recorder, timers, texts, uploads, dictation }
}

test('explicit recording, finish, released tracks and one upload yield editable text', async () => {
  const h = setup(); assert.equal(h.recorder.starts, 0)
  await h.dictation.start(); await h.dictation.start()
  assert.equal(h.recorder.starts, 1); assert.equal(h.dictation.state.status, 'recording')
  assert.equal(h.uploads.length, 0)
  h.dictation.finish(); h.dictation.finish(); await flush()
  assert.equal(h.uploads.length, 1); assert.equal(h.track.readyState, 'ended')
  assert.deepEqual(h.texts, ['A small win']); assert.equal(h.timers.size, 0)
})

test('denied microphone and unsupported recorder keep text usable without upload', async () => {
  for (const error of ['denied', 'unsupported']) {
    const h = setup()
    if (error === 'denied') h.environment.getUserMedia = async () => { throw Object.assign(new Error('private'), { name: 'NotAllowedError' }) }
    else h.environment.createRecorder = () => { throw new Error('private') }
    await h.dictation.start()
    assert.equal(h.dictation.state.status, 'error'); assert.equal(h.uploads.length, 0)
    assert.doesNotMatch(h.dictation.state.message, /private/)
    if (error === 'unsupported') assert.equal(h.track.readyState, 'ended')
  }
})

test('cancellation during ignored permission releases late tracks with no upload', async () => {
  const h = setup(), media = deferred(); h.environment.getUserMedia = () => media.promise
  const pending = h.dictation.start(); h.dictation.stop(); media.resolve(streamOf(h.track)); await pending
  assert.equal(h.track.readyState, 'ended'); assert.equal(h.recorder.starts, 0); assert.equal(h.uploads.length, 0)
})

test('cancellation aborts upload and ignores late transcript', async () => {
  const h = setup(), result = deferred()
  h.dictation.transcribe = (...args) => { h.uploads.push(args); return result.promise }
  await h.dictation.start(); h.dictation.finish(); await flush()
  const signal = h.uploads[0][2].signal
  h.dictation.stop(); assert.equal(signal.aborted, true)
  result.resolve({ text: 'Late words' }); await flush()
  assert.deepEqual(h.texts, []); assert.equal(h.timers.size, 0)
})

test('recording size, recording timer and upload timeout are bounded', async () => {
  const oversized = setup(); await oversized.dictation.start()
  oversized.recorder.ondataavailable({ data: { size: MAX_RECORDING_BYTES + 1 } })
  assert.equal(oversized.dictation.state.status, 'error'); assert.equal(oversized.uploads.length, 0)
  const timed = setup(); await timed.dictation.start(); [...timed.timers.values()][0](); await flush()
  assert.equal(timed.uploads.length, 1)
  const hung = setup(); hung.dictation.transcribe = () => new Promise(() => {})
  await hung.dictation.start(); hung.dictation.finish(); await flush(); [...hung.timers.values()][0]()
  assert.equal(hung.dictation.state.status, 'error'); assert.equal(hung.track.readyState, 'ended')
})

test('failed or invalid provider text never replaces the draft', async () => {
  for (const response of [{ text: '' }, { text: 'x'.repeat(4001) }, { text: '界'.repeat(3000) }, null]) {
    const h = setup(); h.dictation.transcribe = async () => response
    await h.dictation.start(); h.dictation.finish(); await flush()
    assert.deepEqual(h.texts, []); assert.equal(h.dictation.state.status, 'error')
  }
})

test('transcript appends to the latest edited draft, never auto-sends or persists', async () => {
  const h = harness(), d = setup(), result = deferred()
  h.api.transcribeRecording = () => result.promise
  const chat = useChat({ ...h.options, dictationEnvironment: d.environment })
  chat.draft.value = 'Before'; await chat.dictation.start(); chat.dictation.finish(); await flush()
  chat.draft.value = 'Edited'; result.resolve({ text: 'A small win' }); await flush()
  assert.equal(chat.draft.value, 'Edited A small win'); assert.equal(h.calls.text.length, 0); assert.equal(h.calls.saves.length, 0)
  chat.dispose()
})

test('sending text or starting voice cancels dictation instead of uploading', async () => {
  for (const action of ['send', 'voice']) {
    const h = harness(), d = setup(); h.api.transcribeRecording = d.transcribe
    const chat = useChat({ ...h.options, dictationEnvironment: d.environment })
    chat.draft.value = 'Typed draft'; await chat.dictation.start()
    if (action === 'send') await chat.send()
    else { const pending = chat.voice.start(); await flush(); h.peer.completeIce(); await pending }
    assert.equal(d.uploads.length, 0); assert.equal(d.track.readyState, 'ended')
    chat.dispose()
  }
})

for (const exit of ['hidden', 'hashchange', 'pagehide', 'beforeunload', 'Emergency', 'unmount']) {
  test(`${exit} discards recording, releases capture and rejects late callbacks`, async () => {
    const h = setup(), document = new Target(), window = new Target()
    const unbind = bindVoiceLifecycle(h.dictation, document, window)
    await h.dictation.start(); const late = h.recorder.onstop
    if (exit === 'unmount') unbind()
    else if (exit === 'Emergency') interruptVoice(h.dictation, true)
    else if (exit === 'hidden') { document.hidden = true; document.emit('visibilitychange') }
    else window.emit(exit)
    late(); await flush()
    assert.equal(h.uploads.length, 0); assert.equal(h.track.readyState, 'ended')
    unbind(); assert.equal(document.count() + window.count(), 0)
  })
}
