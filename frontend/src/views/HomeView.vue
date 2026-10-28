<script setup>
import AppIcon from '../components/AppIcon.vue'
defineEmits(['navigate'])
const activities = [
  { route: 'emotion', icon: 'smile', title: 'Emotion log', description: 'A color, a feeling, a moment to notice.', class: 'activity-lilac' },
  { route: 'breathing', icon: 'wind', title: 'Guided breathing', description: 'Follow a gentle rhythm. In, then out.', class: 'activity-sage' },
  { route: 'chat', icon: 'chat', title: 'Support chat', description: 'A space for conversation.', class: 'activity-peach' },
]
</script>
<template>
  <section class="home-layout page-enter">
    <div class="home-content">
      <h1>How would you like to <em>begin?</em></h1>
      <p class="intro">Choose the one that feels right for you right now.</p>
      <div class="activity-list"><button v-for="activity in activities" :key="activity.route" class="activity-card" :class="activity.class" @click="$emit('navigate', activity.route)"><span class="activity-icon"><AppIcon :name="activity.icon" /></span><span class="activity-copy"><strong>{{ activity.title }}</strong><span>{{ activity.description }}</span></span><AppIcon name="arrow-right" /></button></div>
    </div>
    <aside class="home-art" aria-label="A quiet reminder">
      <svg class="art-waves" viewBox="0 0 500 640" preserveAspectRatio="none" aria-hidden="true"><path fill="var(--lavender)" d="M190 0H500V355C360 310 402 156 256 114C209 100 193 45 190 0Z" /><path fill="var(--lilac)" d="M0 185C155 206 90 329 275 361C378 379 359 468 500 494V640H0Z" /><path fill="var(--lavender)" d="M0 465C106 392 162 535 283 538C376 540 412 492 500 522V640H0Z" /></svg>
      <div class="art-sun"><AppIcon name="wind" /></div>
      <div class="art-caption"><p>One thing<br>at a time.</p><span>There’s room to simply be.</span></div>
    </aside>
  </section>
</template>
