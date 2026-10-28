import { test } from 'node:test'
import assert from 'node:assert/strict'
import { useChat } from '../useChat.js'
import { appendCaption, conversationHistory } from '../domain.js'
import { deferred, flush, harness } from './fakes.js'

test('typing works after denied microphone permission and retains the draft through setup', async () => {
  const h = harness()
  h.environment.getUserMedia = async () => { throw Object.assign(new Error('denied'), { name: 'NotAllowedError' }) }
  const chat = useChat(h.options)
  chat.draft.value = 'A fictional question.'
  assert.equal(h.calls.config.length, 0)
  await chat.voice.start()
  assert.equal(chat.voiceState.value.status, 'error'); assert.equal(chat.draft.value, 'A fictional question.')
  await chat.send()
  assert.equal(h.calls.text.length, 1); assert.equal(h.calls.sessions.length, 0)
  assert.deepEqual(chat.messages.value.map(message => message.role), ['user', 'assistant'])
  assert.equal(chat.draft.value, '')
  chat.dispose(); assert.deepEqual(chat.messages.value, [])
})

test('voice HTTP failure cannot disable text sending', async () => {
  const h = harness(); h.api.createVoiceSession = async () => { throw new Error('server failure') }
  const chat = useChat(h.options), pending = chat.voice.start()
  await flush(); h.peer.completeIce(); await pending
  assert.equal(chat.voiceState.value.status, 'error')
  chat.draft.value = 'Keep using text'; await chat.send()
  assert.equal(chat.messages.value.at(-1).text, 'A fictional reply.'); chat.dispose()
})

test('typed reply failure keeps editable draft, does not invent an assistant bubble or auto-retry', async () => {
  const h = harness(); let calls = 0
  h.api.sendTextMessage = async () => { calls++; throw new Error('private detail') }
  const chat = useChat(h.options); chat.draft.value = 'A fictional message'; await chat.send()
  assert.equal(calls, 1); assert.equal(chat.draft.value, 'A fictional message')
  assert.equal(chat.messages.value.length, 1); assert.equal(chat.messages.value[0].status, 'failed')
  assert.match(chat.textError.value, /draft/); assert.doesNotMatch(chat.textError.value, /private/)
  chat.dispose()
})

test('leaving aborts pending text and ignores its late reply', async () => {
  const h = harness(), reply = deferred(); let signal
  h.api.sendTextMessage = (_text, _history, options) => { signal = options.signal; return reply.promise }
  const chat = useChat(h.options); chat.draft.value = 'Leave before reply'; const pending = chat.send()
  chat.dispose(); assert.equal(signal.aborted, true)
  reply.resolve({ reply: 'Too late' }); await pending
  assert.deepEqual(chat.messages.value, []); assert.equal(chat.draft.value, '')
})

test('caption grouping preserves fragments and spaces across overlapping speakers', () => {
  const messages = []
  appendCaption(messages, { session: 1, id: 'u1', role: 'user', text: 'I think', start: 0, end: 300 })
  appendCaption(messages, { session: 1, id: 'a1', role: 'assistant', text: 'Mm-hmm.', start: 100, end: 250 })
  appendCaption(messages, { session: 1, id: 'u2', role: 'user', text: ' I think so.', start: 300, end: 600 })
  assert.equal(messages.length, 2); assert.equal(messages[0].text, 'I think I think so.')
  assert.deepEqual(conversationHistory(messages), [{ role: 'user', content: 'I think I think so.' }, { role: 'assistant', content: 'Mm-hmm.' }])
})

test('shared context is bounded and excludes failed drafts', async () => {
  const h = harness(), chat = useChat(h.options)
  chat.draft.value = 'First'; await chat.send(); chat.draft.value = 'Next'; await chat.send()
  assert.deepEqual(h.calls.text[1].history.map(message => message.role), ['user', 'assistant'])
  assert.ok(conversationHistory(Array.from({ length: 30 }, () => ({ source: 'text', status: 'complete', role: 'user', text: 'x'.repeat(4000) }))).length <= 1)
  chat.dispose()
})

test('voice startup retains the visible conversation and supplies shared text/caption context', async () => {
  const h = harness(), chat = useChat(h.options)
  chat.draft.value = 'Fictional typed context'; await chat.send()
  appendCaption(chat.messages.value, { session: 99, id: 'old', role: 'user', text: 'A fictional earlier caption.', start: 0, end: 300 })
  const pending = chat.voice.start(); await flush(); h.peer.completeIce(); await pending
  assert.equal(chat.messages.value.length, 3)
  assert.deepEqual(h.calls.sessions[0].history, [
    { role: 'user', content: 'Fictional typed context' },
    { role: 'assistant', content: 'A fictional reply.' },
    { role: 'user', content: 'A fictional earlier caption.' },
  ])
  assert.equal(h.calls.sessions[0].options, undefined)
  chat.dispose(); assert.deepEqual(chat.messages.value, [])
})

