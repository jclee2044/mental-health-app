// Pure browser-independent rules. All times are milliseconds on a monotonic clock.
export const PATTERN = Object.freeze({ id: 'paced-4-6-v1', countdown: 3000, inhale: 4000, exhale: 6000, cycles: 6, total: 63000 })

export function phaseAt(elapsedMs) {
  const elapsed = Math.max(0, Math.min(PATTERN.total, elapsedMs))
  if (elapsed < PATTERN.countdown) return { phase: 'countdown', count: Math.ceil((3000 - elapsed) / 1000), cycle: 0, progress: 0 }
  if (elapsed >= PATTERN.total) return { phase: 'complete', count: 0, cycle: 6, progress: 0 }
  const breathing = elapsed - PATTERN.countdown
  const withinCycle = breathing % 10000
  const inhale = withinCycle < PATTERN.inhale
  const withinPhase = inhale ? withinCycle : withinCycle - PATTERN.inhale
  const duration = inhale ? PATTERN.inhale : PATTERN.exhale
  return { phase: inhale ? 'inhale' : 'exhale', count: Math.ceil((duration - withinPhase) / 1000), cycle: Math.floor(breathing / 10000) + 1, progress: withinPhase / duration }
}

export class BreathingClock {
  state = 'ready'
  elapsed = 0
  pausedMs = 0
  anchor = 0
  pausedAt = null
  start(now) { this.state = 'running'; this.anchor = now; this.elapsed = 0; this.pausedMs = 0 }
  tick(now) {
    if (this.state === 'running') {
      this.elapsed = Math.min(PATTERN.total, Math.max(0, now - this.anchor))
      if (this.elapsed >= PATTERN.total) this.state = 'completed'
    }
    return phaseAt(this.elapsed)
  }
  pause(now) {
    if (this.state !== 'running') return
    this.tick(now)
    if (this.state === 'completed') return
    this.state = 'paused'; this.pausedAt = now
  }
  resume(now) {
    if (this.state !== 'paused') return
    this.pausedMs += Math.max(0, now - this.pausedAt)
    this.anchor = now - this.elapsed
    this.pausedAt = null; this.state = 'running'
  }
  end(now) {
    if (this.state === 'ready' || this.state === 'ended') return
    if (this.state === 'paused') { this.pausedMs += Math.max(0, now - this.pausedAt); this.pausedAt = null }
    this.tick(now)
    if (this.state !== 'completed') this.state = 'ended'
  }
}
