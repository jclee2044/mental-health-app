import { test } from 'node:test'
import assert from 'node:assert/strict'
import { BreathAudio } from '../audio.js'

function fakeContext() {
  const events = []
  const parameter = () => ({ value: 0, setValueAtTime: (...args) => events.push(['set', ...args]), linearRampToValueAtTime: (...args) => events.push(['ramp', ...args]) })
  const node = () => ({ connect() {}, disconnect: () => events.push(['disconnect']) })
  return {
    events, state: 'suspended', sampleRate: 100, currentTime: 7, destination: {},
    async resume() { this.state = 'running' }, async close() { this.state = 'closed' },
    createBuffer: (_channels, length) => ({ getChannelData: () => new Float32Array(length) }),
    createBufferSource: () => ({ ...node(), start: (...args) => events.push(['start', ...args]), stop: (...args) => events.push(['stop', ...args]) }),
    createBiquadFilter: () => ({ ...node(), Q: parameter(), frequency: parameter() }),
    createGain: () => ({ ...node(), gain: parameter() }),
  }
}
test('audio unlocks on demand and schedules only remaining phase after resume', async () => {
  const context = fakeContext(), audio = new BreathAudio(() => context)
  assert.equal(audio.play('inhale'), false)
  await audio.unlock()
  assert.equal(audio.play('inhale', .5), true)
  assert.ok(context.events.some(event => event[0] === 'start' && event[1] === 7 && event[2] === 2))
  assert.ok(context.events.some(event => event[0] === 'stop' && event[1] === 9))
  audio.stop()
  assert.equal(audio.nodes.length, 0)
  assert.equal(audio.play('countdown'), false)
  audio.close()
  assert.equal(context.state, 'closed')
})
test('failed audio context unlock leaves a usable error for the UI fallback', async () => {
  const audio = new BreathAudio(() => { throw new Error('Unavailable') })
  await assert.rejects(audio.unlock(), /Unavailable/)
  audio.stop()
})
