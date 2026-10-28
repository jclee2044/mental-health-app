<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import AppIcon from '../../components/AppIcon.vue'
import { listSessions } from './api.js'
defineEmits(['navigate'])
const sessions = ref([]), loading = ref(true), error = ref('')
const controller = new AbortController()
let active = true
onUnmounted(() => { active = false; controller.abort() })
async function load() {
  loading.value = true; error.value = ''
  try { const data = await listSessions({ signal: controller.signal }); if (active) sessions.value = data.sessions }
  catch (failure) { if (active) error.value = failure.message }
  finally { if (active) loading.value = false }
}
onMounted(load)
</script>
<template><section class="narrow-page page-enter"><h1>Past sessions</h1><p v-if="loading" role="status">Loading sessions…</p><div v-else-if="error" class="error-banner" role="alert"><p>{{ error }}</p><button class="button secondary" @click="load">Try again</button></div><template v-else><p v-if="!sessions.length">Your breathing sessions will appear here.</p><article v-for="session in sessions" :key="session.id" class="session-card"><AppIcon name="wind" /><div><strong>{{ session.status === 'completed' ? 'Six cycles completed' : 'Exercise ended' }}</strong><p>{{ session.active_seconds.toFixed(1) }}s breathing · {{ session.pause_seconds.toFixed(1) }}s paused</p><p>{{ session.sequence_seconds.toFixed(1) }}s sequence · {{ session.instruction_seconds.toFixed(1) }}s instruction to finish, excluding pauses</p><p>{{ session.local_date }} · {{ new Date(session.started_at).toLocaleTimeString(undefined,{hour:'numeric',minute:'2-digit'}) }}</p></div></article></template><button class="button secondary full-width" @click="$emit('navigate','breathing')">Guided breathing</button></section></template>
