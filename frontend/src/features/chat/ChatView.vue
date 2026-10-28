<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import AppIcon from '../../components/AppIcon.vue'
import { useChat } from './useChat.js'
import { bindVoiceLifecycle, interruptVoice } from './lifecycle.js'

const props = defineProps({ interrupted: Boolean, records: Object })
const emit = defineEmits(['navigate'])
const remoteAudio = ref(null)
const { messages, draft, textBusy, textError, voiceState, voice, dictation, dictationState, send, dispose } = useChat({ getAudio: () => remoteAudio.value, records: props.records })
const labels = { permission: 'Permission', connecting: 'Connecting', active: 'Active', muted: 'Muted', closing: 'Closing', closed: 'Closed', error: 'Error' }
const canStart = computed(() => ['closed', 'error'].includes(voiceState.value.status))
const canMute = computed(() => ['active', 'muted'].includes(voiceState.value.status))
const dictating = computed(() => ['starting', 'recording', 'transcribing'].includes(dictationState.value.status))
const dictationLabel = computed(() => dictationState.value.status === 'recording' ? 'Transcribe recording' : dictating.value ? 'Cancel dictation' : 'Dictate message')
const conversationStarted = ref(false)
watch([() => messages.value.length, () => voiceState.value.status], ([count, status]) => {
  if (count || ['permission', 'connecting', 'active', 'muted', 'closing'].includes(status)) conversationStarted.value = true
}, { immediate: true })
function startVoice() { if (!props.interrupted && !textBusy.value) { dictation.stop(); voice.start() } }
function toggleDictation() {
  if (dictationState.value.status === 'recording') dictation.finish()
  else if (dictating.value) dictation.stop('Dictation cancelled. Your existing draft is unchanged.')
  else if (!props.interrupted && !textBusy.value && canStart.value) dictation.start()
}
function endChat() { dispose(); emit('navigate', 'home') }
let unbind = () => {}
const capture = {
  stop: (message, immediate) => { dictation.stop(); voice.stop(message, immediate) },
  dispose: () => { dictation.dispose(); voice.dispose() },
}
watch(() => props.interrupted, value => interruptVoice(capture, value), { flush: 'sync' })
onMounted(() => { unbind = bindVoiceLifecycle(capture, document, window) })
onBeforeUnmount(() => { unbind(); dispose() })
</script>

