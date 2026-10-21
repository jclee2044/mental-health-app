<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import AppIcon from './components/AppIcon.vue'
import ModalSheet from './components/ModalSheet.vue'
import HomeView from './views/HomeView.vue'
import ChatView from './views/ChatView.vue'
import FeaturePendingView from './views/FeaturePendingView.vue'
import { usePreferences } from './composables/usePreferences.js'
import { useFeatures } from './features.js'
import { registerPwa } from './pwa.js'

const routes = ['home', 'emotion', 'history', 'breathing', 'sessions', 'chat']
const readRoute = () => routes.includes(location.hash.slice(1)) ? location.hash.slice(1) : 'home'
const screen = ref(readRoute())
const splash = ref(!location.hash && !matchMedia('(prefers-reduced-motion: reduce)').matches)
const sheet = ref(null)
const main = ref(null)
const preferences = usePreferences()
const offlineStatus = ref('Preparing offline mode…')
const features = useFeatures({ navigate: go, interrupted: () => Boolean(sheet.value), reducedMotion: () => preferences.reducedMotion.value })
const activeFeature = computed(() => features.find(feature => feature.routes[screen.value]))
const title = computed(() => ({ home: 'Home', emotion: 'Emotion log', history: 'Past logs', breathing: 'Guided breathing', sessions: 'Past breathing sessions', chat: 'Support chat' })[screen.value])
let splashTimer
function go(destination) {
  splash.value = false
  if (screen.value === destination) return
  location.hash = destination
}
function routeChanged() { screen.value = readRoute(); features.forEach(feature => feature.onNavigate?.(screen.value)) }
function openEmergency() { sheet.value = 'emergency' }
watch(screen, async () => { await nextTick(); main.value?.focus() })
onMounted(() => {
  registerPwa(status => { offlineStatus.value = status })
  window.addEventListener('hashchange', routeChanged)
  splashTimer = setTimeout(() => { splash.value = false }, 900)
})
onUnmounted(() => { clearTimeout(splashTimer); window.removeEventListener('hashchange', routeChanged) })
</script>

<template>
  <div class="app" :class="{ 'large-text': preferences.largeText.value, 'reduce-motion': preferences.reducedMotion.value }" :style="{ '--accent': preferences.accent.value }">
    <a class="skip-link" href="#main-content" @click.prevent="main?.focus()">Skip to content</a>
    <header class="site-header">
      <button class="brand" aria-label="Still home" @click="go('home')"><AppIcon name="leaf" /><span>still<span class="brand-dot">.</span></span></button>
      <span class="header-caption">A little space for yourself</span>
      <button class="emergency-button" @click="openEmergency"><AppIcon name="plus" /> Emergency</button>
    </header>
    <main id="main-content" ref="main" tabindex="-1" :aria-label="title">
      <section v-if="splash" class="splash page-enter">
        <div class="splash-mark"><AppIcon name="leaf" /></div><h1>A moment of still.</h1>
        <button class="text-button" @click="splash = false">Skip introduction <span aria-hidden="true">→</span></button>
      </section>
      <template v-else>
        <div v-if="screen !== 'home'" class="page-top"><button class="text-button" @click="go('home')"><AppIcon name="arrow-left" /> Home</button><span class="eyebrow">{{ title }}</span></div>
        <HomeView v-if="screen === 'home'" @navigate="go" />
        <ChatView v-else-if="screen === 'chat'" @end="go('home')" />
        <component :is="activeFeature.routes[screen]" v-else-if="activeFeature" v-bind="activeFeature.props(screen)" v-on="activeFeature.events" @emergency="openEmergency" />
        <FeaturePendingView v-else :title="title" @navigate="go" />
        <template v-for="feature in features" :key="feature.id"><component :is="feature.notice.component" v-if="feature.notice" v-bind="feature.notice.props()" v-on="feature.notice.events" /></template>
      </template>
    </main>
    <footer class="site-footer">
      <span class="footer-wordmark">Make room for a moment.</span>
      <nav aria-label="Secondary navigation">
        <button @click="go('history')"><AppIcon name="calendar" /> Past logs</button>
        <button @click="sheet = 'appearance'"><AppIcon name="sliders" /> Appearance</button>
        <button @click="sheet = 'about'">About</button>
      </nav>
    </footer>
    <ModalSheet v-if="sheet" :title="sheet === 'emergency' ? 'Emergency & crisis support' : sheet === 'appearance' ? 'Make it yours' : 'About Still'" :emergency="sheet === 'emergency'" @close="sheet = null" @emergency="openEmergency">
      <template v-if="sheet === 'emergency'">
        <p>United States resources. These services are separate from Still.</p>
        <a class="resource-card" href="tel:988"><span class="resource-number">988</span><span><strong>Crisis counseling</strong><span>Suicide & Crisis Lifeline</span></span><AppIcon name="arrow-up-right" /></a>
        <a class="resource-card" href="tel:911"><span class="resource-number">911</span><span><strong>Emergency services</strong><span>For immediate danger or a medical emergency</span></span><AppIcon name="arrow-up-right" /></a>
        <p class="small muted">Opening this panel does not contact anyone.</p>
      </template>
      <template v-else-if="sheet === 'appearance'">
        <p>Choose what feels comfortable. You can change this any time.</p>
        <fieldset><legend>Accent color</legend><div class="swatches"><button v-for="color in preferences.accents" :key="color.value" :style="{ '--swatch': color.value }" class="swatch" :aria-label="color.name" :aria-pressed="preferences.accent.value === color.value" @click="preferences.accent.value = color.value"><AppIcon v-if="preferences.accent.value === color.value" name="check" /></button></div></fieldset>
        <label class="toggle-row"><span><strong>Larger text</strong><span>A little more room to read</span></span><input v-model="preferences.largeText.value" type="checkbox"></label>
        <label class="toggle-row"><span><strong>Reduced motion</strong><span>Use still cues instead of animation</span></span><input v-model="preferences.reducedMotion.value" type="checkbox"></label>
      </template>
      <template v-else>
        <p>Still is a coursework skills prototype running on localhost. It does not provide therapy, diagnosis, crisis response, or monitoring.</p>
        <p>Available activities depend on this version. Support chat is not connected.</p>
        <p class="small" role="status">{{ offlineStatus }}</p>
      </template>
    </ModalSheet>
  </div>
</template>
