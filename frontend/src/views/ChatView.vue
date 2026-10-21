<script setup>
import AppIcon from '../components/AppIcon.vue'
defineEmits(['end'])
</script>
<template><section class="narrow-page page-enter"><p class="eyebrow">A space to talk</p><h1>Support chat</h1><div class="empty-state"><span class="empty-icon"><AppIcon name="chat" /></span><h2>A little more time.</h2><p>Conversation is coming in a later update.<br>Messages aren’t being sent or saved.</p></div><label for="chat-draft">Message</label><textarea id="chat-draft" disabled placeholder="Chat isn’t connected yet" rows="3"></textarea><div class="button-row"><button class="button secondary" @click="$emit('end')">End chat</button><button class="button" disabled>Send</button></div></section></template>
