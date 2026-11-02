<script setup>
import { inject, ref } from 'vue'
import AppIcon from './AppIcon.vue'
const soundEnabled = inject('appSoundEnabled', ref(true))
</script>
<template>
  <button class="app-sound-control" type="button" :aria-label="soundEnabled ? 'Mute all app sounds' : 'Enable app sounds'" :title="soundEnabled ? 'Mute all app sounds' : 'Enable app sounds'" :aria-pressed="soundEnabled" @click="soundEnabled = !soundEnabled"><AppIcon :name="soundEnabled ? 'sound' : 'mute'" /><span>Sound {{ soundEnabled ? 'on' : 'off' }}</span></button>
</template>
