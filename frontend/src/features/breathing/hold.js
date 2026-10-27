// One input owns a hold. Pointer cancellation and focus loss count as release.
export function createBreathingHold({ start, release }) {
  let owner = null
  function press(input) {
    if (owner !== null) return false
    owner = input
    start()
    return true
  }
  function end(input) {
    if (owner === null || (input !== undefined && owner !== input)) return
    owner = null
    release()
  }
  return {
    get active() { return owner !== null },
    pointerDown(event) {
      if (event.button !== 0 || event.isPrimary === false || owner !== null) return
      event.preventDefault()
      event.currentTarget.focus({ preventScroll: true })
      event.currentTarget.setPointerCapture(event.pointerId)
      press(`pointer:${event.pointerId}`)
    },
    pointerUp(event) { end(`pointer:${event.pointerId}`) },
    keyDown(event) {
      if (![' ', 'Enter'].includes(event.key)) return
      event.preventDefault()
      if (!event.repeat) press(`key:${event.key}`)
    },
    keyUp(event) {
      if (![' ', 'Enter'].includes(event.key)) return
      event.preventDefault()
      end(`key:${event.key}`)
    },
    blur() { if (owner?.startsWith('key:')) end() },
    cancel() { end() },
  }
}
