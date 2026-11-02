<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import AppIcon from './components/AppIcon.vue'
import ModalSheet from './components/ModalSheet.vue'
import BrandWordmark from './components/BrandWordmark.vue'
import ThemeBackdrop from './components/ThemeBackdrop.vue'
import HomeView from './views/HomeView.vue'
import ChatView from './views/ChatView.vue'
import FeaturePendingView from './views/FeaturePendingView.vue'
import { usePreferences } from './composables/usePreferences.js'
import { useFeatures } from './features.js'
import { registerPwa } from './pwa.js'

const routes = ['home', 'emotion', 'history', 'breathing', 'sessions', 'chat', 'conversations']
const readRoute = () => routes.includes(location.hash.slice(1)) ? location.hash.slice(1) : 'home'
const screen = ref(readRoute())
const splash = ref(!location.hash && !matchMedia('(prefers-reduced-motion: reduce)').matches)
const sheet = ref(null)
const main = ref(null)
const preferences = usePreferences()
const features = useFeatures({ navigate: go, interrupted: () => Boolean(sheet.value), reducedMotion: () => preferences.reducedMotion.value })
const activeFeature = computed(() => features.find(feature => feature.routes[screen.value]))
const title = computed(() => ({ home: 'Home', emotion: 'Emotion log', history: 'Past logs', breathing: 'Guided breathing', sessions: 'Past breathing sessions', chat: 'Support chat', conversations: 'Saved chats' })[screen.value])
let splashTimer
function go(destination) {
  splash.value = false
  if (screen.value === destination) return
  location.hash = destination
}
function routeChanged() { screen.value = readRoute(); features.forEach(feature => feature.onNavigate?.(screen.value)) }
function openEmergency() { sheet.value = 'emergency' }
function focusMain() {
  main.value?.focus({ preventScroll: true })
  window.scrollTo(0, 0)
}
watch(screen, async () => { await nextTick(); focusMain() })
onMounted(() => {
  registerPwa(() => {})
  window.addEventListener('hashchange', routeChanged)
  splashTimer = setTimeout(() => { splash.value = false }, 900)
})
onUnmounted(() => { clearTimeout(splashTimer); window.removeEventListener('hashchange', routeChanged) })
</script>

<template>
  <div class="app" :class="{ 'large-text': preferences.largeText.value, 'reduce-motion': preferences.reducedMotion.value }" :style="{ '--accent': preferences.accent.value, '--theme-color': preferences.themeColor.value }">
    <ThemeBackdrop />
    <a class="skip-link" href="#main-content" @click.prevent="focusMain">Skip to content</a>
    <header class="site-header">
      <button class="brand" aria-label="inspire home" @click="go('home')"><BrandWordmark /></button>
      <button class="emergency-button" @click="openEmergency"><AppIcon name="plus" /> Emergency</button>
    </header>
    <main id="main-content" ref="main" tabindex="-1" :aria-label="title">
      <section v-if="splash" class="splash page-enter">
        <div class="splash-wordmark"><BrandWordmark /></div><h1>A moment for yourself.</h1>
        <button class="text-button" @click="splash = false">Skip introduction <span aria-hidden="true">→</span></button>
      </section>
      <template v-else>
        <HomeView v-if="screen === 'home'" @navigate="go" />
        <component :is="activeFeature.routes[screen]" v-else-if="activeFeature" v-bind="activeFeature.props(screen)" v-on="activeFeature.events" @emergency="openEmergency" />
        <ChatView v-else-if="screen === 'chat'" @end="go('home')" />
        <FeaturePendingView v-else :title="title" />
        <template v-for="feature in features" :key="feature.id"><component :is="feature.notice.component" v-if="feature.notice" v-bind="feature.notice.props()" v-on="feature.notice.events" /></template>
      </template>
    </main>
    <footer class="site-footer">
      <p class="prototype-note">Localhost coursework prototype. No therapy, diagnosis, crisis response or monitoring.</p>
      <nav aria-label="Secondary navigation">
        <button @click="sheet = 'appearance'"><AppIcon name="sliders" /> Appearance</button>
      </nav>
    </footer>
    <ModalSheet v-if="sheet" :title="sheet === 'emergency' ? 'Emergency & crisis support' : 'Make it yours'" :emergency="sheet === 'emergency'" @close="sheet = null" @emergency="openEmergency">
      <template v-if="sheet === 'emergency'">
        <p>United States resources. These services are separate from inspire.</p>
        <a class="resource-card" href="tel:988"><span class="resource-number">988</span><span><strong>Crisis counseling</strong><span>Suicide & Crisis Lifeline</span></span><AppIcon name="arrow-up-right" /></a>
        <a class="resource-card" href="tel:911"><span class="resource-number">911</span><span><strong>Emergency services</strong><span>For immediate danger or a medical emergency</span></span><AppIcon name="arrow-up-right" /></a>
        <p class="small muted">Opening this panel does not contact anyone.</p>
      </template>
      <template v-else>
        <p>Choose what feels comfortable. You can change this any time.</p>
        <fieldset><legend>Theme color</legend><div class="swatches"><button v-for="color in preferences.accents" :key="color.value" :style="{ '--swatch': color.surface, '--swatch-ink': color.value }" class="swatch theme-swatch" :title="color.name" :aria-label="color.name" :aria-pressed="preferences.accent.value === color.value" @click="preferences.accent.value = color.value"><AppIcon v-if="preferences.accent.value === color.value" name="check" /></button></div></fieldset>
        <label class="toggle-row"><span><strong>Larger text</strong><span>A little more room to read</span></span><input v-model="preferences.largeText.value" type="checkbox"></label>
        <label class="toggle-row"><span><strong>Reduced motion</strong><span>Use still cues instead of animation</span></span><input v-model="preferences.reducedMotion.value" type="checkbox"></label>
      </template>

    </ModalSheet>
  </div>
</template>
