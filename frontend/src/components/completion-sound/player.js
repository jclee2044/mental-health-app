// Each action arms one cue during its user gesture. Cancellation invalidates
// pending decoding and late saves; a cue never queues itself for later replay.
export class CompletionSound {
  constructor(load, allowed, createContext = () => new (window.AudioContext || window.webkitAudioContext)()) {
    this.load = load
    this.allowed = allowed
    this.createContext = createContext
    this.context = null
    this.loading = null
    this.source = null
    this.version = 0
    this.closed = false
  }
  arm() {
    this.stop()
    const ticket = this.version
    if (this.closed || !this.allowed()) return ticket
    try {
      this.context ??= this.createContext()
      const resumed = this.context.state === 'suspended' ? this.context.resume() : Promise.resolve()
      this.loading ??= this.load(this.context).catch(error => { this.loading = null; throw error })
      this.ready = Promise.all([resumed, this.loading]).then(([, buffer]) => buffer).catch(() => null)
    } catch { this.ready = Promise.resolve(null) }
    return ticket
  }
  async complete(ticket) {
    const buffer = await this.ready
    if (ticket !== this.version || this.closed || !this.allowed() || !buffer || this.context?.state !== 'running') return false
    // Consume before starting: repeated completion callbacks cannot replay it.
    this.version++
    try {
      const source = this.context.createBufferSource()
      this.source = source
      source.buffer = buffer
      source.connect(this.context.destination)
      source.onended = () => { source.disconnect(); if (this.source === source) this.source = null }
      source.start()
      return true
    } catch { this.stop(); return false }
  }
  stop() {
    this.version++
    if (this.source) {
      try { this.source.stop() } catch { /* Already ended. */ }
      this.source.disconnect()
      this.source = null
    }
  }
  close() {
    this.closed = true
    this.stop()
    this.context?.close().catch(() => {})
  }
}
