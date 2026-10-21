<script setup>
import { localDate } from '../../dates.js'
import { computed, onUnmounted, reactive, ref } from 'vue'
import AppIcon from '../../components/AppIcon.vue'
import { saveEntry } from './api.js'
import { colors, feelings, pointSummary } from './domain.js'
const props = defineProps({ entry: { type: Object, default: null } })
const emit = defineEmits(['navigate'])
const draft = reactive({ feeling: props.entry?.feeling ?? null, color: props.entry?.color ?? null, color_meaning: props.entry?.color_meaning || '', pleasantness: props.entry?.pleasantness ?? 0, energy: props.entry?.energy ?? 0, note: props.entry?.note || '', recorded_at: props.entry?.recorded_at || new Date().toISOString(), local_date: props.entry?.local_date || localDate() })
const entryId = props.entry?.id || crypto.randomUUID()
const step = ref(1)
const chosenPoint = ref(Boolean(props.entry))
const fields = ref({})
const error = ref('')
const saving = ref(false)
const controller = new AbortController()
let active = true
onUnmounted(() => { active = false; controller.abort() })
const summary = computed(() => pointSummary(draft.pleasantness, draft.energy))
function next() {
  fields.value = {}
  if (draft.feeling === null) fields.value.feeling = 'Choose a feeling to continue.'
  if (!draft.color) fields.value.color = 'Choose a color to continue.'
  if (Object.keys(fields.value).length) return
  step.value = 2
}
function place(event) {
  const bounds = event.currentTarget.getBoundingClientRect()
  draft.pleasantness = Math.round(Math.max(-100, Math.min(100, ((event.clientX - bounds.left) / bounds.width) * 200 - 100)))
  draft.energy = Math.round(Math.max(-100, Math.min(100, 100 - ((event.clientY - bounds.top) / bounds.height) * 200)))
  chosenPoint.value = true
}
function graphKey(event) {
  const movement = { ArrowLeft: [-5, 0], ArrowRight: [5, 0], ArrowUp: [0, 5], ArrowDown: [0, -5], Enter: [0, 0], ' ': [0, 0] }[event.key]
  if (!movement) return
  event.preventDefault()
  draft.pleasantness = Math.max(-100, Math.min(100, draft.pleasantness + movement[0]))
  draft.energy = Math.max(-100, Math.min(100, draft.energy + movement[1]))
  chosenPoint.value = true
}
async function save() {
  if (saving.value) return
  if (!chosenPoint.value) { fields.value = { graph: 'Place a point on the graph, or use the sliders.' }; return }
  error.value = ''; fields.value = {}; saving.value = true
  try {
    await saveEntry(entryId, { ...draft }, { signal: controller.signal })
    if (active) step.value = 3
  } catch (failure) { if (active) { error.value = failure.message; fields.value = failure.fields || {} } }
  finally { saving.value = false }
}
</script>
<template>
  <section class="narrow-page emotion-page page-enter">
    <template v-if="step < 3">
      <template v-if="step === 1">
        <h1>How are you<br><em>feeling today?</em></h1><p class="small">A moment to notice. No explanation needed.</p>
        <div class="feeling-bubble" :style="{background: draft.color || '#d7dfd0'}" aria-hidden="true"><AppIcon name="leaf" /></div>
        <form novalidate @submit.prevent="next">
          <fieldset><legend>Choose a feeling <span class="required-note">Required</span></legend><div class="feeling-options"><label v-for="(feeling,index) in feelings" :key="feeling" :class="{selected:draft.feeling===index+1}"><input v-model="draft.feeling" type="radio" name="feeling" :value="index+1"><span>{{ feeling }}</span></label></div><p v-if="fields.feeling" class="field-error" role="alert">{{ fields.feeling }}</p></fieldset>
          <fieldset><legend>Choose a color <span class="required-note">Required</span></legend><div class="swatches"><button v-for="color in colors" :key="color.value" type="button" class="swatch" :style="{'--swatch':color.value}" :aria-label="color.name" :aria-pressed="draft.color===color.value" @click="draft.color=color.value"><AppIcon v-if="draft.color===color.value" name="check" /></button><label class="custom-color" aria-label="Custom color"><input type="color" aria-label="Custom color" :value="draft.color || '#8fa98d'" @input="draft.color=$event.target.value"><span aria-hidden="true">+</span></label></div><p class="small muted color-hint">Your color, your meaning.</p><p v-if="fields.color" class="field-error" role="alert">{{ fields.color }}</p></fieldset>
          <label for="color-meaning">What does this color mean to you? <span class="optional">Optional</span></label><input id="color-meaning" v-model="draft.color_meaning" type="text" maxlength="80" placeholder="A word or two, if you like">
          <label for="entry-note">Anything you’d like to add? <span class="optional">Optional</span></label><textarea id="entry-note" v-model="draft.note" rows="3" maxlength="2000" placeholder="Leave a little note for yourself…"></textarea>
          <button class="button full-width form-next" type="submit">Continue <AppIcon name="arrow-right" /></button>
        </form>
      </template>
      <template v-else>
        <h1>Where would you<br><em>place this feeling?</em></h1><p class="small">Tap the graph or use the sliders. There’s no right answer.</p>
        <div class="entry-tag"><span class="color-dot" :style="{background:draft.color}"></span>{{ feelings[draft.feeling-1] }}</div>
        <div class="graph-wrap"><span class="axis-top">High energy</span><span class="axis-left">Unpleasant</span><div class="emotion-graph" role="button" tabindex="0" aria-label="Pleasantness and energy graph. Arrow keys move the point; Enter selects the center." @click="place" @keydown="graphKey"><div v-if="chosenPoint" class="graph-point" :style="{left:`${(draft.pleasantness+100)/2}%`,top:`${(100-draft.energy)/2}%`,background:draft.color}"></div><span v-else class="graph-instruction">Place your point</span></div><span class="axis-right">Pleasant</span><span class="axis-bottom">Low energy</span></div>
        <p class="point-summary" aria-live="polite">{{ chosenPoint ? summary : 'No point selected yet' }}</p>
        <label for="pleasantness">Pleasantness <output>{{ draft.pleasantness }}</output></label><input id="pleasantness" v-model.number="draft.pleasantness" type="range" min="-100" max="100" @input="chosenPoint=true"><label for="energy">Energy <output>{{ draft.energy }}</output></label><input id="energy" v-model.number="draft.energy" type="range" min="-100" max="100" @input="chosenPoint=true">
        <p v-for="(message,key) in fields" :key="key" class="field-error" role="alert">{{ message }}</p><p v-if="error" class="error-banner" role="alert">{{ error }} Your entry is still here.</p>
        <div class="button-row"><button class="button secondary" :disabled="saving" @click="step=1">Back</button><button class="button" :disabled="saving" @click="save">{{ saving ? 'Saving…' : entry ? 'Save changes' : 'Save entry' }}</button></div>
      </template>
      <div class="form-links"><button class="text-button" @click="emit('navigate','history')">View past logs</button><button class="text-button" @click="emit('navigate','home')">Leave without saving</button></div>
    </template>
    <template v-else><div class="saved-state"><span class="saved-mark"><AppIcon name="check" /></span><h1>Entry saved.</h1><p>You can come back to it whenever you like.</p><button class="button full-width" @click="emit('navigate','home')">Home</button><button class="button secondary full-width" @click="emit('navigate','history')">View past logs</button></div></template>
  </section>
</template>
