import { test } from 'node:test'
import assert from 'node:assert/strict'
import { CompletionSound } from '../src/components/completion-sound/player.js'

function fixture(load = async () => ({ duration: 4.1012 })) {
  let allowed = true
  const sources = []
  const context = {
    state: 'suspended', destination: {},
    async resume() { this.state = 'running' }, async close() { this.state = 'closed' },
    createBufferSource() {
      const source = { starts: 0, stops: 0, connect() {}, disconnect() {}, start() { this.starts++ }, stop() { this.stops++ } }
      sources.push(source)
      return source
    },
  }
  return { sound: new CompletionSound(load, () => allowed, () => context), context, sources,
    disallow: () => { allowed = false } }
}

test('arming is silent; completion plays once, with the approved buffer', async () => {
  const f = fixture()
  const ticket = f.sound.arm()
  assert.equal(f.sources.length, 0)
  assert.equal(f.context.state, 'running')
  assert.equal(await f.sound.complete(ticket), true)
  assert.equal(f.sources[0].buffer.duration, 4.1012)
  assert.equal(await f.sound.complete(ticket), false)
  f.sound.close()
  assert.equal(f.sources[0].stops, 1)
})

test('mute/interruption blocks pending playback even after decoding', async () => {
  let resolve
  const f = fixture(() => new Promise(done => { resolve = done }))
  const ticket = f.sound.arm()
  const pending = f.sound.complete(ticket)
  f.sound.stop()
  resolve({ duration: 4.1012 })
  assert.equal(await pending, false)
  assert.equal(f.sources.length, 0)
  f.sound.close()
})

test('hidden or interrupted actions remain silent; closed cues cannot restart', async () => {
  const f = fixture()
  const ticket = f.sound.arm()
  f.disallow()
  assert.equal(await f.sound.complete(ticket), false)
  f.sound.close()
  assert.equal(await f.sound.complete(f.sound.arm()), false)
  assert.equal(f.sources.length, 0)
})

test('decode/autoplay failure does not reject completion or queue a replay', async () => {
  const f = fixture(async () => { throw new Error('Unsupported audio') })
  assert.equal(await f.sound.complete(f.sound.arm()), false)
  f.sound.close()
  const unavailable = new CompletionSound(() => {}, () => true, () => { throw new Error('No AudioContext') })
  assert.equal(await unavailable.complete(unavailable.arm()), false)
  unavailable.close()
})
