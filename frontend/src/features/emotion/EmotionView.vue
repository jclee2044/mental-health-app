<script setup>
import { localDate } from '../../dates.js'
import { computed, onUnmounted, reactive, ref } from 'vue'
import AppIcon from '../../components/AppIcon.vue'
import { saveEntry } from './api.js'
import { colors } from './domain.js'
import { graphInteraction } from './graph.js'
const props = defineProps({ entry: { type: Object, default: null } })
const emit = defineEmits(['navigate'])
const draft = reactive({ feeling: props.entry?.feeling ?? null, color: props.entry?.color ?? null, color_meaning: props.entry?.color_meaning || '', pleasantness: props.entry?.pleasantness ?? 0, energy: props.entry?.energy ?? 0, note: props.entry?.note || '', recorded_at: props.entry?.recorded_at || new Date().toISOString(), local_date: props.entry?.local_date || localDate() })
const entryId = props.entry?.id || crypto.randomUUID()
const saved = ref(false)
const chosenPoint = ref(Boolean(props.entry))
const fields = ref({})
const apiFieldErrors = computed(() => Object.fromEntries(Object.entries(fields.value).filter(([key]) => !['graph', 'color'].includes(key))))
const error = ref('')
const saving = ref(false)
const controller = new AbortController()
let active = true
onUnmounted(() => { active = false; controller.abort() })
const graph = graphInteraction((pleasantness, energy) => {
  if (saving.value) return
  draft.pleasantness = pleasantness
  draft.energy = energy
  chosenPoint.value = true
})
function graphKey(event) {
  const movement = { ArrowLeft: [-5, 0], ArrowRight: [5, 0], ArrowUp: [0, 5], ArrowDown: [0, -5], Enter: [0, 0], ' ': [0, 0] }[event.key]
  if (!movement || saving.value) return
  event.preventDefault()
  draft.pleasantness = Math.max(-100, Math.min(100, draft.pleasantness + movement[0]))
  draft.energy = Math.max(-100, Math.min(100, draft.energy + movement[1]))
  chosenPoint.value = true
}
async function save() {
  if (saving.value) return
  fields.value = {}
  if (!chosenPoint.value) fields.value.graph = 'Place a point on the graph, or use the sliders.'
  if (!draft.color) fields.value.color = 'Choose a color.'
  if (Object.keys(fields.value).length) return
  error.value = ''; fields.value = {}; saving.value = true
  try {
    await saveEntry(entryId, { ...draft }, { signal: controller.signal })
    if (active) saved.value = true
  } catch (failure) { if (active) { error.value = failure.message; fields.value = failure.fields || {} } }
  finally { saving.value = false }
}
</script>
<template>
  <section class="narrow-page emotion-page page-enter">
    <template v-if="!saved">
        <h1>How are you<br><em>feeling today?</em></h1>
        <form novalidate @submit.prevent="save">
          <fieldset class="graph-field"><legend>Pleasantness × energy <span class="required-note">Required</span></legend>
            <p id="graph-help" class="small muted">Tap or drag to place your point.</p>
            <div class="graph-wrap"><span class="axis-top">High energy</span><span class="axis-left">Unpleasant</span><div class="emotion-graph" role="group" tabindex="0" aria-label="Pleasantness and energy graph" aria-describedby="graph-help graph-keyboard" @pointerdown="graph.down" @pointermove="graph.move" @pointerup="graph.up" @pointercancel="graph.cancel" @lostpointercapture="graph.cancel" @keydown="graphKey"><div v-if="chosenPoint" class="graph-point" :style="{left:`${(draft.pleasantness+100)/2}%`,top:`${(100-draft.energy)/2}%`,background:draft.color || 'var(--accent)'}"></div><span v-else class="graph-instruction">Place your point</span></div><span class="axis-right">Pleasant</span><span class="axis-bottom">Low energy</span></div>
            <details class="graph-controls"><summary>Use sliders or keyboard</summary>
              <p id="graph-keyboard" class="small muted">Focus the graph and use arrow keys to move. Enter or Space selects the center before placement.</p>
              <label for="pleasantness">Pleasantness <output>{{ draft.pleasantness }}</output></label><input id="pleasantness" v-model.number="draft.pleasantness" :disabled="saving" type="range" min="-100" max="100" @input="chosenPoint=true">
              <label for="energy">Energy <output>{{ draft.energy }}</output></label><input id="energy" v-model.number="draft.energy" :disabled="saving" type="range" min="-100" max="100" @input="chosenPoint=true">
            </details>
            <p v-if="fields.graph" class="field-error" role="alert">{{ fields.graph }}</p>
          </fieldset>
          <fieldset><legend>Choose a color <span class="required-note">Required</span></legend><div class="swatches"><button v-for="color in colors" :key="color.value" type="button" class="swatch" :style="{'--swatch':color.value}" :aria-label="color.name" :aria-pressed="draft.color===color.value" @click="draft.color=color.value"><AppIcon v-if="draft.color===color.value" name="check" /></button><label class="custom-color" aria-label="Custom color"><input type="color" aria-label="Custom color" :value="draft.color || '#8fa98d'" @input="draft.color=$event.target.value"><span aria-hidden="true">+</span></label></div><p class="small muted color-hint">Your color, your meaning.</p><p v-if="fields.color" class="field-error" role="alert">{{ fields.color }}</p></fieldset>
          <label for="color-meaning">What does this color mean to you? <span class="optional">Optional</span></label><input id="color-meaning" v-model="draft.color_meaning" type="text" maxlength="80" placeholder="A word or two, if you like">
          <label for="entry-note">Anything you’d like to add? <span class="optional">Optional</span></label><textarea id="entry-note" v-model="draft.note" rows="3" maxlength="2000" placeholder="Leave a little note for yourself…"></textarea>
          <p v-if="error" class="error-banner" role="alert">{{ error }} Your entry is still here.</p>
          <p v-for="(message,key) in apiFieldErrors" :key="key" class="field-error" role="alert">{{ message }}</p>
          <div class="button-row form-next"><button class="button secondary" type="button" @click="emit('navigate','home')">Cancel</button><button class="button" :disabled="saving" type="submit">{{ saving ? 'Saving…' : entry ? 'Save changes' : 'Save entry' }}</button></div>
        </form>
      <div class="form-links"><button class="history-button" type="button" aria-label="View past logs" title="View past logs" @click="emit('navigate','history')"><AppIcon name="history" /></button></div>
    </template>
    <template v-else><div class="saved-state"><span class="saved-mark"><AppIcon name="check" /></span><h1>Entry saved.</h1><p>You can come back to it whenever you like.</p><button class="history-button" type="button" aria-label="View past logs" title="View past logs" @click="emit('navigate','history')"><AppIcon name="history" /></button></div></template>
  </section>
</template>
