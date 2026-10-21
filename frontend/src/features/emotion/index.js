import { ref } from 'vue'
import EmotionView from './EmotionView.vue'
import HistoryView from './HistoryView.vue'
import './styles.css'

export function createFeature({ navigate }) {
  const editing = ref(null)
  return {
    id: 'emotion',
    routes: { emotion: EmotionView, history: HistoryView },
    props: route => route === 'emotion' ? { entry: editing.value } : {},
    events: {
      navigate(destination) { editing.value = null; navigate(destination) },
      edit(entry) { editing.value = entry; navigate('emotion') },
    },
    onNavigate(destination) { if (destination !== 'emotion') editing.value = null },
  }
}
