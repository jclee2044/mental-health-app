import { test } from 'node:test'
import assert from 'node:assert/strict'
import { getVoiceConfig, createVoiceSession, sendTextMessage, endVoiceSession, saveChatTurn, listConversations, getConversation, deleteConversation } from '../api.js'
import { transcribeRecording } from '../api.js'

test('dictation uses bounded shared JSON transport without browser model configuration', async () => {
  const original = globalThis.fetch, calls = []
  globalThis.fetch = async (url, options) => { calls.push({ url, options }); return { ok: true, status: 200, json: async () => ({ text: 'A win' }) } }
  try {
    assert.deepEqual(await transcribeRecording('fictional-base64', 'audio/webm'), { text: 'A win' })
    assert.equal(calls[0].url, '/api/chat/transcriptions')
    assert.deepEqual(JSON.parse(calls[0].options.body), { audio: 'fictional-base64', mime_type: 'audio/webm' })
    assert.equal(calls[0].options.cache, 'no-store')
  } finally { globalThis.fetch = original }
})

test('endpoint wrappers use only same-origin shared transport and never auto-retry', async () => {
  const original = globalThis.fetch, calls = []
  globalThis.fetch = async (url, options) => { calls.push({ url, options }); return { ok: true, status: 200, json: async () => ({}) } }
  try {
    await getVoiceConfig(); await createVoiceSession('fake SDP'); await sendTextMessage('fictional', [])
    assert.deepEqual(calls.map(call => call.url), ['/api/voice/config', '/api/voice/sessions', '/api/chat/messages'])
    assert.deepEqual(JSON.parse(calls[1].options.body), { sdp: 'fake SDP', history: [] })
    assert.deepEqual(JSON.parse(calls[2].options.body), { message: 'fictional', history: [] })
    assert.ok(calls.every(call => call.options.cache === 'no-store'))
    globalThis.fetch = async () => { calls.push({}); throw new Error('offline') }
    await assert.rejects(createVoiceSession('fake SDP'))
    assert.equal(calls.length, 4)
  } finally { globalThis.fetch = original }
})

test('server close uses a bounded keepalive POST and rejects untrusted identifiers before HTTP', async () => {
  const original = globalThis.fetch, calls = []
  globalThis.fetch = async (url, options) => { calls.push({ url, options }); return { ok: true, status: 204 } }
  try {
    assert.equal(await endVoiceSession('live_fake'), null)
    assert.equal(calls[0].url, '/api/voice/sessions/live_fake/end')
    assert.equal(calls[0].options.keepalive, true)
    assert.deepEqual(JSON.parse(calls[0].options.body), {})
    assert.equal(calls[0].options.cache, 'no-store')
    assert.throws(() => endVoiceSession('../untrusted'))
    assert.equal(calls.length, 1)
  } finally { globalThis.fetch = original }
})

test('conversation endpoints use shared no-store transport and separate storage from generation', async () => {
  const original = globalThis.fetch, calls = []
  globalThis.fetch = async (url, options) => { calls.push({ url, options }); return { ok: true, status: options.method === 'DELETE' ? 204 : 200, json: async () => ({}) } }
  try {
    const body = { position: 0, user: 'Fictional question', assistant: 'Fictional reply' }
    await saveChatTurn('conversation', 'turn', body); await listConversations(); await getConversation('conversation'); await deleteConversation('conversation')
    assert.deepEqual(calls.map(call => [call.url, call.options.method]), [
      ['/api/chat/conversations/conversation/turns/turn', 'PUT'], ['/api/chat/conversations', 'GET'],
      ['/api/chat/conversations/conversation', 'GET'], ['/api/chat/conversations/conversation', 'DELETE'],
    ])
    assert.deepEqual(JSON.parse(calls[0].options.body), body)
    assert.ok(calls.every(call => call.options.cache === 'no-store'))
  } finally { globalThis.fetch = original }
})
