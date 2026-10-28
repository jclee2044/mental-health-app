import { test } from 'node:test'
import assert from 'node:assert/strict'
import { VoiceSession } from '../voice.js'
import { deferred, flush, harness, streamOf, Track, Target } from './fakes.js'
import { bindVoiceLifecycle, interruptVoice } from '../lifecycle.js'

async function connect(h) {
  const pending = h.voice.start(); await flush(); h.peer.completeIce(); await pending
}
async function ready(h) { await connect(h); h.event({ type: 'session.started', session: { id: 'live_fake' } }) }
function setup() { const h = harness(); h.voice = new VoiceSession(h.options); return h }

test('construction is inert; explicit start orders channel, offer, complete ICE, POST, answer and started', async () => {
  const h = setup()
  assert.equal(h.calls.config.length + h.calls.media.length + h.calls.sessions.length, 0)
  const pending = h.voice.start(); await flush()
  assert.equal(h.voice.state.status, 'connecting')
  assert.deepEqual(h.calls.media, [{ audio: true, video: false }])
  assert.equal(h.calls.sessions.length, 0)
  assert.ok(h.order.indexOf('channel:oai-events') < h.order.indexOf('offer'))
  assert.equal(h.track.enabled, false)
  h.peer.completeIce(); await pending
  assert.equal(h.calls.sessions[0].sdp, 'v=0\r\na=fully-gathered-ice\r\n')
  assert.deepEqual(h.peer.remoteDescription, { type: 'answer', sdp: 'v=0\r\na=fake-answer\r\n' })
  assert.equal(h.voice.state.status, 'connecting')
  h.peer.connectionState = 'connected'; h.peer.emit('connectionstatechange'); h.channel.emit('open')
  assert.equal(h.voice.state.status, 'connecting')
  h.event({ type: 'session.started', session: { id: 'live_fake' } })
  assert.equal(h.voice.state.status, 'active'); assert.equal(h.track.enabled, true)
  assert.deepEqual(h.channel.sent, []) // Never sends session.start or browser configuration.
  h.voice.dispose()
})

test('permission denial and missing configuration leave no transport or microphone alive', async () => {
  const h = setup()
  h.environment.getUserMedia = async () => { throw Object.assign(new Error('private device detail'), { name: 'NotAllowedError' }) }
  await h.voice.start()
  assert.equal(h.voice.state.status, 'error'); assert.match(h.voice.state.message, /denied/)
  assert.doesNotMatch(h.voice.state.message, /private/); assert.equal(h.calls.sessions.length, 0)
  h.api.getVoiceConfig = async () => ({ status: 'unconfigured', duration_seconds: 300 })
  await h.voice.start()
  assert.match(h.voice.state.message, /not configured/); assert.equal(h.order.length, 0)
})

test('cancel during an ignored permission prompt stops every late track without restarting', async () => {
  const h = setup(), permission = deferred(), extra = new Track()
  h.environment.getUserMedia = () => permission.promise
  const pending = h.voice.start(); await flush()
  assert.equal(h.voice.state.status, 'permission')
  h.voice.stop(); assert.equal(h.voice.state.status, 'closed')
  permission.resolve(streamOf(h.track, extra)); await pending
  assert.equal(h.track.stops, 1); assert.equal(extra.stops, 1)
  assert.equal(h.calls.sessions.length, 0); assert.equal(h.voice.state.status, 'closed')
})

test('ICE timeout aborts the wait and late ICE cannot send a POST', async () => {
  const h = setup(), pending = h.voice.start(); await flush()
  h.advance(25000); await pending
  assert.equal(h.voice.state.status, 'error'); assert.equal(h.track.stops, 1)
  h.peer.completeIce(); await flush()
  assert.equal(h.calls.sessions.length, 0); assert.equal(h.peer.count() + h.channel.count() + h.track.count(), 0)
  assert.equal(h.timers.size, 0)
})

test('late API success after End closes the created provider session without applying the answer', async () => {
  const h = setup(), answer = deferred()
  h.api.createVoiceSession = () => answer.promise
  const pending = h.voice.start(); await flush(); h.peer.completeIce(); await flush()
  h.voice.stop(); assert.match(h.voice.state.message, /unconfirmed/)
  answer.resolve({ session_id: 'live_late', sdp: 'v=0\r\n', duration_seconds: 300 }); await pending
  h.event({ type: 'session.started', session: { id: 'live_late' } })
  assert.equal(h.peer.remoteDescription, null); assert.equal(h.voice.state.status, 'closed')
  assert.deepEqual(h.calls.ends, ['live_late'])
})

