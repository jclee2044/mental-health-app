import { test } from 'node:test'
import assert from 'node:assert/strict'
import { effectScope, nextTick, ref } from 'vue'
import { usePreferences } from '../src/composables/usePreferences.js'
import { setupView } from './setupView.js'

test('sound preference survives reload, with safe defaults and storage failure fallback', async () => {
  const storageDescriptor = Object.getOwnPropertyDescriptor(globalThis, 'localStorage')
  const originalMatchMedia = globalThis.matchMedia
  let saved = '{}'
  Object.defineProperty(globalThis, 'localStorage', { configurable: true, writable: true, value: { getItem: () => saved, setItem: (_key, value) => { saved = value } } })
  globalThis.matchMedia = () => ({ matches: false })
  const scope = effectScope()
  try {
    const first = scope.run(usePreferences)
    assert.equal(first.soundEnabled.value, true)
    first.soundEnabled.value = false
    await nextTick()
    const reloaded = scope.run(usePreferences)
    assert.equal(reloaded.soundEnabled.value, false)
    reloaded.accent.value = '#355c4c'
    await nextTick()
    assert.equal(JSON.parse(saved).soundEnabled, false)
    globalThis.localStorage = { getItem() { throw new Error('Unavailable') }, setItem() { throw new Error('Unavailable') } }
    const fallback = scope.run(usePreferences)
    fallback.soundEnabled.value = false
    await nextTick()
    assert.equal(fallback.soundEnabled.value, false)
  } finally { scope.stop(); if (storageDescriptor) Object.defineProperty(globalThis, 'localStorage', storageDescriptor); else delete globalThis.localStorage; globalThis.matchMedia = originalMatchMedia }
})

test('footer and dialog controls use the same sound preference across remounts', async () => {
  const enabled = ref(false)
  const mount = () => setupView(new URL('../src/components/SoundToggle.vue', import.meta.url), [
    [/import AppIcon from [^\n]+/, 'const AppIcon = {}'],
  ], {}, () => {}, { appSoundEnabled: enabled })
  const footer = await mount()
  const dialog = await mount()
  try {
    assert.equal(footer.state.soundEnabled, enabled)
    assert.equal(dialog.state.soundEnabled, enabled)
    footer.state.soundEnabled.value = true
    assert.equal(dialog.state.soundEnabled.value, true)
    dialog.state.soundEnabled.value = false
    footer.unmount()
    const revisited = await mount()
    assert.equal(revisited.state.soundEnabled.value, false)
    revisited.unmount()
  } finally { dialog.unmount() }
})
