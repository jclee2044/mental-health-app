<script setup>defineProps({ title: { type: String, required: true } }); defineEmits(['navigate'])</script>
<template><section class="narrow-page page-enter"><h1>{{ title }}</h1><p>This activity isn’t included in this version yet.</p><button class="button secondary" @click="$emit('navigate','home')">Return home</button></section></template>