test('started received during setRemoteDescription waits for the answer to finish applying', async () => {
  const h = setup(), applied = deferred(); h.peer.remoteWait = applied.promise
  const pending = h.voice.start(); await flush(); h.peer.completeIce(); await flush()
  h.event({ type: 'session.started', session: { id: 'live_fake' } })
  assert.equal(h.voice.state.status, 'connecting')
  applied.resolve(); await pending; assert.equal(h.voice.state.status, 'active')
  h.voice.dispose()
})

test('resolved configuration larger than 16 KB does not discard startup or finalization', async () => {
  const h = setup(); await connect(h)
  // Live lifecycle events include resolved configuration, including both prompts.
  const session = { id: 'live_fake', instructions: 'x'.repeat(6000), delegation: { responses: { instructions: 'y'.repeat(11000) } } }
  const started = { type: 'session.started', session }
  assert.ok(JSON.stringify(started).length > 16000)
  h.event(started)
  assert.equal(h.voice.state.status, 'active'); assert.equal(h.track.enabled, true)
  h.voice.stop(); h.event({ type: 'session.closed', session })
  assert.equal(h.voice.state.status, 'closed'); assert.doesNotMatch(h.voice.state.message, /unconfirmed/)
  await flush(); assert.deepEqual(h.calls.ends, [])
})

test('oversized lifecycle events and captions remain bounded without exposing configuration', async () => {
  const h = setup(); await connect(h)
  h.event({ type: 'session.started', session: { id: 'live_fake', instructions: 'x'.repeat(128 * 1024) } })
  assert.equal(h.voice.state.status, 'connecting'); assert.equal(h.track.enabled, false)
  h.event({ type: 'session.started', session: { id: 'live_fake' } })
  h.event({ type: 'session.input_transcript.delta', event_id: 'large', delta: 'a', start_ms: 0, end_ms: 1, extra: 'x'.repeat(16000) })
  assert.equal(h.captions.length, 0)
  assert.ok(h.changes.every(state => !('session' in state) && !('instructions' in state)))
  h.voice.dispose()
})

test('automatic playback rejection exposes recovery and the gesture retries play synchronously', async () => {
  const h = setup(); await ready(h)
  const remote = new Track(); h.audio.blocked = true
  h.peer.emit('track', { track: remote, streams: [streamOf(remote)] }); await flush()
  assert.equal(h.voice.state.playbackBlocked, true); assert.equal(h.voice.state.status, 'active')
  h.audio.blocked = false
  const enabled = h.voice.enableAudio()
  assert.equal(h.audio.plays, 2)
  await enabled; assert.equal(h.voice.state.playbackBlocked, false)
  h.voice.dispose(); assert.equal(remote.stops, 1); assert.equal(h.audio.srcObject, null)
})

test('Mute/Unmute only toggle tracks: playback, provider session and duration timer continue', async () => {
  const h = setup(); await ready(h)
  const remote = new Track(), stream = streamOf(remote)
  h.peer.emit('track', { track: remote, streams: [stream] }); await flush()
  const timers = [...h.timers.keys()], pauses = h.audio.pauses
  h.voice.toggleMute()
  assert.equal(h.voice.state.status, 'muted'); assert.equal(h.track.enabled, false)
  assert.equal(h.track.readyState, 'live'); assert.equal(h.track.stops, 0)
  assert.equal(h.audio.pauses, pauses); assert.equal(h.audio.srcObject, stream)
  assert.equal(h.channel.readyState, 'open'); assert.deepEqual(h.channel.sent, []); assert.deepEqual(h.calls.ends, [])
  assert.deepEqual([...h.timers.keys()], timers); assert.match(h.voice.state.message, /billing continue/)
  h.voice.toggleMute()
  assert.equal(h.voice.state.status, 'active'); assert.equal(h.track.enabled, true)
  assert.deepEqual(h.channel.sent, [])
  h.voice.dispose()
})

test('muting needs no network acknowledgment and never ends voice after five seconds', async () => {
  const h = setup(); await ready(h); h.voice.toggleMute(); h.advance(5000)
  assert.equal(h.voice.state.status, 'muted'); assert.equal(h.track.stops, 0)
  h.voice.dispose()
})

