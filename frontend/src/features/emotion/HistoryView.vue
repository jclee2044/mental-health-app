<script setup>
import { localDate } from '../../dates.js'
import { computed, onMounted, onUnmounted, ref } from 'vue'
import AppIcon from '../../components/AppIcon.vue'
import ModalSheet from '../../components/ModalSheet.vue'
import { deleteEntry, listEntries } from './api.js'
import { feelings, pointSummary } from './domain.js'
const emit = defineEmits(['navigate', 'edit', 'emergency'])
const entries = ref([])
const loading = ref(true)
const error = ref('')
const month = ref(new Date(new Date().getFullYear(),new Date().getMonth(),1))
const day = ref(localDate())
const deleting = ref(null)
const busy = ref(false)
const controller = new AbortController()
let active = true
onUnmounted(() => { active = false; controller.abort() })
async function load() {
  loading.value=true; error.value=''
  try {
    const entryData = await listEntries({signal:controller.signal})
    if(active) entries.value=entryData.entries
  }
  catch(failure) { if(active) error.value=failure.message }
  finally { if(active) loading.value=false }
}
onMounted(load)
const monthName = computed(() => month.value.toLocaleDateString(undefined,{month:'long',year:'numeric'}))
const cells = computed(() => {
  const year=month.value.getFullYear(), index=month.value.getMonth()
  const offset=(new Date(year,index,1).getDay()+6)%7
  return [...Array(offset).fill(null),...Array.from({length:new Date(year,index+1,0).getDate()},(_,i)=>localDate(new Date(year,index,i+1)))]
})
const selected = computed(() => entries.value.filter(entry=>entry.local_date===day.value))
const dayTitle = computed(()=>new Date(`${day.value}T12:00:00`).toLocaleDateString(undefined,{month:'long',day:'numeric',year:'numeric'}))
function moveMonth(delta) { month.value=new Date(month.value.getFullYear(),month.value.getMonth()+delta,1) }
function forDay(date) { return entries.value.filter(entry=>entry.local_date===date) }
async function remove() {
  if(busy.value) return
  busy.value=true; error.value=''
  try { await deleteEntry(deleting.value.id,{signal:controller.signal}); if(active) { entries.value=entries.value.filter(entry=>entry.id!==deleting.value.id); deleting.value=null } }
  catch(failure) { if(active) error.value=failure.message }
  finally { busy.value=false }
}
</script>
<template>
  <section class="history-page page-enter"><div class="history-heading"><div><p class="eyebrow">Your moments</p><h1>Past logs</h1></div><button class="button secondary" @click="emit('navigate','emotion')">New entry <AppIcon name="plus" /></button></div>
    <p v-if="loading" role="status">Loading saved moments…</p>
    <div v-else-if="error && !deleting" class="error-banner" role="alert"><p>{{ error }}</p><button class="button secondary" @click="load">Try again</button></div>
    <div v-else class="history-layout">
      <div class="calendar-panel"><div class="calendar-heading"><button class="icon-button" aria-label="Previous month" @click="moveMonth(-1)"><AppIcon name="arrow-left" /></button><h2>{{ monthName }}</h2><button class="icon-button" aria-label="Next month" @click="moveMonth(1)"><AppIcon name="arrow-right" /></button></div><div class="calendar-grid"><span v-for="weekday in ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']" :key="weekday" class="weekday">{{ weekday }}</span><template v-for="(date,index) in cells" :key="date || `blank-${index}`"><span v-if="!date"></span><button v-else class="calendar-day" :class="{ selected: day===date, today: date===localDate() }" :aria-pressed="day===date" :aria-label="`${date}, ${forDay(date).length} entries`" @click="day=date">{{ Number(date.slice(-2)) }}<span v-if="forDay(date).length" class="calendar-dot" :style="{background:forDay(date)[0].color}"></span></button></template></div><p class="small muted calendar-key"><span class="color-dot"></span> A saved entry · your chosen color</p></div>
      <div class="day-entries"><p class="eyebrow">{{ dayTitle }}</p><template v-if="!selected.length"><div class="empty-state"><span class="empty-icon"><AppIcon name="calendar" /></span><h2>No entries here yet.</h2><p>{{ entries.length ? 'Choose another day, or notice a new moment.' : 'Your saved moments will appear here.' }}</p><button class="button" @click="emit('navigate','emotion')">Emotion log</button></div></template><article v-for="entry in selected" :key="entry.id" class="entry-card"><div class="entry-card-top"><span class="color-dot" :style="{background:entry.color}"></span><strong>{{ feelings[entry.feeling-1] }}</strong><time :datetime="entry.recorded_at">{{ new Date(entry.recorded_at).toLocaleTimeString(undefined,{hour:'numeric',minute:'2-digit'}) }}</time></div><p class="small">{{ pointSummary(entry.pleasantness,entry.energy) }}<br>Pleasantness {{ entry.pleasantness }} · Energy {{ entry.energy }}</p><p v-if="entry.color_meaning" class="small">Color meaning: {{ entry.color_meaning }}</p><p v-if="entry.note" class="entry-note">{{ entry.note }}</p><div class="entry-actions"><button class="text-button" @click="emit('edit',entry)">Edit entry</button><button class="text-button delete-link" @click="deleting=entry">Delete</button></div></article></div>
    </div>
    <ModalSheet v-if="deleting" title="Delete this entry?" @close="deleting=null" @emergency="emit('emergency')"><p>This entry will be removed from your past logs. This can’t be undone in the app.</p><p v-if="error" class="error-banner" role="alert">{{ error }}</p><button class="button danger full-width" :disabled="busy" @click="remove">{{ busy ? 'Deleting…' : 'Delete entry' }}</button></ModalSheet>
  </section>
</template>
