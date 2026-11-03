<script setup>
defineProps({ records: { type: Array, required: true }, summaries: { type: Array, default: () => [] } })
defineEmits(['retry', 'retrySummary'])
</script>
<template>
  <div v-for="record in records.filter(item => item.state !== 'saved' || item === records.at(-1))" :key="record.turnId" class="chat-save-notice" :class="{ 'chat-storage-error': record.state === 'failed' }" role="status">
    <span>{{ record.state === 'saved' ? 'Chat saved.' : record.state === 'failed' ? 'Chat not saved. Retry before reloading or closing the app.' : 'Saving chat…' }}</span>
    <button v-if="record.state === 'failed'" class="text-button" @click="$emit('retry', record)">Retry chat save</button>
  </div>
  <div v-for="summary in summaries.filter(item => item.state === 'failed')" :key="summary.conversationId" class="chat-save-notice" role="status">
    <span>Memory summary unavailable. Recent chat excerpts still work.</span>
    <button class="text-button" @click="$emit('retrySummary', summary)">Retry memory summary</button>
  </div>
</template>
