// Cache only the built application shell. Personal records always use the API.
export function registerPwa(onStatus) {
  if (!import.meta.env.PROD || !('serviceWorker' in navigator)) { onStatus('Offline mode is available in the production build.'); return }
  navigator.serviceWorker.register('/sw.js').then(() => navigator.serviceWorker.ready).then(() => {
    onStatus('Offline shell ready. Saving and history still need the local server.')
  }).catch(() => onStatus('Offline mode is unavailable. You can still use the app while the server is running.'))
}
