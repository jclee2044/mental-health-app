import { test } from 'node:test'
import assert from 'node:assert/strict'
import { ref } from 'vue'
import { setupView } from '../../../../tests/setupView.js'

test('global sound mutes current and new assistant playback without changing microphone or session', async () => {
  const original = { document: globalThis.document, window: globalThis.window }
  globalThis.document = { addEventListener() {}, removeEventListener() {} }
  globalThis.window = { addEventListener() {}, removeEventListener() {} }
  let microphoneCalls = 0, stopCalls = 0
  globalThis.outputChatMock = {
    messages: ref([]), draft: ref(''), textBusy: ref(false), textError: ref(''),
    voiceState: ref({ status: 'active', microphoneMuted: false }),
    voice: { toggleMute() { microphoneCalls++ }, stop() { stopCalls++ }, dispose() {} },
    dictation: { stop() {}, dispose() {} }, dictationState: ref({ status: 'idle' }),
    send() {}, dispose() {},
  }
  const enabled = ref(false)
  const view = await setupView(new URL('../ChatView.vue', import.meta.url), [
    [/import AppIcon from [^\n]+/, 'const AppIcon = {}'],
    [/import PersonalMemoryPanel from [^\n]+/, 'const PersonalMemoryPanel = {}'],
    [/import \{ useChat \} from [^\n]+/, 'const useChat = () => globalThis.outputChatMock'],
  ], { interrupted: false }, () => {}, { appSoundEnabled: enabled })
  try {
    const playback = { muted: false }
    view.state.remoteAudio.value = playback
    assert.equal(playback.muted, true)
    enabled.value = true
    assert.equal(playback.muted, false)
    enabled.value = false
    assert.equal(playback.muted, true)
    const replacement = { muted: false }
    view.state.remoteAudio.value = replacement
    assert.equal(replacement.muted, true)
    assert.equal(microphoneCalls, 0)
    assert.equal(stopCalls, 0)
    assert.equal(view.state.voiceState.value.status, 'active')
  } finally { view.unmount(); delete globalThis.outputChatMock; Object.assign(globalThis, original) }
})
