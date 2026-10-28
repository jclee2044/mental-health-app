import { ref } from 'vue'
import * as requests from './api.js'

// Owned by the feature registration so retries survive navigation, not reloads.
export function useConversationRecords({ api = requests } = {}) {
  const records = ref([])
  async function retry(record) {
    if (record.state === 'saving' || record.state === 'saved') return
    record.state = 'saving'
    try {
      const save = record.kind === 'voice' ? api.saveVoiceTurn : api.saveChatTurn
      const result = await save(record.conversationId, record.turnId, record.body)
      if (result?.saved !== true || result.conversation_id !== record.conversationId || result.turn_id !== record.turnId) throw new Error('Invalid save response')
      record.state = 'saved'
    } catch { record.state = 'failed' }
  }
  function queue(record) {
    records.value.push({ ...record, state: 'pending' })
    return retry(records.value.at(-1))
  }
  function clearSaved() { records.value = records.value.filter(record => record.state !== 'saved') }
  return { records, queue, retry, clearSaved }
}