test('closing releases capture/playback immediately and waits boundedly for session.closed', async () => {
  const h = setup(); await ready(h); h.voice.stop()
  assert.equal(h.voice.state.status, 'closing'); assert.equal(h.track.stops, 1)
  assert.equal(h.audio.srcObject, null); assert.equal(h.channel.readyState, 'open')
  assert.deepEqual(h.channel.sent.at(-1), { type: 'session.close' })
  h.event({ type: 'session.closed', session: { id: 'live_fake' } })
  assert.equal(h.voice.state.status, 'closed'); assert.doesNotMatch(h.voice.state.message, /unconfirmed/)
  assert.equal(h.peer.count() + h.channel.count() + h.track.count(), 0); assert.equal(h.timers.size, 0)
  h.voice.dispose(); await flush(); assert.equal(h.track.stops, 1); assert.deepEqual(h.calls.ends, [])
})

test('close timeout releases remaining transport and reports incomplete finalization', async () => {
  const h = setup(); await ready(h); h.voice.stop(); h.advance(2000)
  assert.equal(h.voice.state.status, 'closed'); assert.match(h.voice.state.message, /unconfirmed/)
  assert.equal(h.channel.readyState, 'closed'); assert.equal(h.timers.size, 0)
})

test('duration ends voice only; there is no chat navigation callback', async () => {
  const h = setup(); await ready(h); h.advance(300000)
  assert.equal(h.voice.state.status, 'closing'); assert.equal(h.track.stops, 1)
  h.advance(2000); await flush()
  assert.equal(h.voice.state.status, 'closed'); assert.match(h.voice.state.message, /keep typing/)
  assert.equal(h.peer.count() + h.channel.count() + h.track.count(), 0); assert.equal(h.timers.size, 0)
  assert.equal(h.audio.srcObject, null); assert.equal(h.peer.connectionState, 'closed')
  assert.deepEqual(h.calls.ends, ['live_fake'])
})

test('bad session readiness, provider errors, and malformed messages never display raw details', async () => {
  for (const event of [{ type: 'session.started', session: { id: 'wrong' } }, { type: 'error', error: { message: 'private-provider-secret' } }]) {
    const h = setup(); await connect(h); h.event(event)
    assert.equal(h.voice.state.status, 'error'); assert.doesNotMatch(h.voice.state.message, /private-provider-secret/)
    assert.equal(h.track.stops, 1)
  }
  const h = setup(); await ready(h)
  h.channel.emit('message', { data: '{bad' }); h.event(null); h.event({ type: 'session.update' })
  assert.equal(h.voice.state.status, 'active'); h.voice.dispose()
})

test('captions validate timing and deduplicate event IDs without requiring completed-turn events', async () => {
  const h = setup(); await ready(h)
  const event = { type: 'session.input_transcript.delta', event_id: 'one', delta: ' hello', start_ms: 0, end_ms: 300 }
  h.event(event); h.event(event); h.event({ ...event, event_id: 'bad', end_ms: -1 })
  assert.equal(h.captions.length, 1); assert.equal(h.captions[0].role, 'user'); assert.equal(h.captions[0].text, ' hello')
  h.voice.dispose()
})

test('disposal and connection failure cannot restart audio from late events', async () => {
  const h = setup(); await ready(h)
  h.peer.connectionState = 'failed'; h.peer.emit('connectionstatechange')
  assert.equal(h.voice.state.status, 'error'); assert.equal(h.track.stops, 1)
  const states = h.changes.length; h.voice.dispose()
  h.event({ type: 'session.started', session: { id: 'live_fake' } }); await h.voice.start()
  assert.equal(h.changes.length, states); assert.equal(h.calls.sessions.length, 1)
})

test('duplicate Start and repeated End create one session and send one close', async () => {
  const h = setup(), first = h.voice.start()
  await Promise.all([h.voice.start(), h.voice.start()]); await flush()
  assert.equal(h.calls.config.length, 1); assert.equal(h.calls.media.length, 1)
  h.peer.completeIce(); await first
  h.event({ type: 'session.started', session: { id: 'live_fake' } })
  await h.voice.start(); assert.equal(h.calls.sessions.length, 1)
  h.voice.stop(); const timers = h.timers.size
  h.voice.stop(); h.voice.stop(); await h.voice.start()
  assert.equal(h.timers.size, timers); assert.equal(h.track.stops, 1)
  assert.deepEqual(h.channel.sent, [{ type: 'session.close' }])
  h.advance(2000); h.voice.stop(); h.voice.dispose(); h.voice.dispose(); await flush()
  assert.deepEqual(h.calls.ends, ['live_fake']); assert.equal(h.calls.sessions.length, 1)
  assert.equal(h.peer.connectionState, 'closed'); assert.equal(h.timers.size, 0)
})

