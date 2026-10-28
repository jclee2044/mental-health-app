export const flush = async () => { for (let i = 0; i < 12; i++) await Promise.resolve() }
export function deferred() { let resolve, reject; const promise = new Promise((yes, no) => { resolve = yes; reject = no }); return { promise, resolve, reject } }

export class Target extends EventTarget {
  listeners = new Map()
  addEventListener(type, fn, options) { super.addEventListener(type, fn, options); if (!this.listeners.has(type)) this.listeners.set(type, new Set()); this.listeners.get(type).add(fn) }
  removeEventListener(type, fn, options) { super.removeEventListener(type, fn, options); this.listeners.get(type)?.delete(fn) }
  emit(type, fields = {}) { this.dispatchEvent(Object.assign(new Event(type), fields)) }
  count() { return [...this.listeners.values()].reduce((sum, set) => sum + set.size, 0) }
}
export class Track extends Target {
  enabled = true; stops = 0; readyState = 'live'
  stop() { this.stops++; this.readyState = 'ended' }
}
export const streamOf = (...tracks) => ({ getTracks: () => tracks, getAudioTracks: () => tracks })

export function harness() {
  const order = [], changes = [], captions = [], timers = new Map()
  let now = 0, timerId = 0
  const track = new Track(), channel = new Target(), peer = new Target()
  Object.assign(channel, { readyState: 'open', sent: [], send(raw) { this.sent.push(JSON.parse(raw)) }, close() { this.readyState = 'closed'; this.emit('close') } })
  Object.assign(peer, {
    iceGatheringState: 'gathering', connectionState: 'new', localDescription: null, remoteDescription: null,
    addTrack: () => { order.push('track') },
    createDataChannel(label) { order.push(`channel:${label}`); return channel },
    async createOffer() { order.push('offer'); return { type: 'offer', sdp: 'v=0\r\na=incomplete\r\n' } },
    async setLocalDescription(value) { order.push('local'); this.localDescription = value },
    async setRemoteDescription(value) { order.push('answer'); this.remoteDescription = value; if (this.remoteWait) await this.remoteWait },
    close() { this.connectionState = 'closed'; this.emit('connectionstatechange') },
    completeIce() { this.iceGatheringState = 'complete'; this.localDescription = { type: 'offer', sdp: 'v=0\r\na=fully-gathered-ice\r\n' }; this.emit('icegatheringstatechange') },
  })
  const audio = { srcObject: null, autoplay: false, plays: 0, pauses: 0, blocked: false, setAttribute() {}, play() { this.plays++; return this.blocked ? Promise.reject(new Error('NotAllowedError')) : Promise.resolve() }, pause() { this.pauses++ } }
  const calls = { config: [], sessions: [], media: [], text: [], ends: [], saves: [], voiceSaves: [] }
  const api = {
    async getVoiceConfig(options) { calls.config.push(options); return { status: 'configured', duration_seconds: 300 } },
    async createVoiceSession(sdp, history, options) { calls.sessions.push({ sdp, history, options }); order.push('post'); return { session_id: 'live_fake', sdp: 'v=0\r\na=fake-answer\r\n', duration_seconds: 300 } },
    async endVoiceSession(id) { calls.ends.push(id); return null },
    async sendTextMessage(message, history, options) { calls.text.push({ message, history, options }); return { reply: 'A fictional reply.' } },
    async saveChatTurn(conversationId, turnId, body) { calls.saves.push({ conversationId, turnId, body }); return { conversation_id: conversationId, turn_id: turnId, saved: true } },
    async saveVoiceTurn(conversationId, turnId, body) { calls.voiceSaves.push({ conversationId, turnId, body }); return { conversation_id: conversationId, turn_id: turnId, saved: true } },
  }
  const environment = {
    async getUserMedia(constraints) { calls.media.push(constraints); return streamOf(track) },
    createPeer: () => peer, createStream: tracks => streamOf(...tracks),
    setTimeout(callback, delay) { const id = ++timerId; timers.set(id, { callback, at: now + delay }); return id },
    clearTimeout: id => timers.delete(id),
  }
  function advance(ms) {
    const end = now + ms
    for (;;) {
      const next = [...timers].filter(([, timer]) => timer.at <= end).sort((a, b) => a[1].at - b[1].at)[0]
      if (!next) break
      const [id, timer] = next; now = timer.at; timers.delete(id); timer.callback()
    }
    now = end
  }
  const h = { api, environment, order, track, channel, peer, audio, calls, changes, captions, timers, advance }
  h.options = { api, environment, getAudio: () => audio, onChange: state => changes.push(state), onTranscript: value => captions.push(value) }
  h.event = event => channel.emit('message', { data: JSON.stringify(event) })
  return h
}
