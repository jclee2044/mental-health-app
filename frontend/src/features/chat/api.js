import { request } from '../../api/client.js'

export const transcribeRecording = (audio, mime_type, options = {}) => request('/chat/transcriptions', { ...options, method: 'POST', body: { audio, mime_type }, timeoutMs: 25000 })
export const saveVoiceTurn = (conversationId, turnId, body) => request(`/chat/conversations/${conversationId}/voice-turns/${turnId}`, { method: 'PUT', body })

export const getVoiceConfig = options => request('/voice/config', options)
export const createVoiceSession = (sdp, history = [], options = {}) => request('/voice/sessions', { ...options, method: 'POST', body: { sdp, history }, timeoutMs: 15000 })
export const endVoiceSession = (id) => {
  if (typeof id !== 'string' || !/^[A-Za-z0-9_-]{1,128}$/.test(id)) throw new Error('Invalid voice session identifier')
  return request(`/voice/sessions/${id}/end`, { method: 'POST', body: {}, timeoutMs: 5000, keepalive: true })
}
export const sendTextMessage = (message, history, options = {}) => request('/chat/messages', { ...options, method: 'POST', body: { message, history }, timeoutMs: 15000 })
export const saveChatTurn = (conversationId, turnId, body) => request(`/chat/conversations/${conversationId}/turns/${turnId}`, { method: 'PUT', body })
export const listConversations = options => request('/chat/conversations', options)
export const getConversation = (id, options) => request(`/chat/conversations/${id}`, options)
export const deleteConversation = id => request(`/chat/conversations/${id}`, { method: 'DELETE' })
