import { onBeforeUnmount, onMounted, watch } from 'vue'
import harp from './harp-softened.wav?inline'
import { CompletionSound } from './player.js'

export function useCompletionSound(enabled, interrupted, cue = harp) {
  const sound = new CompletionSound(async context => {
    // Bundle the approved edit for offline use; no request controls the cue.
    const bytes = Uint8Array.from(atob(cue.slice(cue.indexOf(',') + 1)), c => c.charCodeAt(0))
    return context.decodeAudioData(bytes.buffer)
  }, () => enabled.value && !interrupted() && !document.hidden)
  const visibility = () => { if (document.hidden) sound.stop() }
  watch([enabled, interrupted], () => { if (!enabled.value || interrupted()) sound.stop() }, { flush: 'sync' })
  onMounted(() => document.addEventListener('visibilitychange', visibility))
  onBeforeUnmount(() => { sound.close(); document.removeEventListener('visibilitychange', visibility) })
  return sound
}
