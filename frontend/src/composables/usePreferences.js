import { ref, watch } from 'vue'

export function usePreferences() {
  let saved = {}
  try { saved = JSON.parse(localStorage.getItem('still.preferences') || '{}') || {} } catch { /* Memory-only preferences remain usable when storage is unavailable. */ }
  // Keep the existing storage key and saved choices across the rebrand.
  const accents = [{ name: 'Violet', value: '#70518e' }, { name: 'Forest', value: '#355c4c' }, { name: 'Clay', value: '#854e49' }, { name: 'Ocean', value: '#3d607d' }]
  // Follow the refreshed Violet palette without resetting other personal choices.
  const savedAccent = saved.accent === '#6134be' ? accents[0].value : saved.accent
  const accent = ref(accents.some(color => color.value === savedAccent) ? savedAccent : accents[0].value)
  const largeText = ref(saved.largeText === true)
  const reducedMotion = ref(saved.reducedMotion ?? matchMedia('(prefers-reduced-motion: reduce)').matches)
  watch([accent, largeText, reducedMotion], () => {
    try { localStorage.setItem('still.preferences', JSON.stringify({ accent: accent.value, largeText: largeText.value, reducedMotion: reducedMotion.value })) } catch { /* Storage is optional for appearance. */ }
  })
  return { accent, largeText, reducedMotion, accents }
}
