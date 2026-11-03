import { request } from '../../api/client.js'

export const transcribeRecording = (audio, mime_type, options = {}) => request('/chat/transcriptions', { ...options, method: 'POST', body: { audio, mime_type }, timeoutMs: 25000 })
export const saveVoiceTurn = (conversationId, turnId, body) => request(`/chat/conversations/${conversationId}/voice-turns/${turnId}`, { method: 'PUT', body })

export const getVoiceConfig = options => request('/voice/config', options)
export const createVoiceSession = (sdp, history = [], { personalMemory, ...options } = {}) => request('/voice/sessions', { ...options, method: 'POST', body: { sdp, history, ...(personalMemory ? { personal_memory: personalMemory } : {}) }, timeoutMs: 15000 })
export const endVoiceSession = (id) => {
  if (typeof id !== 'string' || !/^[A-Za-z0-9_-]{1,128}$/.test(id)) throw new Error('Invalid voice session identifier')
  return request(`/voice/sessions/${id}/end`, { method: 'POST', body: {}, timeoutMs: 5000, keepalive: true })
}
export const sendTextMessage = (message, history, { personalMemory, ...options } = {}) => request('/chat/messages', { ...options, method: 'POST', body: { message, history, ...(personalMemory ? { personal_memory: personalMemory } : {}) }, timeoutMs: 15000 })
export const saveChatTurn = (conversationId, turnId, body) => request(`/chat/conversations/${conversationId}/turns/${turnId}`, { method: 'PUT', body })
export const listConversations = options => request('/chat/conversations', options)
export const getConversation = (id, options) => request(`/chat/conversations/${id}`, options)
export const deleteConversation = id => request(`/chat/conversations/${id}`, { method: 'DELETE' })

export const generateConversationTitle = (id, options) => request(`/chat/conversations/${id}/title`, { ...options, method: 'POST', timeoutMs: 15000 })

export const getMemoryPreferences = options => request('/personal-memory/preferences', options)
export const setMemoryPreferences = (body, options) => request('/personal-memory/preferences', { ...options, method: 'PUT', body })
export const getMemoryFacts = options => request('/personal-memory/facts', options)
export const putMemoryFact = (id, body, options) => request(`/personal-memory/facts/${id}`, { ...options, method: 'PUT', body })
export const deleteMemoryFact = (id, options) => request(`/personal-memory/facts/${id}`, { ...options, method: 'DELETE' })
export const getMemoryExclusions = options => request('/personal-memory/exclusions', options)
export const excludeMemorySource = (body, options) => request('/personal-memory/exclusions', { ...options, method: 'PUT', body })
export const restoreMemorySource = (kind, id, options) => request(`/personal-memory/exclusions/${kind}/${id}`, { ...options, method: 'DELETE' })
export const previewMemory = (body, options) => request('/personal-memory/preview', { ...options, method: 'POST', body })
export const getMemorySource = (kind, id, options) => request(`/personal-memory/sources/${kind}/${id}`, options)
export const generateMemorySummary = (id, retry = false) => request(`/personal-memory/conversations/${id}/summary`, { method: 'POST', body: { retry }, timeoutMs: 15000 })
