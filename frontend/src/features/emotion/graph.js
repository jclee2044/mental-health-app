// Pointer handling is local to the graph; no HTTP or animation timers.
export function graphInteraction(select) {
  let pointer = null
  function place(event) {
    const bounds = event.currentTarget.getBoundingClientRect()
    if (!bounds.width || !bounds.height) return
    const clamp = value => Math.round(Math.max(-100, Math.min(100, value)))
    select(clamp((event.clientX - bounds.left) / bounds.width * 200 - 100),
      clamp(100 - (event.clientY - bounds.top) / bounds.height * 200))
  }
  return {
    down(event) {
      if (pointer !== null || event.isPrimary === false || event.button !== 0) return
      pointer = event.pointerId
      event.currentTarget.setPointerCapture(pointer)
      place(event)
    },
    move(event) { if (pointer === event.pointerId) place(event) },
    up(event) {
      if (pointer !== event.pointerId) return
      place(event)
      pointer = null
      if (event.currentTarget.hasPointerCapture(event.pointerId)) event.currentTarget.releasePointerCapture(event.pointerId)
    },
    cancel(event) { if (pointer === event.pointerId) pointer = null },
  }
}
