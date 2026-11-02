import { ref } from 'vue'
import * as requests from './api.js'

export function useConversationHistory({ api = requests } = {}) {
  const conversations = ref([]), selected = ref(null), loading = ref(false), error = ref(''), confirming = ref(false)
  let active = true, revision = 0
  const controller = new AbortController()
  async function run(operation) {
    const current = ++revision
    loading.value = true; error.value = ''; confirming.value = false
    try {
      const result = await operation()
      if (active && current === revision) result()
    } catch { if (active && current === revision) error.value = 'Saved chats are unavailable. Check the local server and try again.' }
    finally { if (active && current === revision) loading.value = false }
  }
  const attempted = new Set()
  async function generateTitle(item) {
    if (item.title || item.titleState === 'loading' || !active) return
    attempted.add(item.id)
    item.titleState = 'loading'
    try {
      const result = await api.generateConversationTitle(item.id, { signal: controller.signal })
      if (typeof result.title !== 'string' || !result.title.trim() || result.title.length > 80) throw new Error('Invalid title')
      if (active) {
        item.title = result.title; item.titleState = 'saved'
        const current = conversations.value.find(chat => chat.id === item.id)
        if (current) { current.title = result.title; current.titleState = 'saved' }
        if (selected.value?.id === item.id) selected.value.title = result.title
      }
    } catch { if (active) {
      item.titleState = 'failed'
      const current = conversations.value.find(chat => chat.id === item.id)
      if (current) current.titleState = 'failed'
    } }
  }
  async function generateMissing() {
    for (const item of conversations.value) {
      if (!active) break
      if (!item.title && !attempted.has(item.id)) await generateTitle(item)
    }
  }
  const load = () => run(async () => {
    const data = await api.listConversations({ signal: controller.signal })
    return () => { conversations.value = data.conversations.map(item => ({ ...item, titleState: conversations.value.find(chat => chat.id === item.id)?.titleState })); selected.value = null; void generateMissing() }
  })
  const open = id => run(async () => {
    const data = await api.getConversation(id, { signal: controller.signal })
    return () => { selected.value = data }
  })
  const remove = () => {
    if (!confirming.value || !selected.value || loading.value) return
    const id = selected.value.id
    return run(async () => {
      await api.deleteConversation(id)
      return () => { conversations.value = conversations.value.filter(item => item.id !== id); selected.value = null }
    })
  }
  function dispose() { active = false; revision++; controller.abort() }
  return { conversations, selected, loading, error, confirming, load, open, remove, dispose, generateTitle }
}
