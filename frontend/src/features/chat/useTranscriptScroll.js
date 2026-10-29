import { watch } from 'vue'

export function useTranscriptScroll(chatWindow, messages) {
  // Caption deltas can grow a bubble without changing the message count.
  // Wait for Vue to render before reading the container's new height.
  watch(() => messages.value.map(({ id, text, status }) => [id, text, status]), () => {
    const window = chatWindow.value
    if (window) window.scrollTop = window.scrollHeight
  }, { flush: 'post' })
}
