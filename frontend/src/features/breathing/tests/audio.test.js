import { test } from 'node:test'
import assert from 'node:assert/strict'
import { BreathAudio } from '../audio.js'

const recordings = { inhale: { duration: 4 }, exhale: { duration: 6 } }
function fakeContext() {
  const events = [], sources = []
  const parameter = () => ({ setValueAtTime: (...args) => events.push(['set', ...args]), linearRampToValueAtTime: (...args) => events.push(['ramp', ...args]) })
  const node = () => ({ connect() {}, disconnect: () => events.push(['disconnect']) })
  return {
    events, sources, state: 'suspended', currentTime: 7, destination: {},
    async resume() { this.state = 'running' }, async close() { this.state = 'closed' },
    createBufferSource: () => { const source = { ...node(), start: (...args) => events.push(['start', ...args]), stop: (...args) => events.push(['stop', ...args]) }; sources.push(source); return source },
    createGain: () => ({ ...node(), gain: parameter() }),
  }
}
test('recorded phases resume at the matching offset and stop at the phase boundary', async () => {
  const context = fakeContext()
  let loads = 0
  const audio = new BreathAudio(() => context, async () => { loads++; return recordings })
  assert.equal(audio.play('inhale'), false)
  await audio.unlock()
  await audio.unlock()
  assert.equal(loads, 1)
  assert.equal(audio.play('inhale', .5), true)
  assert.equal(context.sources.at(-1).buffer, recordings.inhale)
  assert.ok(context.events.some(event => event[0] === 'start' && event[1] === 7 && event[2] === 2))
  assert.ok(context.events.some(event => event[0] === 'stop' && event[1] === 9))
  context.events.length = 0
  assert.equal(audio.play('exhale', .25), true)
  assert.equal(context.sources.at(-1).buffer, recordings.exhale)
  assert.ok(context.events.some(event => event[0] === 'start' && event[2] === 1.5))
  assert.ok(context.events.some(event => event[0] === 'stop' && event[1] === 11.5))
  audio.stop()
  assert.equal(audio.nodes.length, 0)
  assert.equal(audio.play('countdown'), false)
  assert.equal(audio.play('inhale', 1), false)
  audio.close()
  assert.equal(context.state, 'closed')
})
test('decode failure is retryable and leaves text/visual fallback available', async () => {
  const context = fakeContext()
  let fail = true
  const audio = new BreathAudio(() => context, async () => { if (fail) throw new Error('Decode failed'); return recordings })
  await assert.rejects(audio.unlock(), /Decode failed/)
  assert.equal(audio.play('inhale'), false)
  fail = false
  await audio.unlock()
  assert.equal(audio.play('inhale'), true)
  audio.close()
})
test('closing during decoding prevents a late completion from starting sound', async () => {
  const context = fakeContext()
  let resolve
  const audio = new BreathAudio(() => context, () => new Promise(done => { resolve = done }))
  const pending = audio.unlock()
  audio.close()
  resolve(recordings)
  await assert.rejects(pending, /unavailable/)
  assert.equal(audio.play('inhale'), false)
  assert.equal(context.sources.length, 0)
})
test('failed context unlock or invalid recording durations reject safely', async () => {
  const audio = new BreathAudio(() => { throw new Error('Unavailable') })
  await assert.rejects(audio.unlock(), /Unavailable/)
  audio.stop()
  const bad = new BreathAudio(fakeContext, async () => ({ inhale: { duration: 2 }, exhale: { duration: 6 } }))
  await assert.rejects(bad.unlock(), /recording is unavailable/)
  assert.equal(bad.play('inhale'), false)
  bad.close()
})

test('a missing inhale recording stays silent instead of substituting an exhale', async () => {
  const context = fakeContext()
  const audio = new BreathAudio(() => context, async () => ({ exhale: recordings.exhale }))
  await audio.unlock()
  assert.equal(audio.play('inhale'), false)
  assert.equal(context.sources.length, 0)
  assert.equal(audio.play('exhale'), true)
  assert.equal(context.sources.at(-1).buffer, recordings.exhale)
  audio.close()
})
