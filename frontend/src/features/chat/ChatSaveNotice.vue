<script setup>
defineProps({ records: { type: Array, required: true } })
defineEmits(['retry'])
</script>
<template>
  <div v-for="record in records.filter(item => item.state !== 'saved' || item === records.at(-1))" :key="record.turnId" class="chat-save-notice" :class="{ 'chat-storage-error': record.state === 'failed' }" role="status">
    <span>{{ record.state === 'saved' ? 'Chat saved.' : record.state === 'failed' ? 'Chat not saved. Retry before reloading or closing the app.' : 'Saving chat…' }}</span>
    <button v-if="record.state === 'failed'" class="text-button" @click="$emit('retry', record)">Retry chat save</button>
  </div>
</template>
