// Shared by the real component and focused mocks; no model/API dependency.
export function interruptVoice(voice, interrupted) {
  if (interrupted) voice.stop('Voice ended while the panel is open. Select the microphone to start fresh.', true)
}

export function bindVoiceLifecycle(voice, document, window) {
  const away = () => voice.stop('Voice ended while you were away. Select the microphone to start fresh.', true)
  const visibility = () => { if (document.hidden) away() }
  const listeners = [
    [document, 'visibilitychange', visibility],
    [window, 'hashchange', away],
    [window, 'pagehide', away],
    [window, 'beforeunload', away],
  ]
  listeners.forEach(([target, name, listener]) => target.addEventListener(name, listener))
  let disposed = false
  return () => {
    if (disposed) return
    disposed = true
    listeners.forEach(([target, name, listener]) => target.removeEventListener(name, listener))
    voice.dispose()
  }
}
