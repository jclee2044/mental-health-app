import { test } from 'node:test'
import assert from 'node:assert/strict'
import { usePersonalMemory } from '../usePersonalMemory.js'
import { useChat } from '../useChat.js'
import { VoiceSession } from '../voice.js'
import { deferred, flush, harness } from './fakes.js'
import * as requests from '../api.js'

function memoryHarness() {
  const calls = [], state = { emotions: false, conversations: false, facts: false }
  const api = {
    async getMemoryPreferences() { return { ...state } },
    async getMemoryFacts() { return { facts: [] } },
    async getMemoryExclusions() { return { exclusions: [] } },
    async setMemoryPreferences(value) { calls.push(['preferences', value]); Object.assign(state, value); return { ...state } },
    async putMemoryFact(id, body) { calls.push(['save', id, body]); return { id, ...body } },
    async deleteMemoryFact(id) { calls.push(['forget', id]) },
    async excludeMemorySource(body) { calls.push(['exclude', body]) },
    async restoreMemorySource(kind, id) { calls.push(['restore', kind, id]) },
    async previewMemory(body) { calls.push(['preview', body]); return { status: 'ready', sources: [] } },
    async getMemorySource(kind, id) { calls.push(['original', kind, id]); return { kind, record: { id, messages: [] } } },
  }
  return { api, calls, state }
}

test('memory defaults off, requires confirmed server preferences and never invents facts', async () => {
  const h = memoryHarness(); let interruptions = 0
  const memory = usePersonalMemory({ api: h.api, conversationId: 'fictional', interrupt: () => interruptions++ })
  assert.equal(memory.scope(), null)
  await flush()
  assert.equal(memory.loaded.value, true); assert.equal(memory.scope(), null)
  await memory.updatePreference('emotions', true)
  assert.equal(interruptions, 1)
  assert.equal(memory.scope().conversation_id, 'fictional')
  assert.deepEqual(memory.facts.value, [])
  await memory.updatePreference('emotions', false)
  assert.equal(memory.scope(), null)
  memory.dispose()
})

test('failed consent save keeps confirmed preferences and visible retryable error', async () => {
  const h = memoryHarness(), memory = usePersonalMemory({ api: h.api, conversationId: 'fictional' })
  await flush()
  h.api.setMemoryPreferences = async () => { throw new Error('private SQL') }
  await memory.updatePreference('conversations', true)
  assert.equal(memory.preferences.value.conversations, false)
  assert.equal(memory.scope(), null)
  assert.match(memory.error.value, /try again/)
  assert.doesNotMatch(memory.error.value, /private/)
  memory.dispose()
})

test('remembering requires editable user confirmation; correction and forgetting are storage only', async () => {
  const h = memoryHarness(), memory = usePersonalMemory({ api: h.api, conversationId: 'fictional' })
  await flush()
  memory.remember({ kind: 'conversation', id: 'source-chat', text: 'I prefer listening.' })
  assert.equal(h.calls.length, 0)
  memory.draft.value = 'I prefer practical options.'
  await memory.saveFact()
  assert.equal(h.calls[0][2].conversation_id, 'source-chat')
  assert.equal(memory.facts.value[0].text, 'I prefer practical options.')
  memory.editFact(memory.facts.value[0]); memory.draft.value = 'A correction'
  await memory.saveFact()
  assert.equal(memory.facts.value.length, 1)
  await memory.forgetFact(memory.facts.value[0].id)
  assert.equal(memory.facts.value.length, 0)
  memory.dispose()
})

test('excluding a source clears its confirmed facts and context; allow again does not recreate facts', async () => {
  const h = memoryHarness(), memory = usePersonalMemory({ api: h.api, conversationId: 'fictional' })
  await flush()
  memory.facts.value = [{ id: 'fact', text: 'Fiction', conversation_id: 'chat' }]
  memory.acceptReport({ status: 'ready', sources: [{ kind: 'conversation', id: 'chat' }] })
  await memory.exclude({ kind: 'conversation', id: 'chat' })
  assert.equal(memory.facts.value.length, 0); assert.equal(memory.report.value, null)
  await memory.restore(memory.exclusions.value[0])
  assert.equal(memory.exclusions.value.length, 0); assert.equal(memory.facts.value.length, 0)
  memory.dispose()
})

