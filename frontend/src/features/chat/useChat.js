import { ref } from 'vue'
import * as requests from './api.js'
import { VoiceSession } from './voice.js'
import { Dictation } from './dictation.js'
import { appendCaption, conversationHistory, voiceTranscriptBatches } from './domain.js'
import { useConversationRecords } from './useConversationRecords.js'

export function useChat({ getAudio, api = requests, environment, dictationEnvironment, records = useConversationRecords({ api }) } = {}) {
  const messages = ref([]), draft = ref(''), textBusy = ref(false), textError = ref('')
  const voiceState = ref(null)
  let active = true, sequence = 0, textController = null
  const conversationId = crypto.randomUUID()
  records.clearSaved()
  let position = 0
  const queuedVoice = new Set()
  function saveVoice() {
    const unsaved = messages.value.filter(message => message.source === 'voice' && !queuedVoice.has(message.id ?? message))
    const batches = voiceTranscriptBatches(unsaved)
    unsaved.forEach(message => queuedVoice.add(message.id ?? message))
    for (const batch of batches) records.queue({ kind: 'voice', conversationId, turnId: crypto.randomUUID(), body: { position: position++, messages: batch } })
  }
  const voice = new VoiceSession({ api, getAudio, environment,
    getHistory: () => conversationHistory(messages.value),
    onChange: state => {
      voiceState.value = state
      if (state.status === 'permission') dictation.stop()
      if (['closed', 'error'].includes(state.status)) saveVoice()
    },
    onTranscript: fragment => { if (active) appendCaption(messages.value, fragment) },
  })
  voiceState.value = { ...voice.state }
  const dictationState = ref({ status: 'idle', message: '' })
  const dictation = new Dictation({ environment: dictationEnvironment,
    transcribe: (audio, mime, options) => api.transcribeRecording(audio, mime, options),
    onChange: state => { dictationState.value = state },
    appendText: text => {
      if (!active) return false
      const next = `${draft.value}${draft.value && !/\s$/.test(draft.value) ? ' ' : ''}${text}`
      if (next.length > 4000 || new TextEncoder().encode(next).length > 8000) return false
      draft.value = next
      return true
    },
  })
  async function send() {
    dictation.stop()
    const text = draft.value.trim()
    if (!active || textBusy.value || !text) return
    if (position >= 100) { textError.value = 'This conversation has reached its save limit. End chat to start a new one.'; return }
    if (new TextEncoder().encode(text).length > 8000) { textError.value = 'Please shorten your message.'; return }
    voice.stop('Switched to text. Microphone off. Select the microphone to speak again.', true)
    saveVoice()
    const history = conversationHistory(messages.value)
    const user = { id: `text-${++sequence}`, role: 'user', source: 'text', text, status: 'pending' }
    messages.value.push(user); textBusy.value = true; textError.value = ''
    textController = new AbortController()
    try {
      const result = await api.sendTextMessage(text, history, { signal: textController.signal })
      if (!active) return
      if (typeof result?.reply !== 'string' || !result.reply.trim() || new TextEncoder().encode(result.reply).length > 8000) throw new Error('Invalid reply')
      user.status = 'complete'
      messages.value.push({ id: `text-${++sequence}`, role: 'assistant', source: 'text', text: result.reply, status: 'complete' })
      // Storage retry never repeats the provider call.
      records.queue({ conversationId, turnId: crypto.randomUUID(), body: { position: position++, user: text, assistant: result.reply } })
      if (draft.value.trim() === text) draft.value = ''
    } catch {
      if (active) { user.status = 'failed'; textError.value = 'The reply could not be completed. Your draft is still here; you can send it again.' }
    } finally { if (active) textBusy.value = false }
  }
  function dispose() { active = false; textController?.abort(); dictation.dispose(); voice.dispose(); saveVoice(); messages.value = []; draft.value = '' }
  return { messages, draft, textBusy, textError, voiceState, voice, dictation, dictationState, send, dispose }
}
