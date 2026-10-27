<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import AppIcon from '../../components/AppIcon.vue'
import { BreathingClock, PATTERN, phaseAt } from './clock.js'
import { localDate } from '../../dates.js'
import { BreathAudio } from './audio.js'
import { decodeRecordings } from './recordings.js'
import { createBreathingHold } from './hold.js'
const props = defineProps({ interrupted: Boolean, reducedMotion: Boolean })
const emit = defineEmits(['navigate', 'record', 'start'])
const audio = new BreathAudio(undefined, decodeRecordings)
const soundEnabled = ref(true)
const soundStatus = ref('Recorded inhale & exhale')
let audioKey = ''
const clock = new BreathingClock()
const state = ref('ready')
const cue = ref(phaseAt(0))
const elapsed = ref(0)
const pauseReason = ref('')
let instructionStart = performance.now()
const instructionSeconds = ref(null)
let frame, sessionId, startedAt, sessionDay, recorded = false, lastFrame = 0
function render(now) {
  // A long main-thread stall is an interruption, not permission to skip breaths.
  if (lastFrame && now - lastFrame > 1500 && clock.state === 'running') {
    clock.pause(lastFrame)
    // Keep the stall in instruction-to-finish time; only subsequent pause time is excluded.
    clock.pausedAt = now
    pauseReason.value = 'The rhythm was interrupted. Resume when you’re ready.'
  }
  cue.value = clock.tick(now); elapsed.value = clock.elapsed; state.value = clock.state
  lastFrame = now
  syncAudio()
  if (clock.state === 'completed') record()
  if (clock.state === 'running') frame = requestAnimationFrame(render)
}
function begin() {
  if (props.interrupted || document.hidden || !hold.active || clock.state === 'running') return
  if (recorded) instructionStart = performance.now()
  emit('start')
  if (soundEnabled.value) unlockSound()
  sessionId = crypto.randomUUID(); startedAt = new Date().toISOString(); sessionDay = localDate(); recorded = false
  instructionSeconds.value = null; clock.start(performance.now()); lastFrame = 0; state.value = 'running'
  render(performance.now())
}
function pause(reason = 'Continue whenever you’re ready.') {
  if (clock.state !== 'running') return
  clock.pause(performance.now()); cancelAnimationFrame(frame)
  audio.stop(); audioKey = ''
  cue.value = phaseAt(clock.elapsed); elapsed.value = clock.elapsed; state.value = clock.state; pauseReason.value = reason
  if (clock.state === 'completed') record()
}
function resume() {
  if (props.interrupted || document.hidden || !hold.active) return
  if (soundEnabled.value) unlockSound()
  clock.resume(performance.now()); lastFrame = 0; state.value = clock.state; render(performance.now())
}
function record() {
  if (!sessionId || recorded) return
  recorded = true
  const now = performance.now()
  instructionSeconds.value = Math.max(0, (now - instructionStart - clock.pausedMs) / 1000)
  emit('record', { id: sessionId, pattern: PATTERN.id, status: clock.state === 'completed' ? 'completed' : 'ended',
    started_at: startedAt, ended_at: new Date().toISOString(), local_date: sessionDay,
    sequence_seconds: clock.elapsed / 1000, active_seconds: Math.max(0, clock.elapsed - PATTERN.countdown) / 1000,
    pause_seconds: clock.pausedMs / 1000, instruction_seconds: instructionSeconds.value })
}
function end() { clock.end(performance.now()); cancelAnimationFrame(frame); audio.stop(); record(); emit('navigate','home') }
const hold = createBreathingHold({
  start: () => { if (clock.state === 'paused') resume(); else begin() },
  release: () => { if (['running', 'paused'].includes(clock.state)) end() },
})
function visibility() { if (document.hidden) hold.cancel() }
watch(() => props.interrupted, value => { if (value) hold.cancel() })
onMounted(() => {
  document.addEventListener('visibilitychange', visibility)
  window.addEventListener('blur', hold.cancel)
})
onBeforeUnmount(() => { cancelAnimationFrame(frame); audio.close(); clock.end(performance.now()); record(); document.removeEventListener('visibilitychange', visibility); window.removeEventListener('blur', hold.cancel) })
const heading = computed(() => state.value === 'ready' ? 'A gentler rhythm.' : state.value === 'paused' ? 'Take your time.' : state.value === 'completed' ? 'A moment, taken.' : cue.value.phase === 'countdown' ? 'Settle in.' : cue.value.phase === 'inhale' ? 'Breathe in.' : 'Breathe out.')
const remainingSeconds = computed(() => Math.max(0, Math.ceil((PATTERN.total - Math.max(PATTERN.countdown, elapsed.value)) / 1000)))
const circleScale = computed(() => {
  if (props.reducedMotion || state.value === 'ready' || state.value === 'completed' || cue.value.phase === 'countdown') return 1
  const progress = cue.value.progress
  return cue.value.phase === 'inhale' ? .78 + .6 * progress : 1.38 - .6 * progress
})
async function unlockSound() {
  try { await audio.unlock(); audioKey = ''; soundStatus.value = 'Recorded inhale & exhale'; syncAudio() }
  catch { soundStatus.value = 'Sound unavailable. Follow the words and circle.' }
}
function syncAudio() {
  if (!soundEnabled.value || clock.state !== 'running' || !['inhale','exhale'].includes(cue.value.phase)) { audio.stop(); audioKey = ''; return }
  const key = `${cue.value.cycle}-${cue.value.phase}`
  if (key === audioKey || !audio.context || audio.context.state !== 'running') return
  try { if (audio.play(cue.value.phase,cue.value.progress)) audioKey = key }
  catch { audio.stop(); soundStatus.value = 'Sound unavailable. Follow the words and circle.' }
}
function toggleSound() {
  soundEnabled.value = !soundEnabled.value
  if (soundEnabled.value) unlockSound()
  else { audio.stop(); audioKey = '' }
}
</script>
<template>
  <section class="breathing-page narrow-page page-enter">
    <h1 aria-live="polite">{{ heading }}</h1>
    <p id="breathing-hold-instructions" class="breathing-hold-instructions"><strong>{{ state === 'ready' ? 'Tap and hold the circle to start.' : state === 'completed' ? 'Finished. You can release the circle.' : state === 'paused' ? 'Keep holding while paused.' : 'Keep holding the circle.' }}</strong><span>{{ state === 'completed' ? 'Hold it again for another exercise.' : 'Release at any time to end the exercise.' }}</span></p>
    <p class="breathing-description">{{ state === 'ready' ? 'A 3-second countdown, then 6 cycles: breathe in for 4 seconds and out for 6. No breath holds.' : state === 'paused' ? pauseReason : state === 'completed' ? 'You’ve finished the breathing exercise.' : cue.phase === 'countdown' ? 'Starting in ' + cue.count + '… Keep holding.' : props.reducedMotion ? 'Let the words carry the pace.' : 'Follow the circle, gently.' }}</p>
    <div class="breathing-stage"><div class="breathing-guide-ring"></div><button type="button" class="breathing-circle" aria-label="Hold to begin or repeat breathing; release to end" aria-describedby="breathing-hold-instructions" @pointerdown="hold.pointerDown" @pointerup="hold.pointerUp" @pointercancel="hold.pointerUp" @lostpointercapture="hold.pointerUp" @keydown="hold.keyDown" @keyup="hold.keyUp" @blur="hold.blur" @contextmenu.prevent @click.prevent :style="{transform:`scale(${circleScale})`}" :data-phase="cue.phase" :data-scale="circleScale.toFixed(3)"><span v-if="state === 'ready'" class="breathing-circle-label"><AppIcon name="wind" /><strong>Tap &amp; hold</strong><span>to start</span></span><AppIcon v-else-if="state === 'completed'" name="check" /><AppIcon v-else-if="state === 'paused'" name="pause" /></button><div v-if="state === 'running'" class="breathing-count" aria-hidden="true">{{ cue.count }}</div></div>
    <p class="breathing-time" role="timer" aria-live="off">{{ state === 'ready' ? '60 seconds of breathing' : state === 'completed' ? 'Exercise complete' : `${remainingSeconds} seconds left` }}<span>{{ state === 'ready' ? 'After a separate 3-second countdown' : state === 'paused' ? 'Timer paused · Release to end' : state === 'completed' ? 'All 6 cycles finished' : cue.phase === 'countdown' ? 'Getting ready · Breathing timer starts after countdown' : 'Release to end' }}</span></p>
    <p class="breathing-progress" role="status">{{ state === 'ready' ? '6 cycles · 60 seconds of breathing' : state === 'completed' ? '6 of 6 cycles' : cue.phase === 'countdown' ? '3–2–1 countdown' : `Cycle ${cue.cycle} of 6 · ${Math.floor(Math.max(0,elapsed-3000)/1000)} / 60 seconds` }}</p>
    <div class="sound-control" :data-audio-phase="audioKey" :data-audio-state="audio.context?.state || 'idle'"><button class="text-button" :aria-pressed="soundEnabled" :aria-label="soundEnabled ? 'Mute breathing sounds' : 'Enable breathing sounds'" @click="toggleSound"><AppIcon :name="soundEnabled ? 'sound' : 'mute'" /> {{ soundEnabled ? 'Sound on' : 'Sound off' }}</button><span class="small muted" role="status">{{ soundEnabled ? soundStatus : 'Text and visual cues stay on' }}</span></div>
    <template v-if="state === 'completed'"><div class="button-row"><button class="button secondary" @click="emit('navigate','home')">Home</button><p class="small">Hold the circle again to repeat.</p></div><p class="small breathing-note">Sequence: {{ (elapsed/1000).toFixed(1) }}s · Instruction to finish: {{ instructionSeconds?.toFixed(1) }}s, excluding pauses.</p></template>
    <template v-else-if="state !== 'ready'"><button v-if="state === 'paused'" class="button full-width" @click="resume"><AppIcon name="play" /> Resume</button><button v-else class="button full-width" @click="pause()"><AppIcon name="pause" /> Pause</button><button class="button secondary full-width end-exercise" @click="end">End exercise</button></template>
    <button class="text-button" @click="emit('navigate','sessions')">View past breathing sessions</button>
  </section>
</template>
