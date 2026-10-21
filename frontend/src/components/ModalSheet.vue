<script setup>
import { onMounted, onUnmounted, ref, useId } from 'vue'
import AppIcon from './AppIcon.vue'
defineProps({ title: { type: String, required: true }, emergency: Boolean })
const emit = defineEmits(['close', 'emergency'])
const dialog = ref(null)
const titleId = useId()
let previousFocus
onMounted(() => { previousFocus = document.activeElement; dialog.value.showModal() })
onUnmounted(() => { previousFocus?.focus?.() })
</script>
<template>
  <dialog ref="dialog" class="modal-sheet" :aria-labelledby="titleId" @cancel.prevent="emit('close')" @click="event => { if (event.target === dialog) emit('close') }">
    <div class="modal-top"><button v-if="!emergency" class="emergency-button" @click="emit('emergency')"><AppIcon name="plus" /> Emergency</button><button class="icon-button" aria-label="Close panel" @click="emit('close')"><AppIcon name="close" /></button></div>
    <h2 :id="titleId">{{ title }}</h2><slot /><button class="button secondary full-width" @click="emit('close')">Return to {{ emergency ? 'what I was doing' : 'app' }}</button>
  </dialog>
</template>