test('leaving aborts memory reads and rejects late context/original responses', async () => {
  const h = memoryHarness(), pending = deferred(); let signal
  const memory = usePersonalMemory({ api: h.api, conversationId: 'fictional' })
  await flush()
  h.api.previewMemory = (_body, options) => { signal = options.signal; return pending.promise }
  const request = memory.preview()
  memory.dispose()
  assert.equal(signal.aborted, true)
  pending.resolve({ status: 'ready', sources: [{ kind: 'fact', id: 'late' }] })
  await request
  assert.equal(memory.report.value, null)
})

test('voice receives one memory scope at startup and ignores a cancelled late memory report', async () => {
  const h = harness(), pending = deferred(), reports = []
  h.api.createVoiceSession = (sdp, history, options) => { h.calls.sessions.push({ sdp, history, options }); return pending.promise }
  const voice = new VoiceSession({ ...h.options, getPersonalMemory: () => ({ local_date: '2026-11-02', conversation_id: 'fictional' }), onPersonalMemory: report => reports.push(report) })
  const startup = voice.start(); await flush(); h.peer.completeIce(); await flush()
  assert.deepEqual(h.calls.sessions[0].options.personalMemory, { local_date: '2026-11-02', conversation_id: 'fictional' })
  voice.stop('Stopped for memory settings', true)
  pending.resolve({ session_id: 'live_fake', sdp: 'v=0\r\n', duration_seconds: 300, personal_memory: { status: 'ready', sources: [] } })
  await startup
  assert.equal(reports.length, 0)
  assert.deepEqual(h.calls.ends, ['live_fake'])
  assert.equal(h.calls.sessions.length, 1)
  voice.dispose()
})

test('changing memory interrupts pending text, rejects a late reply and keeps the draft', async () => {
  const h = harness(), m = memoryHarness(), pending = deferred()
  Object.assign(h.api, m.api)
  h.api.sendTextMessage = () => pending.promise
  const chat = useChat(h.options)
  await flush()
  chat.draft.value = 'Fictional message'
  const sending = chat.send()
  await chat.personalMemory.updatePreference('emotions', true)
  pending.resolve({ reply: 'Late', personal_memory: { status: 'ready', sources: [{ kind: 'fact', id: 'old' }] } })
  await sending
  assert.equal(chat.messages.value.length, 1)
  assert.equal(chat.messages.value[0].status, 'failed')
  assert.equal(chat.draft.value, 'Fictional message')
  assert.equal(chat.personalMemory.report.value, null)
  assert.equal(h.calls.saves.length, 0)
  chat.dispose()
})

test('typed requests supply scope only after opt-in, with no extra model call or historical messages in browser history', async () => {
  const h = harness(), m = memoryHarness()
  Object.assign(h.api, m.api)
  const chat = useChat(h.options)
  await flush()
  chat.draft.value = 'First fictional message'; await chat.send()
  assert.equal(h.calls.text[0].options.personalMemory, undefined)
  await chat.personalMemory.updatePreference('conversations', true)
  chat.draft.value = 'Next fictional message'; await chat.send()
  assert.equal(typeof h.calls.text[1].options.personalMemory.conversation_id, 'string')
  assert.equal(h.calls.text.length, 2)
  assert.equal(h.calls.text[1].history.length, 2)
  chat.dispose()
})

test('memory endpoints share no-store transport and provider scope never contains browser configuration', async () => {
  const original = globalThis.fetch, calls = []
  globalThis.fetch = async (url, options) => { calls.push({ url, options }); return { ok: true, status: 200, json: async () => ({}) } }
  try {
    const personalMemory = { local_date: '2026-11-02', conversation_id: 'fictional' }
    await requests.getMemoryPreferences()
    await requests.setMemoryPreferences({ emotions: true, conversations: false, facts: false })
    await requests.previewMemory({ ...personalMemory, query: 'exam' })
    await requests.createVoiceSession('SDP', [], { personalMemory })
    await requests.sendTextMessage('fictional', [], { personalMemory })
    assert.ok(calls.every(item => item.options.cache === 'no-store'))
    assert.deepEqual(JSON.parse(calls[3].options.body), { sdp: 'SDP', history: [], personal_memory: personalMemory })
    assert.equal(calls.length, 5)
  } finally { globalThis.fetch = original }
})
