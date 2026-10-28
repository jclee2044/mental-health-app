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
  const load = () => run(async () => {
    const data = await api.listConversations({ signal: controller.signal })
    return () => { conversations.value = data.conversations; selected.value = null }
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
  return { conversations, selected, loading, error, confirming, load, open, remove, dispose }
}
