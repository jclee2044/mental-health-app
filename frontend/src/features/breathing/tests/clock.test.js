import { test } from 'node:test'
import assert from 'node:assert/strict'
import { BreathingClock, PATTERN, phaseAt } from '../clock.js'

test('countdown, fixed 4/6 phases, exactly six cycles and completion', () => {
  assert.equal(phaseAt(0).count, 3)
  assert.equal(phaseAt(1000).count, 2)
  assert.equal(phaseAt(2000).count, 1)
  for (let cycle = 0; cycle < 6; cycle++) {
    const start = 3000 + cycle * 10000
    assert.deepEqual(phaseAt(start), { phase: 'inhale', cycle: cycle + 1, count: 4, progress: 0 })
    assert.equal(phaseAt(start + 3999).phase, 'inhale')
    assert.deepEqual(phaseAt(start + 4000), { phase: 'exhale', cycle: cycle + 1, count: 6, progress: 0 })
    assert.equal(phaseAt(start + 9999).phase, 'exhale')
  }
  assert.equal(phaseAt(PATTERN.total).phase, 'complete')
  assert.equal(phaseAt(999999).cycle, 6)
})

test('pause during countdown preserves phase and excludes chosen pause', () => {
  const clock = new BreathingClock()
  clock.start(100)
  clock.pause(1600)
  assert.equal(clock.tick(30000).count, 2)
  clock.resume(31600)
  assert.equal(clock.tick(33100).phase, 'inhale')
  assert.equal(clock.pausedMs, 30000)
})

test('pause mid-inhale, end mid-exhale, and repeated pause/end are safe', () => {
  const clock = new BreathingClock()
  clock.start(0); clock.pause(4500); clock.pause(9000)
  assert.equal(clock.elapsed, 4500)
  clock.resume(14500)
  assert.equal(clock.tick(17000).phase, 'exhale')
  clock.end(19000)
  assert.equal(clock.state, 'ended')
  assert.equal(clock.elapsed, 9000)
  clock.end(40000)
  assert.equal(clock.elapsed, 9000)
})

test('delayed frames do not accumulate timer drift', () => {
  const clock = new BreathingClock()
  clock.start(37)
  for (let time = 37; time < 63037; time += 17.13) clock.tick(time)
  clock.tick(63042)
  assert.equal(clock.state, 'completed')
  assert.equal(clock.elapsed, 63000)
})