<template>
  <section class="chat-page narrow-page page-enter">
    <div class="chat-heading">
      <h1>What’s on your mind?</h1>
      <button class="chat-history-button" type="button" aria-label="View saved chats" title="View saved chats" @click="$emit('navigate', 'conversations')">
        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 10a9 9 0 1 1 2 8M3 4v6h6M12 7v5l3 2" /></svg>
      </button>
    </div>
    <audio ref="remoteAudio" autoplay playsinline hidden aria-hidden="true"></audio>
    <div class="chat-frame">
      <div class="chat-window" role="region" aria-label="Chat window" tabindex="0">
        <div v-if="!messages.length" class="empty-state">
          <span class="empty-icon"><AppIcon name="chat" /></span>
          <p>Your day, something weighing on you,<br />or a small win you’d like to share.</p>
        </div>
        <ol v-else class="chat-transcript" aria-label="Conversation" aria-live="polite" aria-relevant="additions text">
          <li v-for="message in messages" :key="message.id" class="chat-bubble" :class="`chat-${message.role}`">
            <span class="chat-speaker">{{ message.role === 'user' ? 'You' : 'Still' }}</span>
            <p>{{ message.text }}</p>
            <span v-if="message.status === 'pending'" class="chat-caption-note">Waiting for a reply…</span>
            <span v-else-if="message.status === 'failed'" class="chat-caption-note">Reply unavailable · draft kept</span>
          </li>
        </ol>
      </div>
      <form class="chat-composer" @submit.prevent="send">
        <label for="chat-message" class="chat-sr-only">Message</label>
        <div class="chat-input-box" :class="{ 'chat-input-voice-active': !canStart }">
          <textarea id="chat-message" v-model="draft" rows="2" maxlength="4000" placeholder="Write what’s on your mind…" @keydown.ctrl.enter.prevent="send" @keydown.meta.enter.prevent="send"></textarea>
          <div class="chat-input-toolbar">
            <div class="chat-controls">
              <template v-if="canStart">
                <button class="chat-dictation-button" type="button" :aria-label="dictationLabel" :title="dictationLabel" :aria-pressed="dictating" :disabled="textBusy || interrupted" @click="toggleDictation"><AppIcon :name="dictating ? 'check' : 'microphone'" /></button>
                <button class="chat-voice-button" type="button" aria-label="Voice mode" title="Voice mode" :disabled="textBusy || interrupted" @click="startVoice"><svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><path d="M5 10v4M10 5v14M15 8v8M20 10v4" /></svg><span class="chat-sr-only">Voice mode</span></button>
              </template>
              <template v-else>
                <button v-if="canMute" class="button secondary" type="button" :aria-label="voiceState.microphoneMuted ? 'Unmute microphone' : 'Mute microphone'" :aria-pressed="voiceState.microphoneMuted" @click="voice.toggleMute()"><AppIcon :name="voiceState.microphoneMuted ? 'mute' : 'microphone'" /> {{ voiceState.microphoneMuted ? 'Unmute' : 'Mute' }}</button>
                <button class="button secondary" type="button" :disabled="voiceState.status === 'closing'" @click="voice.stop()">{{ ['permission','connecting'].includes(voiceState.status) ? 'Cancel voice setup' : 'End voice' }}</button>
              </template>
              <button v-if="voiceState.playbackBlocked" class="button" type="button" @click="voice.enableAudio()">Enable assistant audio</button>
            </div>
          </div>
        </div>
        <p v-if="dictationState.message" class="small muted dictation-status" :role="dictationState.status === 'error' ? 'alert' : 'status'">{{ dictationState.message }}</p>
        <button v-if="dictating" class="text-button" type="button" @click="dictation.stop('Dictation cancelled. Your existing draft is unchanged.')">Cancel dictation</button>
        <p v-if="textError" class="chat-storage-error" role="alert">{{ textError }}</p>
        <div class="button-row"><button class="button" type="submit" :disabled="textBusy || !draft.trim()">{{ textBusy ? 'Waiting for reply…' : 'Send' }}<AppIcon name="arrow-right" /></button></div>
        <button v-if="conversationStarted" class="text-button chat-end" type="button" @click="endChat">End chat</button>
        <div class="voice-inline" :data-voice-state="voiceState.status">
          <p v-if="voiceState.status !== 'closed' || voiceState.message !== 'Microphone off.'" class="voice-status" :role="voiceState.status === 'error' ? 'alert' : 'status'"><strong>{{ labels[voiceState.status] }}</strong><span>{{ voiceState.message }}</span></p>
          <p v-if="canMute" class="small muted voice-disclosure">Mute affects only your microphone. Assistant playback, the provider session, and billing continue. Use End to close voice.</p>
          <p v-if="voiceState.playbackBlocked" class="small muted">Your browser blocked playback. Captions stay available.</p>
        </div>
      </form>
    </div>
    <p class="small muted chat-privacy">Uses OpenAI. Chats are saved on this device.</p>
    <p class="small muted chat-dictation-privacy">Dictation sends a short recording to OpenAI.</p>
    <details class="chat-privacy-details">
      <summary>Privacy &amp; saved chats</summary>
      <p>Select the microphone to record up to 30 seconds, then select it again to transcribe with OpenAI. You can cancel while preparing or transcribing. Leaving, Emergency, Send or switching to Voice mode cancels dictation. Recognized words go into your editable draft, not directly into chat. This app keeps recording audio in memory only and doesn’t save it. Cancelling an upload can’t guarantee cancellation of provider processing or charges.</p>
      <p>Voice sends microphone audio to OpenAI only after you select Voice mode and allow access. Recent messages and approximate captions provide context across text and voice. Sending text turns the microphone off; returning to voice is your choice.</p>
      <p>Saved chats remain until deleted and aren’t automatically reused as context. Spoken messages save as approximate text when voice ends or you leave chat; audio isn’t saved. Unsaved exchanges can be lost on reload or close. Local deletion doesn’t control OpenAI’s retention or training policies.</p>
    </details>
  </section>
</template>
