import inhale from './assets/inhale.m4a?inline'
import exhale from './assets/exhale.m4a?inline'

// Inline assets travel with the cached JS bundle; no request paces playback.
export async function decodeRecordings(context) {
  const decoded = await Promise.all(Object.entries({ inhale, exhale }).map(async ([phase, uri]) => {
    const bytes = Uint8Array.from(atob(uri.slice(uri.indexOf(',') + 1)), character => character.charCodeAt(0))
    return [phase, await context.decodeAudioData(bytes.buffer)]
  }))
  return Object.fromEntries(decoded)
}
