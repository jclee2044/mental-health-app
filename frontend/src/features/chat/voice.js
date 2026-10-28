// Native browser resources, independent of Vue and HTTP transport. All are injectable.
const busyStates = new Set(['permission', 'connecting', 'active', 'muted', 'closing'])
// Lifecycle snapshots include resolved prompts/history; captions stay smaller.
const MAX_LIFECYCLE_BYTES = 128 * 1024
const stopTracks = stream => stream?.getTracks().forEach(track => { try { track.stop() } catch { /* Device already gone. */ } })

export function browserEnvironment() {
  return {
    getUserMedia: constraints => navigator.mediaDevices.getUserMedia(constraints),
    createPeer: () => new RTCPeerConnection(),
    createStream: tracks => new MediaStream(tracks),
    setTimeout: (callback, delay) => setTimeout(callback, delay),
    clearTimeout: timer => clearTimeout(timer),
  }
}

export class VoiceSession {
  constructor({ api, getAudio, onChange = () => {}, onTranscript = () => {}, getHistory = () => [], environment = browserEnvironment() }) {
    this.api = api; this.getAudio = getAudio; this.onChange = onChange; this.onTranscript = onTranscript; this.getHistory = getHistory; this.env = environment
    this.run = null; this.sequence = 0; this.disposed = false
    this.state = { status: 'closed', message: 'Microphone off.', playbackBlocked: false, mutePending: false, microphoneMuted: true }
  }
  publish(changes) {
    this.state = { ...this.state, ...changes }
    if (!this.disposed) this.onChange({ ...this.state })
  }
  current(run) { return this.run === run && !this.disposed }
  live(run) { return this.current(run) && !run.ending }
  listen(run, target, name, listener) {
    target.addEventListener(name, listener)
    const remove = () => target.removeEventListener(name, listener)
    run.listeners.push(remove)
    return remove
  }
  timer(run, callback, delay) {
    const timer = this.env.setTimeout(() => { run.timers.delete(timer); if (this.current(run)) callback() }, delay)
    run.timers.add(timer)
    return timer
  }
  clearTimer(run, timer) { if (timer !== undefined) { this.env.clearTimeout(timer); run.timers.delete(timer) } }
  async start() {
    if (this.disposed || busyStates.has(this.state.status)) return
    const run = { id: ++this.sequence, controller: new AbortController(), timers: new Set(), listeners: [], remoteTracks: new Set(), seen: new Set(), ending: false }
    this.run = run
    this.publish({ status: 'permission', message: 'Preparing microphone permission…', playbackBlocked: false, mutePending: false, microphoneMuted: true })
    let stage = 'configuration'
    try {
      run.history = this.getHistory().map(message => ({ ...message }))
      const config = await this.api.getVoiceConfig({ signal: run.controller.signal })
      if (!this.live(run)) return
      if (config?.status !== 'configured') { this.fail(run, 'Voice is not configured on the local server. You can still type.'); return }
      if (!Number.isInteger(config.duration_seconds) || config.duration_seconds < 1 || config.duration_seconds > 3600) throw new Error('Invalid duration')
      run.duration = config.duration_seconds
      stage = 'permission'
      this.publish({ message: 'Allow microphone access in your browser, or cancel and type.' })
      const stream = await this.env.getUserMedia({ audio: true, video: false })
      if (!this.live(run)) { stopTracks(stream); return }
      run.stream = stream
      if (!stream.getAudioTracks().length) throw new Error('Missing audio track')
      stage = 'connection'
      this.publish({ status: 'connecting', message: 'Connecting voice…' })
      run.startupTimer = this.timer(run, () => this.fail(run, 'Voice setup timed out. Session finalization is unconfirmed. You can still type.'), 25000)
      run.audio = this.getAudio()
      if (!run.audio) throw new Error('No playback element')
      run.audio.autoplay = true
      run.audio.setAttribute('playsinline', '')
      run.peer = this.env.createPeer()
      for (const track of stream.getAudioTracks()) {
        track.enabled = false // Do not send microphone audio until session.started.
        run.peer.addTrack(track, stream)
        this.listen(run, track, 'ended', () => { if (this.live(run)) this.fail(run, 'Microphone access ended. You can still type.') })
      }
      this.listen(run, run.peer, 'track', event => this.remoteTrack(run, event))
      this.listen(run, run.peer, 'connectionstatechange', () => {
        if (this.live(run) && ['failed', 'disconnected', 'closed'].includes(run.peer.connectionState)) this.fail(run, 'Voice connection ended unexpectedly. You can still type.')
      })
      // The data channel and handlers MUST exist before generating the offer.
      run.channel = run.peer.createDataChannel('oai-events')
      this.listen(run, run.channel, 'message', event => this.message(run, event.data))
      this.listen(run, run.channel, 'error', () => { if (this.live(run)) this.fail(run, 'Voice events are unavailable. You can still type.') })
      this.listen(run, run.channel, 'close', () => {
        if (run.ending && this.current(run)) this.finish(run, false)
        else if (this.live(run)) this.fail(run, 'Voice connection closed. You can still type.')
      })
      const offer = await run.peer.createOffer()
      if (!this.live(run)) return
      await run.peer.setLocalDescription(offer)
      if (!this.live(run)) return
      await this.waitForIce(run)
      if (!this.live(run)) return
      const sdp = run.peer.localDescription?.sdp
      if (typeof sdp !== 'string' || !sdp || new TextEncoder().encode(sdp).length > 65536) throw new Error('Invalid offer')
      run.creationSent = true
      // Keep an already-sent creation request bounded but readable after End, so
      // its returned session ID can be closed rather than orphaned by an abort.
      const answer = await this.api.createVoiceSession(sdp, run.history)
      if (typeof answer?.session_id === 'string' && /^[A-Za-z0-9_-]{1,128}$/.test(answer.session_id)) run.sessionId = answer.session_id
      if (!this.live(run)) { await this.closeProvider(run); return }
      if (typeof answer?.session_id !== 'string' || !/^[A-Za-z0-9_-]{1,128}$/.test(answer.session_id) || typeof answer.sdp !== 'string' || !answer.sdp.startsWith('v=0') || new TextEncoder().encode(answer.sdp).length > 65536 || answer.duration_seconds !== run.duration) throw new Error('Invalid answer')
      run.sessionId = answer.session_id
      await run.peer.setRemoteDescription({ type: 'answer', sdp: answer.sdp })
      if (!this.live(run)) return
      run.answerApplied = true
      this.activate(run)
    } catch (error) {
      if (!this.live(run)) return
      const permission = error?.name === 'NotAllowedError' ? 'Microphone permission was denied. You can still type.' : 'Microphone is unavailable. You can still type.'
      this.fail(run, stage === 'permission' ? permission : stage === 'configuration' ? 'Voice configuration is unavailable. You can still type.' : 'Voice setup failed. Session finalization is unconfirmed. You can still type.')
    }
  }
  waitForIce(run) {
    return new Promise((resolve, reject) => {
      const signal = run.controller.signal
      const clean = () => { remove(); signal.removeEventListener('abort', aborted) }
      const check = () => { if (run.peer.iceGatheringState === 'complete') { clean(); resolve() } }
      const aborted = () => { clean(); reject(new Error('Cancelled')) }
      const remove = this.listen(run, run.peer, 'icegatheringstatechange', check)
      signal.addEventListener('abort', aborted, { once: true })
      if (signal.aborted) aborted()
      else check()
    })
  }
  activate(run) {
    if (!this.live(run) || !run.answerApplied || !run.started || run.ready) return
    run.ready = true
    this.clearTimer(run, run.startupTimer)
    run.stream.getAudioTracks().forEach(track => { track.enabled = true })
    this.publish({ status: 'active', message: 'Voice is active. You can interrupt or stop whenever you like.', microphoneMuted: false })
    this.timer(run, () => this.stop('The voice time limit was reached. You can keep typing.'), run.duration * 1000)
  }
  remoteTrack(run, event) {
    if (!this.live(run)) { event.track?.stop(); return }
    const stream = event.streams?.[0] || this.env.createStream([event.track])
    stream.getTracks().forEach(track => run.remoteTracks.add(track))
    run.audio.srcObject = stream
    this.enableAudio()
  }
  async enableAudio() {
    const run = this.run
    if (!run || !this.live(run) || !run.audio?.srcObject) return
    try {
      // This call happens synchronously inside the Enable button's user gesture.
      await run.audio.play()
      if (this.live(run)) this.publish({ playbackBlocked: false })
    } catch {
      if (this.live(run)) this.publish({ playbackBlocked: true })
    }
  }
  message(run, raw) {
    if (!this.current(run) || typeof raw !== 'string' || raw.length > MAX_LIFECYCLE_BYTES || new TextEncoder().encode(raw).length > MAX_LIFECYCLE_BYTES) return
    let event
    try { event = JSON.parse(raw) } catch { return }
    if (!event || typeof event !== 'object') return
    if (raw.length > 16000 && !['session.started', 'session.closed'].includes(event.type)) return
    if (event.type === 'session.closed') {
      if (event.session?.id && event.session.id !== run.sessionId) return
      this.finish(run, true); return
    }
    if (run.ending) return
    if (event.type === 'session.started') {
      if (!run.sessionId || event.session?.id !== run.sessionId) { this.fail(run, 'Voice readiness could not be confirmed. You can still type.'); return }
      run.started = true; this.activate(run)
    } else if (event.type === 'error') {
      this.fail(run, 'The voice service reported an error. You can still type.')
    } else if (run.ready && ['session.input_transcript.delta', 'session.output_transcript.delta'].includes(event.type)) {
      if (typeof event.event_id !== 'string' || run.seen.has(event.event_id) || typeof event.delta !== 'string' || event.delta.length > 4000 || !Number.isFinite(event.start_ms) || !Number.isFinite(event.end_ms) || event.start_ms < 0 || event.end_ms < event.start_ms) return
      run.seen.add(event.event_id)
      this.onTranscript({ session: run.id, id: event.event_id, role: event.type === 'session.input_transcript.delta' ? 'user' : 'assistant', text: event.delta, start: event.start_ms, end: event.end_ms })
    }
  }
  toggleMute() {
    const run = this.run
    if (!run || !this.live(run) || !run.ready) return
    const muted = this.state.status !== 'muted'
    run.stream.getAudioTracks().forEach(track => { track.enabled = !muted })
    this.publish({ status: muted ? 'muted' : 'active', microphoneMuted: muted, mutePending: false, message: muted ? 'Microphone muted. Assistant audio, the session, and billing continue. Use End to close voice.' : 'Voice is active.' })
  }
  stop(message = 'Voice stopped. You can still type.', immediate = false) {
    const run = this.run
    if (!run || !this.current(run) || run.ending) { if (immediate && run) this.finish(run, false); return }
    run.ending = true; run.closeMessage = message
    this.publish({ status: 'closing', message: 'Closing voice. Microphone off.', microphoneMuted: true, playbackBlocked: false, mutePending: false })
    this.releaseLocal(run)
    run.controller.abort()
    for (const timer of run.timers) this.env.clearTimeout(timer)
    run.timers.clear()
    if (run.sessionId && run.channel?.readyState === 'open') {
      try { run.channel.send(JSON.stringify({ type: 'session.close' })) } catch { this.finish(run, false); return }
      if (this.current(run) && !immediate) this.timer(run, () => this.finish(run, false), 2000)
      else if (this.current(run)) this.finish(run, false)
    } else this.finish(run, !run.creationSent)
  }
  releaseLocal(run) {
    stopTracks(run.stream); run.stream = null
    for (const track of run.remoteTracks) { try { track.stop() } catch { /* Already stopped. */ } }
    run.remoteTracks.clear()
    if (run.audio) { run.audio.pause(); run.audio.srcObject = null }
  }
  release(run) {
    this.run = null
    run.listeners.forEach(remove => remove())
    run.controller.abort()
    for (const timer of run.timers) this.env.clearTimeout(timer)
    run.timers.clear()
    this.releaseLocal(run)
    try { run.channel?.close() } catch { /* Transport already gone. */ }
    try { run.peer?.close() } catch { /* Transport already gone. */ }
  }
  finish(run, confirmed) {
    if (!this.current(run)) return
    if (!confirmed) this.closeProvider(run)
    this.release(run)
    this.publish({ status: 'closed', microphoneMuted: true, playbackBlocked: false, mutePending: false, message: `${run.closeMessage || 'Voice ended. You can still type.'}${confirmed ? '' : ' Session finalization is unconfirmed.'}` })
  }
  fail(run, message) {
    if (!this.live(run)) return
    run.ending = true
    if (run.sessionId && run.channel?.readyState === 'open') { try { run.channel.send(JSON.stringify({ type: 'session.close' })) } catch { /* Best effort. */ } }
    this.closeProvider(run)
    this.release(run)
    this.publish({ status: 'error', message, microphoneMuted: true, playbackBlocked: false, mutePending: false })
  }
  closeProvider(run) {
    if (!run.sessionId) return Promise.resolve(false)
    // One explicit cleanup attempt per session, including repeated End/unmount.
    run.closePromise ??= Promise.resolve().then(() => this.api.endVoiceSession(run.sessionId)).then(result => result === null).catch(() => false)
    return run.closePromise
  }
  dispose() { this.stop('Voice ended.', true); this.disposed = true }
}