for (const path of ['unmount', 'hashchange', 'pagehide', 'beforeunload', 'hidden', 'Emergency']) {
  test(`${path} immediately releases every voice resource and never resumes`, async () => {
    const h = setup(), document = new Target(), window = new Target()
    const unbind = bindVoiceLifecycle(h.voice, document, window)
    await ready(h)
    const remote = new Track(); h.peer.emit('track', { track: remote, streams: [streamOf(remote)] })
    await flush()
    if (path === 'unmount') unbind()
    else if (path === 'Emergency') interruptVoice(h.voice, true)
    else if (path === 'hidden') { document.hidden = true; document.emit('visibilitychange') }
    else window.emit(path)
    assert.equal(h.track.stops, 1); assert.equal(remote.stops, 1)
    assert.equal(h.audio.srcObject, null); assert.equal(h.channel.readyState, 'closed')
    assert.equal(h.peer.connectionState, 'closed'); assert.equal(h.timers.size, 0)
    assert.equal(h.peer.count() + h.track.count() + h.channel.count(), 0)
    assert.deepEqual(h.channel.sent, [{ type: 'session.close' }])
    const state = h.voice.state.status, changes = h.changes.length
    h.event({ type: 'session.started', session: { id: 'live_fake' } })
    document.hidden = false; document.emit('visibilitychange'); interruptVoice(h.voice, false)
    await flush()
    assert.equal(h.voice.state.status, state); assert.equal(h.changes.length, changes)
    assert.deepEqual(h.calls.ends, ['live_fake'])
    unbind(); unbind(); assert.equal(document.count() + window.count(), 0)
  })
}

test('a late answer after unmount is closed once without restoring UI or audio', async () => {
  const h = setup(), answer = deferred()
  h.api.createVoiceSession = () => answer.promise
  const pending = h.voice.start(); await flush(); h.peer.completeIce(); await flush()
  h.voice.dispose(); const changes = h.changes.length
  answer.resolve({ session_id: 'late_unmounted', sdp: 'v=0\r\n', duration_seconds: 300 }); await pending
  assert.deepEqual(h.calls.ends, ['late_unmounted']); assert.equal(h.changes.length, changes)
  assert.equal(h.peer.remoteDescription, null); assert.equal(h.audio.srcObject, null)
})

test('old late answer closes only its session while a fresh conversation stays active', async () => {
  const h = setup(), answer = deferred(), next = harness()
  h.api.createVoiceSession = () => answer.promise
  const old = h.voice.start(); await flush(); h.peer.completeIce(); await flush(); h.voice.stop()
  h.voice.env = next.environment
  h.api.createVoiceSession = async () => ({ session_id: 'fresh_session', sdp: 'v=0\r\n', duration_seconds: 300 })
  const fresh = h.voice.start(); await flush(); next.peer.completeIce(); await fresh
  next.event({ type: 'session.started', session: { id: 'fresh_session' } })
  const changes = h.changes.length, timers = next.timers.size
  answer.resolve({ session_id: 'old_session', sdp: 'v=0\r\n', duration_seconds: 300 }); await old
  assert.deepEqual(h.calls.ends, ['old_session']); assert.equal(h.voice.state.status, 'active')
  assert.equal(h.changes.length, changes); assert.equal(next.track.enabled, true)
  assert.equal(next.peer.connectionState, 'new'); assert.equal(next.timers.size, timers)
  assert.equal(h.peer.remoteDescription, null); h.voice.dispose()
})

test('failed fallback close is contained, never retried and cannot change closed UI', async () => {
  const h = setup(); await ready(h)
  let attempts = 0
  h.api.endVoiceSession = async () => { attempts++; throw new Error('secret') }
  h.voice.stop(); h.advance(2000); const changes = h.changes.length
  await flush(); h.voice.stop(); h.voice.dispose(); await flush()
  assert.equal(attempts, 1); assert.equal(h.changes.length, changes)
  assert.match(h.voice.state.message, /unconfirmed/); assert.doesNotMatch(h.voice.state.message, /secret/)
})
