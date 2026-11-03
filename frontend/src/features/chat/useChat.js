import { ref, watch } from 'vue'
import * as requests from './api.js'
import { VoiceSession } from './voice.js'
import { Dictation } from './dictation.js'
import { appendCaption, conversationHistory, voiceTranscriptBatches } from './domain.js'
import { useConversationRecords } from './useConversationRecords.js'
import { usePersonalMemory } from './usePersonalMemory.js'

export function useChat({ getAudio, api = requests, environment, dictationEnvironment, records = useConversationRecords({ api }) } = {}) {
  const messages = ref([]), draft = ref(''), textBusy = ref(false), textError = ref('')
  const voiceState = ref(null)
  let draftRevision = 0
  const stopDraftWatch = watch(draft, () => { draftRevision++ }, { flush: 'sync' })
  let active = true, sequence = 0, textController = null
  const conversationId = crypto.randomUUID()
  const personalMemory = usePersonalMemory({ api, conversationId, interrupt: () => {
    dictation.stop(); voice.stop('Voice stopped for memory controls. Start Voice again to use updated context.', true)
    textController?.abort()
  } })
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
    getPersonalMemory: personalMemory.scope,
    onPersonalMemory: personalMemory.acceptReport,
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
    // Hand off to the bubble synchronously, before any request or model delay.
    draft.value = ''
    const submittedRevision = draftRevision
    textController = new AbortController()
    try {
      const scope = personalMemory.scope()
      const result = await api.sendTextMessage(text, history, { signal: textController.signal, ...(scope ? { personalMemory: scope } : {}) })
      if (!active) return
      if (textController.signal.aborted) throw new Error('Request interrupted')
      if (typeof result?.reply !== 'string' || !result.reply.trim() || new TextEncoder().encode(result.reply).length > 8000) throw new Error('Invalid reply')
      user.status = 'complete'
      personalMemory.acceptReport(result.personal_memory)
      messages.value.push({ id: `text-${++sequence}`, role: 'assistant', source: 'text', text: result.reply, status: 'complete' })
      // Storage retry never repeats the provider call.
      records.queue({ conversationId, turnId: crypto.randomUUID(), body: { position: position++, user: text, assistant: result.reply } })
    } catch {
      if (active) {
        user.status = 'failed'
        if (draftRevision === submittedRevision) draft.value = text
        textError.value = draft.value === text
          ? 'The reply could not be completed. Your message is back in the draft; you can send it again.'
          : 'The reply could not be completed. Your new draft is unchanged. You can restore the failed message once the draft is empty.'
      }
    } finally { if (active) textBusy.value = false }
  }
  function restoreDraft(message) {
    if (active && !textBusy.value && !draft.value && message.status === 'failed') draft.value = message.text
  }
  function dispose() {
    if (!active) return
    const summarize = personalMemory.loaded.value && personalMemory.preferences.value.conversations
    active = false; textController?.abort(); stopDraftWatch(); personalMemory.dispose(); dictation.dispose(); voice.dispose(); saveVoice()
    // Feature-owned queue survives navigation. Never wait here for a model task.
    records.finishConversation?.(conversationId, { summarize })
    messages.value = []; draft.value = ''
  }
  return { messages, draft, textBusy, textError, voiceState, voice, dictation, dictationState, personalMemory, send, restoreDraft, dispose }
}
