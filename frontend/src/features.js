// Each feature owns its routes, state, requests, styles, and tests. Empty is valid.
export function useFeatures(context) {
  const modules = import.meta.glob('./features/*/index.js', { eager: true })
  return Object.values(modules).map(module => module.createFeature(context))
}
