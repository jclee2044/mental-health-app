import { ref } from 'vue'
import { saveSession } from './api.js'

// This coordinator survives view changes. Failed records remain retryable in memory.
export function useSessionRecords() {
  const records = ref([])
  async function submit(record) {
    if (record.state === 'saving' || record.state === 'saved') return
    record.state = 'saving'
    try { await saveSession(record.id, record.body); record.state = 'saved'; record.message = 'Breathing session saved.' }
    catch (error) { record.state = 'failed'; record.message = `${error.message} This session hasn’t been saved. Retry before closing the app.` }
  }
  function queue({ id, ...body }) {
    if (records.value.some(record => record.id === id)) return
    records.value.push({ id, body, state: 'pending', message: '' })
    submit(records.value[records.value.length - 1])
  }
  function clearSaved() { records.value = records.value.filter(record => record.state !== 'saved') }
  return { records, queue, retry: submit, clearSaved }
}
