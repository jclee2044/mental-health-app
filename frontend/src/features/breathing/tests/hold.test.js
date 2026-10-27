import { test } from 'node:test'
import assert from 'node:assert/strict'
import { createBreathingHold } from '../hold.js'
import { BreathingClock, PATTERN } from '../clock.js'

function session() {
  let now = 0, starts = 0, releases = 0, captures = []
  const clock = new BreathingClock()
  const hold = createBreathingHold({
    start() { starts++; clock.start(now) },
    release() { releases++; clock.end(now) },
  })
  const pointer = (pointerId = 1, extra = {}) => ({
    pointerId, button: 0, isPrimary: true, preventDefault() {},
    currentTarget: { focus() {}, setPointerCapture(id) { captures.push(id) } }, ...extra,
  })
  const key = (key, repeat = false) => ({ key, repeat, preventDefault() {} })
  return { clock, hold, pointer, key, captures, time(value) { now = value; clock.tick(now) },
    get starts() { return starts }, get releases() { return releases } }
}

test('pointer hold is captured, release ends during countdown or breathing, with no restart', () => {
  for (const elapsed of [1000, 8000, PATTERN.total - 1]) {
    const s = session()
    s.hold.pointerDown(s.pointer())
    assert.deepEqual(s.captures, [1])
    s.time(elapsed)
    s.hold.pointerUp(s.pointer())
    assert.equal(s.clock.state, 'ended')
    s.time(PATTERN.total + 1000)
    assert.equal(s.clock.state, 'ended')
    assert.equal(s.clock.elapsed, elapsed)
    s.hold.pointerUp(s.pointer()) // lostpointercapture after pointerup is harmless
    assert.equal(s.releases, 1)
  }
})

test('only an uninterrupted full hold completes; releasing afterward preserves completion', () => {
  const s = session()
  s.hold.pointerDown(s.pointer())
  s.time(PATTERN.total)
  s.hold.pointerUp(s.pointer())
  assert.equal(s.clock.state, 'completed')
  s.hold.pointerDown(s.pointer())
  assert.equal(s.clock.state, 'running')
  assert.equal(s.clock.elapsed, 0)
})

test('Space and Enter holds ignore repeat, unrelated keys and competing pointers', () => {
  for (const key of [' ', 'Enter']) {
    const s = session()
    s.hold.keyDown(s.key('Escape'))
    assert.equal(s.starts, 0)
    s.hold.keyDown(s.key(key))
    s.hold.keyDown(s.key(key, true))
    s.hold.pointerDown(s.pointer())
    s.hold.pointerUp(s.pointer())
    s.hold.keyUp(s.key('Escape'))
    assert.equal(s.starts, 1)
    assert.equal(s.hold.active, true)
    s.time(5000)
    s.hold.keyUp(s.key(key))
    assert.equal(s.clock.state, 'ended')
  }
})

test('cancellation, focus loss or hidden-page cancellation ends once, including while paused', () => {
  const s = session()
  s.hold.pointerDown(s.pointer())
  s.time(4000)
  s.clock.pause(4000)
  s.hold.cancel()
  s.hold.cancel()
  assert.equal(s.clock.state, 'ended')
  assert.equal(s.releases, 1)
})

test('secondary buttons and unrelated pointer releases cannot take ownership', () => {
  const s = session()
  s.hold.pointerDown(s.pointer(1, { button: 2 }))
  s.hold.pointerDown(s.pointer(2, { isPrimary: false }))
  assert.equal(s.starts, 0)
  s.hold.pointerDown(s.pointer(1))
  s.hold.pointerDown(s.pointer(2))
  s.hold.pointerUp(s.pointer(2))
  assert.equal(s.hold.active, true)
  assert.equal(s.starts, 1)
  s.hold.pointerUp(s.pointer(1))
  assert.equal(s.hold.active, false)
})


test('circle focus loss ends keyboard holds; pointer holds can use Pause/Resume with another input', () => {
  const s = session()
  s.hold.keyDown(s.key(' '))
  s.hold.blur()
  assert.equal(s.clock.state, 'ended')
  s.hold.pointerDown(s.pointer())
  s.hold.blur()
  assert.equal(s.hold.active, true)
  s.hold.cancel()
  assert.equal(s.clock.state, 'ended')
})
