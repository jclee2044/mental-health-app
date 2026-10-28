import ChatView from './ChatView.vue'
import ConversationHistoryView from './ConversationHistoryView.vue'
import ChatSaveNotice from './ChatSaveNotice.vue'
import { useConversationRecords } from './useConversationRecords.js'
import './styles.css'

export function createFeature({ navigate, interrupted }) {
  const records = useConversationRecords()
  return {
    id: 'chat', routes: { chat: ChatView, conversations: ConversationHistoryView },
    props: route => route === 'chat' ? { interrupted: interrupted(), records } : { pending: records.records.value.filter(record => record.state !== 'saved') },
    events: { navigate },
    notice: { component: ChatSaveNotice, props: () => ({ records: records.records.value }), events: { retry: records.retry } },
  }
}
