<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import AppIcon from '../../components/AppIcon.vue'
import { BreathingClock, PATTERN, phaseAt } from './clock.js'
import { localDate } from '../../dates.js'
import { BreathAudio } from './audio.js'
const props = defineProps({ interrupted: Boolean, reducedMotion: Boolean })
const emit = defineEmits(['navigate', 'record', 'start'])
const audio = new BreathAudio()
const soundEnabled = ref(true)
const soundStatus = ref('Soft inhale & exhale sounds')
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
  if (props.interrupted) return
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
  if (props.interrupted || document.hidden) return
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
function visibility() { if (document.hidden) pause('You stepped away. Resume when you’re ready.') }
watch(() => props.interrupted, value => { if (value) pause('Take your time. Resume when you’re ready.') })
onMounted(() => document.addEventListener('visibilitychange', visibility))
onBeforeUnmount(() => { cancelAnimationFrame(frame); audio.close(); clock.end(performance.now()); record(); document.removeEventListener('visibilitychange', visibility) })
const heading = computed(() => state.value === 'ready' ? 'A gentler rhythm.' : state.value === 'paused' ? 'Take your time.' : state.value === 'completed' ? 'A moment, taken.' : cue.value.phase === 'countdown' ? 'Settle in.' : cue.value.phase === 'inhale' ? 'Breathe in.' : 'Breathe out.')
const circleScale = computed(() => {
  if (props.reducedMotion || state.value === 'ready' || state.value === 'completed' || cue.value.phase === 'countdown') return 1
  const progress = cue.value.progress
  return cue.value.phase === 'inhale' ? .78 + .6 * progress : 1.38 - .6 * progress
})
async function unlockSound() {
  try { await audio.unlock(); audioKey = ''; soundStatus.value = 'Soft inhale & exhale sounds'; syncAudio() }
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
    <p class="eyebrow">{{ state === 'ready' ? 'One minute · Just breathe' : state === 'completed' ? 'Exercise complete' : 'Your pace, one breath at a time' }}</p>
    <h1 aria-live="polite">{{ heading }}</h1>
    <p class="breathing-description">{{ state === 'ready' ? 'Breathe in for 4 seconds, then out for 6. No holds.' : state === 'paused' ? pauseReason : state === 'completed' ? 'You’ve finished the breathing exercise.' : cue.phase === 'countdown' ? 'Find a comfortable position.' : props.reducedMotion ? 'Let the words carry the pace.' : 'Follow the circle, gently.' }}</p>
    <div class="breathing-stage"><div class="breathing-guide-ring"></div><div class="breathing-circle" :style="{transform:`scale(${circleScale})`}" :data-phase="cue.phase" :data-scale="circleScale.toFixed(3)"><AppIcon v-if="state === 'ready'" name="wind" /><AppIcon v-else-if="state === 'completed'" name="check" /><AppIcon v-else-if="state === 'paused'" name="pause" /></div><div v-if="state === 'running'" class="breathing-count" aria-hidden="true">{{ cue.count }}</div></div>
    <p class="breathing-progress" role="status">{{ state === 'ready' ? '6 cycles · 60 seconds of breathing' : state === 'completed' ? '6 of 6 cycles' : cue.phase === 'countdown' ? '3–2–1 countdown' : `Cycle ${cue.cycle} of 6 · ${Math.floor(Math.max(0,elapsed-3000)/1000)} / 60 seconds` }}</p>
    <div class="sound-control" :data-audio-phase="audioKey" :data-audio-state="audio.context?.state || 'idle'"><button class="text-button" :aria-pressed="soundEnabled" :aria-label="soundEnabled ? 'Mute breathing sounds' : 'Enable breathing sounds'" @click="toggleSound"><AppIcon :name="soundEnabled ? 'sound' : 'mute'" /> {{ soundEnabled ? 'Sound on' : 'Sound off' }}</button><span class="small muted" role="status">{{ soundEnabled ? soundStatus : 'Text and visual cues stay on' }}</span></div>
    <template v-if="state === 'ready'"><button class="button full-width" @click="begin">Begin <AppIcon name="arrow-right" /></button><p class="small breathing-note">You can pause or end whenever you like.</p></template>
    <template v-else-if="state === 'completed'"><div class="button-row"><button class="button secondary" @click="emit('navigate','home')">Home</button><button class="button" @click="begin">Repeat</button></div><p class="small breathing-note">Sequence: {{ (elapsed/1000).toFixed(1) }}s · Instruction to finish: {{ instructionSeconds?.toFixed(1) }}s, excluding pauses.</p></template>
    <template v-else><button v-if="state === 'paused'" class="button full-width" @click="resume"><AppIcon name="play" /> Resume</button><button v-else class="button full-width" @click="pause()"><AppIcon name="pause" /> Pause</button><button class="button secondary full-width end-exercise" @click="end">End exercise</button></template>
    <button class="text-button" @click="emit('navigate','sessions')">View past breathing sessions</button>
  </section>
</template>
