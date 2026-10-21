// Original synthesized airy cues; no downloads, recordings, microphone, or speech service.
export class BreathAudio {
  constructor(createContext = () => new (window.AudioContext || window.webkitAudioContext)()) {
    this.createContext = createContext
    this.context = null
    this.nodes = []
  }
  async unlock() {
    this.context ??= this.createContext()
    if (this.context.state === 'suspended') await this.context.resume()
    if (this.context.state !== 'running') throw new Error('Audio is unavailable.')
  }
  play(phase, progress = 0) {
    this.stop()
    if (!this.context || this.context.state !== 'running') return false
    if (!['inhale', 'exhale'].includes(phase)) return false
    const ctx = this.context
    const duration = phase === 'inhale' ? 4 : 6
    const startProgress = Math.max(0, Math.min(.999, progress))
    const remaining = duration * (1 - startProgress)
    const buffer = ctx.createBuffer(1, Math.ceil(ctx.sampleRate * duration), ctx.sampleRate)
    const samples = buffer.getChannelData(0)
    let seed = 12345, smooth = 0
    for (let i = 0; i < samples.length; i++) {
      seed = (seed * 16807) % 2147483647
      smooth = .6 * smooth + .4 * (seed / 1073741823.5 - 1)
      samples[i] = smooth
    }
    const source = ctx.createBufferSource()
    source.buffer = buffer
    const filter = ctx.createBiquadFilter()
    filter.type = 'bandpass'; filter.Q.value = .65
    const low = phase === 'inhale' ? 500 : 1400
    const high = phase === 'inhale' ? 1400 : 500
    filter.frequency.setValueAtTime(low + (high - low) * startProgress, ctx.currentTime)
    filter.frequency.linearRampToValueAtTime(high, ctx.currentTime + remaining)
    const gain = ctx.createGain()
    gain.gain.setValueAtTime(0, ctx.currentTime)
    for (let step = 1; step <= 40; step++) {
      const fraction = step / 40
      const position = startProgress + (1 - startProgress) * fraction
      gain.gain.linearRampToValueAtTime(.22 * Math.sin(Math.PI * position), ctx.currentTime + remaining * fraction)
    }
    source.connect(filter); filter.connect(gain); gain.connect(ctx.destination)
    source.start(ctx.currentTime, duration * startProgress)
    source.stop(ctx.currentTime + remaining)
    this.nodes = [source, filter, gain]
    return true
  }
  stop() {
    if (this.nodes.length) { try { this.nodes[0].stop() } catch { /* Already ended. */ } }
    for (const node of this.nodes) { try { node.disconnect() } catch { /* Already disconnected. */ } }
    this.nodes = []
  }
  close() { this.stop(); this.context?.close().catch(() => {}) }
}
