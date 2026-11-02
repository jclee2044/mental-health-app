import { test } from 'node:test'
import assert from 'node:assert/strict'
import { ref } from 'vue'
import { setupView } from '../../../../tests/setupView.js'

test('six cycles cue once independently of saving; early release shows an ended result with its own cue', async () => {
  const original = { document: globalThis.document, window: globalThis.window,
    requestAnimationFrame: globalThis.requestAnimationFrame, cancelAnimationFrame: globalThis.cancelAnimationFrame }
  const enabled = ref(false)
  const cues = [], endings = [], records = [], navigations = []
  let stopped = 0
  globalThis.document = { hidden: false, addEventListener() {}, removeEventListener() {} }
  globalThis.window = { addEventListener() {}, removeEventListener() {} }
  globalThis.requestAnimationFrame = () => 1
  globalThis.cancelAnimationFrame = () => {}
  globalThis.breathingSound = { arm: () => 1, complete: ticket => cues.push(ticket), stop() {} }
  globalThis.endingSound = { arm: () => 2, complete: ticket => endings.push(ticket), stop() { stopped++ } }
  const view = await setupView(new URL('../BreathingView.vue', import.meta.url), [
    [/import endingCue from [^\n]+/, "const endingCue = 'open-tones'"],
    [/import completionCue from [^\n]+/, "const completionCue = 'warm-keys'"],
    [/import AppIcon from [^\n]+/, 'const AppIcon = {}'],
    [/import \{ useCompletionSound \} from [^\n]+/, "const useCompletionSound = (_enabled, _interrupted, cue) => { if (!['warm-keys', 'open-tones'].includes(cue)) throw new Error('Unexpected cue'); return cue === 'open-tones' ? globalThis.endingSound : globalThis.breathingSound }"],
    [/import \{ decodeRecordings \} from [^\n]+/, 'const decodeRecordings = async () => ({})'],
  ], { interrupted: false, reducedMotion: false }, (event, value) => { if (event === 'record') records.push(value); if (event === 'navigate') navigations.push(value) }, { appSoundEnabled: enabled })
  const key = { key: ' ', repeat: false, preventDefault() {} }
  try {
    assert.equal(view.state.soundEnabled, enabled)
    let breathStops = 0
    view.state.audio.unlock = async () => {}
    view.state.audio.stop = () => { breathStops++ }
    enabled.value = true
    enabled.value = false
    assert.ok(breathStops > 0) // Global mute immediately stops breathing playback.
    view.state.hold.keyDown(key)
    view.state.hold.keyUp(key)
    assert.equal(records[0].status, 'ended')
    assert.deepEqual(cues, [])
    assert.deepEqual(endings, [2])
    assert.equal(view.state.state.value, 'ended')
    assert.equal(view.state.heading.value, 'Breathing exercise ended.')
    assert.deepEqual(navigations, [])
    view.state.end()
    view.state.hold.keyDown(key)
    view.state.hold.keyUp(key)
    assert.equal(records.length, 1)
    assert.deepEqual(endings, [2])
    // Fresh navigation mounts a new view; use ready here to exercise completion.
    view.state.state.value = 'ready'; view.state.clock.state = 'ready'
    view.state.hold.keyDown(key)
    const anchor = view.state.clock.anchor
    for (let elapsed = 1000; elapsed <= 63000; elapsed += 1000) view.state.render(anchor + elapsed)
    assert.equal(records.at(-1).status, 'completed')
    assert.deepEqual(cues, [1])
    view.state.render(anchor + 63000)
    view.state.hold.keyUp(key)
    assert.deepEqual(cues, [1])
    assert.deepEqual(endings, [2]) // Full completion uses warm keys, not the early-end cue.
    view.state.hold.keyDown(key)
    view.state.pause()
    view.state.loseFocus()
    assert.equal(view.state.state.value, 'ended')
    assert.equal(records.at(-1).status, 'ended')
    assert.equal(stopped, 1) // Invalidates the queued ending cue on window blur.
    assert.deepEqual(navigations, [])
  } finally {
    view.unmount()
    Object.assign(globalThis, original)
    delete globalThis.breathingSound
    delete globalThis.endingSound
  }
})
