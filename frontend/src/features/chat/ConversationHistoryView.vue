<script setup>
import { computed, onMounted, onBeforeUnmount } from 'vue'
import AppIcon from '../../components/AppIcon.vue'
import { useConversationHistory } from './useConversationHistory.js'
const props = defineProps({ pending: { type: Array, default: () => [] } })
defineEmits(['navigate'])
const { conversations, selected, loading, error, confirming, load, open, remove, dispose, generateTitle } = useConversationHistory()
const savingSelected = computed(() => selected.value && props.pending.some(record => record.conversationId === selected.value.id))
onMounted(load)
onBeforeUnmount(dispose)
</script>
<template>
  <section class="narrow-page page-enter">
    <div class="chat-history-heading"><h1>Saved chats</h1><button class="button secondary" @click="$emit('navigate', 'chat')">New</button></div>
    <p class="small muted">Chats without titles send a short text excerpt to the configured model to create a title. Opening a chat is read-only.</p>
    <p v-if="loading" role="status">Loading saved chats…</p>
    <div v-else-if="error" class="chat-storage-error" role="alert"><p>{{ error }}</p><button class="button secondary" @click="selected ? open(selected.id) : load()">Try again</button></div>
    <template v-else-if="selected">
      <h2>{{ selected.title || 'Saved conversation' }}</h2>
      <p class="small muted">{{ new Date(selected.created_at).toLocaleString() }} · {{ selected.message_count }} messages</p>
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
      <div v-for="item in conversations" :key="item.id" class="saved-chat-row">
        <button class="button secondary full-width saved-chat" @click="open(item.id)"><strong>{{ item.title || 'Saved conversation' }}</strong><time class="small muted" :datetime="item.created_at">{{ new Date(item.created_at).toLocaleString() }}</time></button>
        <p v-if="item.titleState === 'loading'" class="small muted" role="status">Creating title…</p>
        <p v-else-if="item.titleState === 'failed'" class="small muted" role="status">Title unavailable. <button class="text-button" @click="generateTitle(item)">Retry title</button></p>
      </div>
      <button class="text-button" @click="load">Refresh saved chats</button>
    </template>
  </section>
</template>
