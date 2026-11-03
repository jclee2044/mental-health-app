// Keep Enter available to input-method editors while composing characters.
export function submitOnEnter(event, send) {
  if (event.key !== 'Enter' || event.shiftKey || event.isComposing || event.keyCode === 229) return
  event.preventDefault()
  if (!event.repeat) send()
}
