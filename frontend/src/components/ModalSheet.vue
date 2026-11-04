<script setup>
import { inject, onMounted, onUnmounted, ref, useId } from 'vue'
import AppIcon from './AppIcon.vue'
import SoundToggle from './SoundToggle.vue'
defineProps({ title: { type: String, required: true }, emergency: Boolean })
const emit = defineEmits(['close', 'emergency'])
const dialog = ref(null)
const titleId = useId()
const soundAnchor = inject('appSoundAnchor', ref(null))
const modalCount = inject('appModalCount', ref(0))
const soundPosition = ref({})
let previousFocus
function positionSoundControl() {
  const rect = soundAnchor.value?.getBoundingClientRect()
  if (rect) soundPosition.value = { left: `${rect.left}px`, top: `${rect.top}px`, width: `${rect.width}px`, height: `${rect.height}px` }
}
onMounted(() => {
  previousFocus = document.activeElement
  positionSoundControl()
  modalCount.value++
  dialog.value.showModal()
  window.addEventListener('resize', positionSoundControl)
})
onUnmounted(() => {
  window.removeEventListener('resize', positionSoundControl)
  modalCount.value--
  previousFocus?.focus?.()
})
</script>
<template>
  <dialog ref="dialog" class="modal-sheet" :aria-labelledby="titleId" @cancel.prevent="emit('close')" @click="event => { if (event.target === dialog) emit('close') }">
    <div class="modal-top"><button v-if="!emergency" class="emergency-button" @click="emit('emergency')"><AppIcon name="plus" /> Emergency</button><button class="icon-button" aria-label="Close panel" @click="emit('close')"><AppIcon name="close" /></button></div>
    <h2 :id="titleId">{{ title }}</h2><slot /><button class="button secondary full-width" @click="emit('close')">Return to {{ emergency ? 'what I was doing' : 'app' }}</button>
    <SoundToggle class="dialog-sound-control" :style="soundPosition" />
  </dialog>
</template>
