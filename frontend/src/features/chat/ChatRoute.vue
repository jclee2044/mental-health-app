<script setup>
import { nextTick, ref } from 'vue'
import ChatView from './ChatView.vue'

defineProps({ interrupted: Boolean, records: Object })
defineEmits(['navigate'])
const conversationKey = ref(0)
const chat = ref(null)
async function newChat() {
  // Remount the session so its existing exit cleanup runs before a fresh chat.
  conversationKey.value++
  await nextTick()
  chat.value?.focusComposer()
}
</script>

<template>
  <ChatView ref="chat" :key="conversationKey" :interrupted="interrupted" :records="records" @navigate="$emit('navigate', $event)" @new-chat="newChat" />
</template>
