<script setup>
import AppIcon from '../components/AppIcon.vue'
defineEmits(['navigate'])
const activities = [
  { route: 'emotion', icon: 'smile', title: 'Emotion log', description: 'A color, a feeling, a moment to notice.', class: 'sage' },
  { route: 'breathing', icon: 'wind', title: 'Guided breathing', description: 'Follow a gentle rhythm. In, then out.', class: 'rose' },
  { route: 'chat', icon: 'chat', title: 'Support chat', description: 'A space for conversation.', class: 'blue' },
]
</script>
<template>
  <section class="home-layout page-enter">
    <div class="home-content">
      <h1>How would you like<br>to <em>begin?</em></h1>
      <p class="intro">There’s no right place to start.<br>Choose what feels useful right now.</p>
      <div class="activity-list"><button v-for="activity in activities" :key="activity.route" class="activity-card" :class="activity.class" @click="$emit('navigate', activity.route)"><span class="activity-icon"><AppIcon :name="activity.icon" /></span><span class="activity-copy"><strong>{{ activity.title }}</strong><span>{{ activity.description }}</span></span><AppIcon name="arrow-right" /></button></div>
      <p class="home-note">Take your time. You can stop or change direction whenever you like.</p>
    </div>
    <aside class="home-art" aria-label="A quiet reminder"><div class="art-orbit orbit-one"></div><div class="art-orbit orbit-two"></div><div class="art-sun"></div><div class="art-stem stem-one"></div><div class="art-stem stem-two"></div><div class="art-leaf leaf-one"></div><div class="art-leaf leaf-two"></div><div class="art-leaf leaf-three"></div><div class="art-caption"><p>One thing<br>at a time.</p><span>There’s room to simply be.</span></div></aside>
  </section>
</template>