test('short sequential exchanges create separate user/assistant bubbles instead of merging turns', () => {
  const messages = []
  for (const [id, role, text, start, end] of [
    ['u1', 'user', 'Hi', 0, 200], ['a1', 'assistant', 'Hello', 250, 450],
    ['u2', 'user', 'Next question', 500, 700], ['a2', 'assistant', 'Go ahead', 750, 950],
  ]) appendCaption(messages, { session: 1, id, role, text, start, end })
  assert.deepEqual(messages.map(message => message.role), ['user', 'assistant', 'user', 'assistant'])
  assert.deepEqual(messages.map(message => message.text), ['Hi', 'Hello', 'Next question', 'Go ahead'])
})

test('late fragments preserve text and can split a previously merged bubble at a late speaker change', () => {
  const messages = []
  const fragment = (id, role, text, start, end) => ({ session: 1, id, role, text, start, end })
  appendCaption(messages, fragment('u2', 'user', 'Next', 600, 800))
  appendCaption(messages, fragment('u1', 'user', 'First', 0, 200))
  assert.equal(messages.length, 1); assert.equal(messages[0].text, 'FirstNext')
  appendCaption(messages, fragment('a1', 'assistant', 'Okay', 300, 500))
  appendCaption(messages, fragment('u1', 'user', 'First', 0, 200))
  assert.deepEqual(messages.map(message => message.text), ['First', 'Okay', 'Next'])
})

test('a speech pause or resumed assistant after interruption gets a new bubble', () => {
  const messages = []
  for (const [id, role, start, end] of [['a1', 'assistant', 0, 500], ['u1', 'user', 200, 400], ['a2', 'assistant', 600, 900], ['a3', 'assistant', 2100, 2300]]) {
    appendCaption(messages, { session: 1, id, role, text: id, start, end })
  }
  assert.deepEqual(messages.map(message => message.text), ['a1', 'u1', 'a2', 'a3'])
})

test('speaking then typing shares captions and stops the microphone; returning to voice keeps all bubbles', async () => {
  const h = harness(), chat = useChat(h.options)
  const pending = chat.voice.start(); await flush(); h.peer.completeIce(); await pending
  h.event({ type: 'session.started', session: { id: 'live_fake' } })
  h.event({ type: 'session.input_transcript.delta', event_id: 'u1', delta: 'My fictional topic', start_ms: 0, end_ms: 300 })
  h.event({ type: 'session.output_transcript.delta', event_id: 'a1', delta: 'Tell me more', start_ms: 350, end_ms: 700 })
  chat.draft.value = 'Continuing by typing'; await chat.send()
  assert.equal(h.track.stops, 1)
  assert.deepEqual(h.calls.text[0].history, [
    { role: 'user', content: 'My fictional topic' }, { role: 'assistant', content: 'Tell me more' },
  ])
  assert.deepEqual(chat.messages.value.map(message => message.role), ['user', 'assistant', 'user', 'assistant'])
  await chat.voice.start()
  assert.equal(h.calls.sessions[1].history.length, 4)
  assert.equal(chat.messages.value.length, 4)
  chat.dispose(); assert.deepEqual(chat.messages.value, [])
})

test('shared context keeps whole messages and enforces role, completion and UTF-8 limits', () => {
  const messages = [
    { role: 'system', status: 'complete', text: 'Never send' },
    { role: 'user', status: 'failed', source: 'text', text: 'Failed draft' },
    ...Array.from({ length: 20 }, (_, i) => ({ role: 'user', status: 'complete', source: 'text', text: `fictional ${i}` })),
  ]
  assert.equal(conversationHistory(messages).length, 16)
  assert.equal(conversationHistory([{ role: 'user', source: 'voice', text: 'é'.repeat(3000) }])[0].content.length, 3000)
  assert.deepEqual(conversationHistory([{ role: 'user', source: 'voice', text: 'é'.repeat(3001) }]), [])
})

test('voice storage batching preserves long Unicode text without splitting code points', async () => {
  const { voiceTranscriptBatches } = await import('../domain.js')
  const text = '🙂'.repeat(5000)
  const batches = voiceTranscriptBatches([{ role: 'user', text }])
  assert.ok(batches.length > 1)
  assert.equal(batches.flat().map(message => message.content).join(''), text)
  assert.ok(batches.every(batch => batch.length <= 50 && batch.reduce((sum, message) => sum + new TextEncoder().encode(message.content).length, 0) <= 8000))
})
