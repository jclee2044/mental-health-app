import { computed, ref, watch } from 'vue'

export function usePreferences() {
  let saved = {}
  try { saved = JSON.parse(localStorage.getItem('still.preferences') || '{}') || {} } catch { /* Memory-only preferences remain usable when storage is unavailable. */ }
  // Keep the existing storage key and saved choices across the rebrand.
  // Soft surface colors are the actual Home/card/wave color, also shown in
  // Appearance. A darker companion keeps headings and controls readable.
  const accents = [
    { name: 'Violet', value: '#70518e', surface: '#eee5f5' },
    { name: 'Rose', value: '#914b69', surface: '#f4dfe6' },
    { name: 'Peach', value: '#854e49', surface: '#f7e2cf' },
    { name: 'Amber', value: '#79581d', surface: '#f5edcf' },
    { name: 'Light brown', value: '#76583f', surface: '#e9dfd3' },
    { name: 'Sage', value: '#52654a', surface: '#e9edd5' },
    { name: 'Forest', value: '#355c4c', surface: '#dcebe4' },
    { name: 'Ocean', value: '#3d607d', surface: '#e2edf5' },
  ]
  // Preserve old preferences using the nearest remaining theme.
  const savedAccent = ({
    '#6134be': '#70518e',
    '#505e70': '#3d607d',
    '#455f7d': '#3d607d',
    '#28665f': '#355c4c',
  })[saved.accent] || saved.accent
  const accent = ref(accents.some(color => color.value === savedAccent) ? savedAccent : accents[0].value)
  const themeColor = computed(() => accents.find(color => color.value === accent.value)?.surface || accents[0].surface)
  const largeText = ref(saved.largeText === true)
  const reducedMotion = ref(saved.reducedMotion ?? matchMedia('(prefers-reduced-motion: reduce)').matches)
  watch([accent, largeText, reducedMotion], () => {
    try { localStorage.setItem('still.preferences', JSON.stringify({ accent: accent.value, largeText: largeText.value, reducedMotion: reducedMotion.value })) } catch { /* Storage is optional for appearance. */ }
  })
  return { accent, themeColor, largeText, reducedMotion, accents }
}
