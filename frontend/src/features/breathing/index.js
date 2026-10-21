import BreathingView from './BreathingView.vue'
import SessionHistoryView from './SessionHistoryView.vue'
import SessionSaveNotice from './SessionSaveNotice.vue'
import { useSessionRecords } from './useSessionRecords.js'
import './styles.css'

export function createFeature({ navigate, interrupted, reducedMotion }) {
  const sessions = useSessionRecords()
  return {
    id: 'breathing',
    routes: { breathing: BreathingView, sessions: SessionHistoryView },
    props: route => route === 'breathing' ? { interrupted: interrupted(), reducedMotion: reducedMotion() } : {},
    events: { navigate, record: sessions.queue, start: sessions.clearSaved },
    notice: { component: SessionSaveNotice, props: () => ({ records: sessions.records.value }), events: { retry: sessions.retry } },
  }
}
