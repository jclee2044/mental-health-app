import { test } from 'node:test'
import assert from 'node:assert/strict'
import { effectScope, nextTick, ref, watch } from 'vue'
import { useTranscriptScroll } from '../useTranscriptScroll.js'

test('scrolls the chat container after render for new messages and growing captions', async () => {
  const scope = effectScope(), messages = ref([])
  const chatWindow = ref({ scrollTop: 0, scrollHeight: 0 })
  scope.run(() => {
    useTranscriptScroll(chatWindow, messages)
    // Simulate the rendered height changing before the post-render scroll.
    watch(() => messages.value.map(message => message.text).join(''), text => {
      chatWindow.value.scrollHeight = text.length * 20
    })
  })
  try {
    messages.value.push({ id: 'voice-1', text: 'First caption' })
    await nextTick()
    assert.equal(chatWindow.value.scrollTop, 260)
    chatWindow.value.scrollTop = 0
    messages.value[0].text += ' and more words'
    await nextTick()
    assert.equal(chatWindow.value.scrollTop, 560)
    messages.value.push({ id: 'voice-2', text: 'Reply' })
    await nextTick()
    assert.equal(chatWindow.value.scrollTop, 660)
    chatWindow.value = null
    messages.value[1].text += ' after exit'
    scope.stop()
    await nextTick()
  } finally { scope.stop() }
})
