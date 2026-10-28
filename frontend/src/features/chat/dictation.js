// Bounded in-memory recording. Only the feature API sends it to the server.
export const MAX_RECORDING_BYTES = 2 * 1024 * 1024
export function dictationEnvironment() {
  return {
    getUserMedia: () => navigator.mediaDevices.getUserMedia({ audio: true, video: false }),
    createRecorder(stream) {
      const Recorder = globalThis.MediaRecorder
      const mime = ['audio/webm;codecs=opus', 'audio/mp4'].find(type => Recorder?.isTypeSupported(type))
      if (!mime) throw new Error('Unsupported recording')
      return new Recorder(stream, { mimeType: mime, audioBitsPerSecond: 64000 })
    },
    async encode(blob) {
      const bytes = new Uint8Array(await blob.arrayBuffer())
      let binary = ''
      for (let i = 0; i < bytes.length; i += 8192) binary += String.fromCharCode(...bytes.subarray(i, i + 8192))
      return btoa(binary)
    },
    setTimeout: (callback, delay) => setTimeout(callback, delay),
    clearTimeout: timer => clearTimeout(timer),
  }
}
const stopTracks = stream => stream?.getTracks().forEach(track => { try { track.stop() } catch { /* Already released. */ } })

export class Dictation {
  constructor({ appendText, transcribe, onChange = () => {}, environment = dictationEnvironment() }) {
    this.appendText = appendText; this.transcribe = transcribe; this.onChange = onChange; this.env = environment
    this.run = null; this.disposed = false
    this.state = { status: 'idle', message: '' }
  }
  publish(status, message) {
    this.state = { status, message }
    if (!this.disposed) this.onChange({ ...this.state })
  }
  current(run) { return !this.disposed && this.run === run }
  async start() {
    if (this.disposed || this.run) return
    const run = { controller: new AbortController(), chunks: [], size: 0 }
    this.run = run
    this.publish('starting', 'Allow microphone access, or cancel dictation.')
    run.timer = this.env.setTimeout(() => {
      if (!this.current(run)) return
      if (this.state.status === 'recording') this.finish()
      else this.fail(run, 'Dictation setup timed out. You can still type.')
    }, 30000)
    try {
      const stream = await this.env.getUserMedia()
      if (!this.current(run)) { stopTracks(stream); return }
      run.stream = stream
      run.recorder = this.env.createRecorder(stream)
      run.mime = run.recorder.mimeType.split(';', 1)[0]
      if (!['audio/webm', 'audio/mp4'].includes(run.mime)) throw new Error('Unsupported recording')
      run.recorder.ondataavailable = event => {
        if (!this.current(run) || !event.data?.size) return
        run.size += event.data.size
        if (run.size > MAX_RECORDING_BYTES) { this.fail(run, 'That recording is too large. Try a shorter message.'); return }
        run.chunks.push(event.data)
      }
      run.recorder.onerror = () => this.fail(run, 'Recording failed. Your existing draft is unchanged.')
      run.recorder.onstop = () => {
        stopTracks(run.stream)
        if (this.current(run)) this.upload(run)
      }
      run.recorder.start(250)
      this.publish('recording', 'Recording… Select the microphone again to transcribe. Up to 30 seconds.')
      this.env.clearTimeout(run.timer)
      run.timer = this.env.setTimeout(() => { if (this.current(run)) this.finish() }, 30000)
    } catch (error) {
      this.fail(run, error?.name === 'NotAllowedError' ? 'Microphone permission was denied. You can still type.' : 'Audio recording isn’t available. Check your microphone or keep typing.')
    }
  }
  finish() {
    const run = this.run
    if (!run || !this.current(run) || this.state.status !== 'recording') return
    this.env.clearTimeout(run.timer)
    this.publish('transcribing', 'Transcribing with OpenAI… You can cancel or keep editing your draft.')
    run.timer = this.env.setTimeout(() => this.fail(run, 'Transcription timed out. Your existing draft is unchanged.'), 30000)
    try { run.recorder.stop() } catch { this.fail(run, 'Recording could not be completed. You can still type.') }
    finally { stopTracks(run.stream) }
  }
  async upload(run) {
    if (!this.current(run)) return
    // Unexpected device stops are terminal; only explicit finish/timer uploads.
    if (this.state.status !== 'transcribing') { this.fail(run, 'Recording ended unexpectedly. Please try again.'); return }
    try {
      if (!run.size) throw new Error('Empty recording')
      const blob = new Blob(run.chunks, { type: run.mime })
      run.chunks = []
      const audio = await this.env.encode(blob)
      if (!this.current(run)) return
      const result = await this.transcribe(audio, run.mime, { signal: run.controller.signal })
      if (!this.current(run)) return
      const text = result?.text
      if (typeof text !== 'string' || !text.trim() || text.length > 4000 || new TextEncoder().encode(text).length > 8000) throw new Error('Invalid transcript')
      if (this.appendText(text.trim()) === false) { this.fail(run, 'Your draft is full. Shorten it before dictating more.'); return }
      this.stop('Added to your draft. Review your words before sending.')
    } catch { this.fail(run, 'Transcription couldn’t be completed. Your existing draft is unchanged; you can try again or type.') }
  }
  fail(run, message) {
    if (!this.current(run)) return
    this.stop(); this.publish('error', message)
  }
  stop(message = '') {
    const run = this.run
    this.run = null
    if (run) {
      run.controller.abort(); this.env.clearTimeout(run.timer)
      if (run.recorder) {
        run.recorder.ondataavailable = run.recorder.onerror = run.recorder.onstop = null
        try { if (run.recorder.state !== 'inactive') run.recorder.stop() } catch { /* Already stopped. */ }
      }
      stopTracks(run.stream); run.chunks = []
    }
    this.publish('idle', message)
  }
  dispose() { this.stop(); this.disposed = true }
}
