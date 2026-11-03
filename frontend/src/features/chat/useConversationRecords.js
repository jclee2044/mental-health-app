import { ref } from 'vue'
import * as requests from './api.js'

// Owned by the feature registration so retries survive navigation, not reloads.
export function useConversationRecords({ api = requests } = {}) {
  const records = ref([])
  const summaries = ref([])
  const ended = new Map()
  async function retrySummary(summary) {
    const ending = ended.get(summary.conversationId)
    if (!ending || ['running', 'saved'].includes(summary.state)) return
    if (ending.records.some(record => record.state !== 'saved')) { summary.state = 'failed'; return }
    ending.records = [] // Do not retain completed transcript bodies for summary retries.
    summary.state = 'running'
    try {
      const result = await api.generateMemorySummary(summary.conversationId, summary.attempted === true)
      summary.attempted = true
      if (['ready', 'empty'].includes(result?.status)) summary.state = 'saved'
      else if (['off', 'excluded', 'missing', 'discarded'].includes(result?.status)) summary.state = 'skipped'
      else if (result?.status === 'pending') summary.state = 'pending'
      else summary.state = 'failed'
    } catch { summary.attempted = true; summary.state = 'failed' }
  }
  function checkSummary(conversationId) {
    const ending = ended.get(conversationId)
    if (!ending || ending.summary.state !== 'waiting') return
    if (ending.requiresManual || ending.records.some(record => record.state === 'failed')) {
      ending.summary.state = 'failed'; return
    }
    if (ending.records.every(record => record.state === 'saved')) void retrySummary(ending.summary)
  }
  function finishConversation(conversationId, { summarize = false } = {}) {
    if (!summarize || !api.generateMemorySummary || ended.has(conversationId)) return
    const saved = records.value.filter(record => record.conversationId === conversationId)
    if (!saved.length) return
    summaries.value.push({ conversationId, state: 'waiting', attempted: false })
    const summary = summaries.value.at(-1)
    ended.set(conversationId, { records: saved, summary, requiresManual: saved.some(record => record.manualSaveRetry) })
    checkSummary(conversationId)
  }
  async function retry(record) {
    if (record.state === 'saving' || record.state === 'saved') return
    const initialSave = record.state === 'pending'
    const ending = ended.get(record.conversationId)
    // A manual storage retry must never indirectly initiate a paid summary.
    if (!initialSave) {
      record.manualSaveRetry = true
      if (ending) ending.requiresManual = true
    }
    record.state = 'saving'
    try {
      const save = record.kind === 'voice' ? api.saveVoiceTurn : api.saveChatTurn
      const result = await save(record.conversationId, record.turnId, record.body)
      if (result?.saved !== true || result.conversation_id !== record.conversationId || result.turn_id !== record.turnId) throw new Error('Invalid save response')
      record.state = 'saved'
    } catch { record.state = 'failed' }
    if (initialSave) checkSummary(record.conversationId)
  }
  function queue(record) {
    records.value.push({ ...record, state: 'pending' })
    return retry(records.value.at(-1))
  }
  function clearSaved() { records.value = records.value.filter(record => record.state !== 'saved') }
  return { records, summaries, queue, retry, clearSaved, finishConversation, retrySummary }
}
