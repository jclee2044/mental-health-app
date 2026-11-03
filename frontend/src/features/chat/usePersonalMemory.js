import { computed, ref } from 'vue'

const localDay = () => {
  const now = new Date()
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`
}
const validPreferences = value => value && ['emotions', 'conversations', 'facts'].every(key => typeof value[key] === 'boolean')
export const validMemoryReport = value => value && ['ready', 'off', 'unavailable'].includes(value.status) && Array.isArray(value.sources) && new TextEncoder().encode(JSON.stringify(value)).length <= 16000

export function usePersonalMemory({ api, conversationId, interrupt = () => {} }) {
  const preferences = ref({ emotions: false, conversations: false, facts: false })
  const loaded = ref(false), busy = ref(false), error = ref(''), facts = ref([]), exclusions = ref([])
  const report = ref(null), original = ref(null), query = ref(''), draft = ref(''), editing = ref(null), sourceConversation = ref(null)
  const enabled = computed(() => loaded.value && Object.values(preferences.value).some(Boolean))
  let active = true, revision = 0
  const controller = new AbortController()
  const options = { signal: controller.signal }
  const scope = () => enabled.value ? { local_date: localDay(), conversation_id: conversationId } : null

  async function run(operation) {
    if (!active || busy.value) return
    busy.value = true; error.value = ''
    const current = ++revision
    try {
      const apply = await operation()
      if (active && current === revision) apply?.()
    } catch {
      if (active && current === revision) error.value = 'Memory could not be loaded or saved. Check the local server, then try again. Chat remains available.'
    } finally { if (active && current === revision) busy.value = false }
  }
  async function load() {
    if (!api.getMemoryPreferences) return
    return run(async () => {
      const value = await api.getMemoryPreferences(options)
      if (!validPreferences(value)) throw new Error('Invalid preferences')
      return () => { preferences.value = value; loaded.value = true }
    })
  }
  function updatePreference(key, value) {
    interrupt()
    return run(async () => {
      const saved = await api.setMemoryPreferences({ ...preferences.value, [key]: value }, options)
      if (!validPreferences(saved)) throw new Error('Invalid preferences')
      return () => { preferences.value = saved; report.value = null; original.value = null }
    })
  }
  function acceptReport(value) {
    if (active && validMemoryReport(value)) report.value = value
  }
  const preview = () => run(async () => {
    const result = await api.previewMemory({ local_date: localDay(), conversation_id: conversationId, query: query.value }, options)
    if (!validMemoryReport(result)) throw new Error('Invalid context')
    return () => { report.value = result; original.value = null }
  })
  function editFact(item = null) {
    interrupt(); editing.value = item?.id ?? null; draft.value = item?.text ?? ''
    sourceConversation.value = item?.conversation_id ?? null
  }
  function remember(source) {
    editFact(); draft.value = source.text ?? ''; sourceConversation.value = source.kind === 'conversation' ? source.id : null
  }
  const saveFact = () => {
    interrupt()
    const id = editing.value ?? crypto.randomUUID()
    return run(async () => {
      const item = await api.putMemoryFact(id, { text: draft.value, conversation_id: sourceConversation.value }, options)
      return () => { facts.value = [item, ...facts.value.filter(value => value.id !== id)]; draft.value = ''; editing.value = null; sourceConversation.value = null; report.value = null }
    })
  }
  const forgetFact = id => {
    interrupt()
    const source = facts.value.find(item => item.id === id)?.conversation_id
    return run(async () => {
      await api.deleteMemoryFact(id, options)
      return () => {
        facts.value = facts.value.filter(value => value.id !== id && (!source || value.conversation_id !== source))
        if (source && !exclusions.value.some(item => item.kind === 'conversation' && item.source_id === source)) exclusions.value.push({ kind: 'conversation', source_id: source })
        report.value = null; original.value = null; if (editing.value === id || sourceConversation.value === source) editFact()
      }
    })
  }
  const exclude = source => {
    interrupt()
    return run(async () => {
      const value = { kind: source.kind, source_id: source.id }
      await api.excludeMemorySource(value, options)
      return () => {
        if (!exclusions.value.some(item => item.kind === value.kind && item.source_id === value.source_id)) exclusions.value.push(value)
        facts.value = facts.value.filter(item => item.conversation_id !== source.id)
        report.value = null; original.value = null
      }
    })
  }
  const restore = source => run(async () => {
    await api.restoreMemorySource(source.kind, source.source_id, options)
    return () => { exclusions.value = exclusions.value.filter(item => item !== source); report.value = null }
  })
  const openSource = source => run(async () => {
    const result = await api.getMemorySource(source.kind, source.id, options)
    return () => { original.value = result }
  })
  function dispose() { active = false; revision++; controller.abort(); report.value = null; original.value = null }
  void load()
  return { preferences, loaded, busy, error, facts, exclusions, enabled, report, original, query, draft, editing, sourceConversation,
    scope, load, updatePreference, acceptReport, preview, editFact, remember, saveFact, forgetFact, exclude, restore, openSource, dispose, interrupt }
}
