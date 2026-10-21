<script setup>
defineProps({ records: { type: Array, required: true } })
defineEmits(['retry'])
</script>
<template><div v-for="record in records.filter(item => item.state === 'failed' || item === records.at(-1))" :key="record.id" class="session-notice" :class="{'error-banner':record.state==='failed'}" role="status"><span>{{ record.state === 'saving' ? 'Saving breathing session…' : record.message }}</span><button v-if="record.state === 'failed'" class="text-button" @click="$emit('retry',record)">Retry session save</button></div></template>
