export class BreathAudio {
  constructor(createContext = () => new (window.AudioContext || window.webkitAudioContext)(), loadRecordings = async () => ({})) {
    this.createContext = createContext
    this.loadRecordings = loadRecordings
    this.context = null
    this.buffers = null
    this.loading = null
    this.nodes = []
    this.closed = false
  }
  async unlock() {
    if (this.closed) throw new Error('Audio is closed.')
    this.context ??= this.createContext()
    // Resume during the initiating user gesture, before waiting for decoding.
    const resumed = this.context.state === 'suspended' ? this.context.resume() : Promise.resolve()
    this.loading ??= this.loadRecordings(this.context).catch(error => { this.loading = null; throw error })
    const [, buffers] = await Promise.all([resumed, this.loading])
    if (this.closed || this.context.state !== 'running') throw new Error('Audio is unavailable.')
    for (const [phase, duration] of [['inhale', 4], ['exhale', 6]]) {
      if (phase === 'inhale' && !buffers[phase]) continue
      if (!buffers[phase] || Math.abs(buffers[phase].duration - duration) > .02) throw new Error('Breathing recording is unavailable.')
    }
    this.buffers = buffers
  }
  play(phase, progress = 0) {
    this.stop()
    if (this.closed || !this.buffers || this.context?.state !== 'running') return false
    if (!['inhale', 'exhale'].includes(phase) || !this.buffers[phase]) return false
    const ctx = this.context
    const duration = phase === 'inhale' ? 4 : 6
    const offset = duration * Math.max(0, Math.min(1, progress))
    const remaining = duration - offset
    if (remaining <= 0) return false
    const source = ctx.createBufferSource()
    source.buffer = this.buffers[phase]
    const gain = ctx.createGain()
    const fade = Math.min(.04, remaining / 2)
    gain.gain.setValueAtTime(0, ctx.currentTime)
    gain.gain.linearRampToValueAtTime(.65, ctx.currentTime + fade)
    gain.gain.setValueAtTime(.65, ctx.currentTime + remaining - fade)
    gain.gain.linearRampToValueAtTime(0, ctx.currentTime + remaining)
    source.connect(gain); gain.connect(ctx.destination)
    source.start(ctx.currentTime, offset)
    source.stop(ctx.currentTime + remaining)
    this.nodes = [source, gain]
    return true
  }
  stop() {
    if (this.nodes.length) { try { this.nodes[0].stop() } catch { /* Already ended. */ } }
    for (const node of this.nodes) { try { node.disconnect() } catch { /* Already disconnected. */ } }
    this.nodes = []
  }
  close() { this.closed = true; this.stop(); this.buffers = null; this.context?.close().catch(() => {}) }
}
