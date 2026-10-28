<script setup>
defineProps({ name: { type: String, required: true } })
const paths = {
  leaf: 'M19 4C8 2 3 8 6 14c3 6 12 5 13-10ZM5 21c0-7 5-11 9-13',
  plus: 'M12 5v14M5 12h14',
  'arrow-left': 'm12 5-7 7 7 7M5 12h14',
  'arrow-right': 'm12 5 7 7-7 7M5 12h14',
  'arrow-up-right': 'M6 18 18 6M6 6h12v12',
  calendar: 'M5 5h14v15H5zM8 3v4m8-4v4M5 10h14M8 14h2m4 0h2m-8 3h2',
  sliders: 'M4 7h6m4 0h6M4 17h10m4 0h2M10 4v6m4 4v6',
  check: 'm5 12 4 4L19 6',
  close: 'm6 6 12 12M6 18 18 6',
  smile: 'M8 9h.01M16 9h.01M7 14q5 6 10 0M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20',
  wind: 'M3 8h12a3 3 0 1 0-3-3M3 12h15a3 3 0 1 1-3 3M3 16h5a3 3 0 1 1-3 3',
  chat: 'M5 5h14v11H9l-4 4zM9 9h6m-6 3h4',
  microphone: 'M9 5a3 3 0 0 1 6 0v7a3 3 0 0 1-6 0zM6 10v2a6 6 0 0 0 12 0v-2M12 18v4m-4 0h8',
  sound: 'M11 5 6 9H3v6h3l5 4zM15 8q5 4 0 8M18 5q8 7 0 14',
  mute: 'M11 5 6 9H3v6h3l5 4zM16 9l5 6m0-6-5 6',
  pause: 'M8 5v14m8-14v14',
  play: 'm8 4 12 8-12 8z',
}
</script>
<template><svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path :d="paths[name] || paths.leaf" /></svg></template>
