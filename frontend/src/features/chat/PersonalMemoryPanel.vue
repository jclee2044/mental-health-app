<script setup>
const props = defineProps({ model: { type: Object, required: true } })
const { preferences, loaded, busy, error, report } = props.model
const labels = { emotions: 'Use recent emotion logs', conversations: 'Use saved conversation text', facts: 'Use facts I confirm' }
function opened(event) { if (event.target.open) props.model.interrupt() }
</script>
<template>
  <details class="personal-memory" @toggle="opened">
    <summary>Personal memory <span class="small muted">{{ report?.status === 'unavailable' ? 'Unavailable · chat continues without it' : loaded && Object.values(preferences).some(Boolean) ? 'On' : 'Off' }}</span></summary>
    <p class="small">Choose what chat may refer to. Saved text from the last seven days, selected log details and confirmed facts are sent to OpenAI with your message or when Voice starts. With saved conversation text enabled, ending a saved chat also creates a short memory summary using OpenAI. No audio is saved here.</p>
    <p class="small muted">Opening these controls stops voice and dictation. Changes apply to future requests; start Voice again to refresh its context. They cannot retract information already sent or erase current-chat messages.</p>
    <p v-if="!loaded && !error" role="status">Loading memory choices…</p>
    <p v-if="error" role="alert">{{ error }}</p>
    <p v-if="report?.chat_coverage?.status === 'partial'" class="small muted" role="status">{{ report.chat_coverage.included_conversations }} of {{ report.chat_coverage.eligible_conversations }} recent chats fit in this snapshot.</p>
    <button v-if="error || !loaded" class="text-button" type="button" :disabled="busy" @click="model.load">Reload memory</button>
    <fieldset :disabled="!loaded || busy"><legend>Allow saved context</legend>
      <label v-for="(label, key) in labels" :key="key" class="memory-choice"><input type="checkbox" :checked="preferences[key]" @change="model.updatePreference(key, $event.target.checked)"><span>{{ label }}</span></label>
    </fieldset>
  </details>
</template>
