<script setup>
import { computed, onMounted, onBeforeUnmount } from 'vue'
import AppIcon from '../../components/AppIcon.vue'
import { useConversationHistory } from './useConversationHistory.js'
const props = defineProps({ pending: { type: Array, default: () => [] } })
defineEmits(['navigate'])
const { conversations, selected, loading, error, confirming, load, open, remove, dispose } = useConversationHistory()
const savingSelected = computed(() => selected.value && props.pending.some(record => record.conversationId === selected.value.id))
onMounted(load)
onBeforeUnmount(dispose)
</script>
<template>
  <section class="narrow-page page-enter">
    <div class="chat-history-heading"><h1>Saved chats</h1><button class="button secondary" @click="$emit('navigate', 'chat')">New</button></div>
    <p class="small muted">Review only. Opening a saved chat doesn’t send it to a model.</p>
    <p v-if="loading" role="status">Loading saved chats…</p>
    <div v-else-if="error" class="chat-storage-error" role="alert"><p>{{ error }}</p><button class="button secondary" @click="selected ? open(selected.id) : load()">Try again</button></div>
    <template v-else-if="selected">
      <p>{{ new Date(selected.created_at).toLocaleString() }} · {{ selected.message_count }} messages</p>
      <ol class="chat-transcript" aria-label="Saved conversation">
        <li v-for="(message, index) in selected.messages" :key="`${message.turn_id}-${index}`" class="chat-bubble" :class="`chat-${message.role}`"><span class="chat-speaker">{{ message.role === 'user' ? 'You' : 'inspire' }}</span><p>{{ message.content }}</p></li>
      </ol>
      <p v-if="savingSelected" role="status">Finish retrying this chat’s pending saves before deleting it.</p>
      <div v-if="confirming" class="chat-storage-error" role="group" aria-label="Confirm conversation deletion"><p>Delete this saved chat? This does not delete provider records or backups.</p><button class="button secondary" @click="confirming = false">Cancel</button><button class="button secondary" @click="remove">Delete saved chat</button></div>
      <button v-else class="text-button" :disabled="savingSelected" @click="confirming = true">Delete this chat</button>
      <button class="history-button" type="button" aria-label="All saved chats" title="All saved chats" @click="load"><AppIcon name="history" /></button>
    </template>
    <template v-else>
      <p v-if="!conversations.length">No chats have been saved yet.</p>
      <button v-for="item in conversations" :key="item.id" class="button secondary full-width saved-chat" @click="open(item.id)">{{ new Date(item.created_at).toLocaleString() }} · {{ item.message_count }} messages</button>
      <button class="text-button" @click="load">Refresh saved chats</button>
    </template>
  </section>
</template>
