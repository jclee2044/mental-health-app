import { test } from 'node:test'
import assert from 'node:assert/strict'
import { useConversationRecords } from '../useConversationRecords.js'
import { useChat } from '../useChat.js'
import { deferred, flush, harness } from './fakes.js'

const record = (conversationId = 'fictional-chat', turnId = 'fictional-turn') => ({ conversationId, turnId, body: { position: 0, user: 'Fictional exam question', assistant: 'Fictional reply' } })
const enableMemory = api => {
  api.getMemoryPreferences = async () => ({ emotions: false, conversations: true, facts: false })
}

test('ending a chat returns immediately and starts one summary only after initial saves', async () => {
  const h = harness(), summary = deferred(), save = deferred()
  const calls = []
  h.api.generateMemorySummary = (id, retry) => { calls.push({ id, retry }); return summary.promise }
  h.api.saveChatTurn = () => save.promise
  const records = useConversationRecords({ api: h.api }), item = record()
  const saving = records.queue(item)
  assert.equal(records.finishConversation(item.conversationId, { summarize: true }), undefined)
  assert.equal(calls.length, 0)
  save.resolve({ saved: true, conversation_id: item.conversationId, turn_id: item.turnId })
  await saving; await flush()
  assert.deepEqual(calls, [{ id: item.conversationId, retry: false }])
  assert.equal(records.summaries.value[0].state, 'running')
  records.finishConversation(item.conversationId, { summarize: true })
  assert.equal(calls.length, 1)
  summary.resolve({ status: 'ready' }); await flush()
  assert.equal(records.summaries.value[0].state, 'saved')
})

test('manual storage Retry never causes a paid summary; summary Retry is separate', async () => {
  const h = harness(), calls = [], original = h.api.saveChatTurn
  h.api.saveChatTurn = async () => { throw new Error('mock storage failure') }
  h.api.generateMemorySummary = async (id, retry) => { calls.push({ id, retry }); return { status: 'ready' } }
  const records = useConversationRecords({ api: h.api }), item = record()
  await records.queue(item)
  records.finishConversation(item.conversationId, { summarize: true })
  assert.equal(records.summaries.value[0].state, 'failed')
  await records.retrySummary(records.summaries.value[0])
  assert.equal(records.summaries.value[0].state, 'failed')
  assert.equal(calls.length, 0)
  h.api.saveChatTurn = original
  await records.retry(records.records.value[0]); await flush()
  assert.equal(calls.length, 0)
  await records.retrySummary(records.summaries.value[0])
  assert.equal(calls.length, 1)
})

test('summary failure never changes a saved exchange; explicit retry targets only summary', async () => {
  const h = harness(); let calls = 0
  h.api.generateMemorySummary = async (_id, retry) => { calls++; if (!retry) throw new Error('mock unavailable'); return { status: 'empty' } }
  const records = useConversationRecords({ api: h.api }), item = record()
  await records.queue(item)
  records.finishConversation(item.conversationId, { summarize: true }); await flush()
  assert.equal(records.records.value[0].state, 'saved')
  assert.equal(records.summaries.value[0].state, 'failed')
  assert.equal(calls, 1)
  await records.retry(records.records.value[0]); await flush()
  assert.equal(calls, 1)
  await records.retrySummary(records.summaries.value[0])
  assert.equal(records.summaries.value[0].state, 'saved')
  assert.equal(h.calls.saves.length, 1)
})

test('new conversation can clear saved notices without losing ended-chat save dependencies', async () => {
  const h = harness(), pending = deferred(), save = h.api.saveChatTurn, calls = []
  h.api.generateMemorySummary = async id => { calls.push(id); return { status: 'ready' } }
  const records = useConversationRecords({ api: h.api })
  await records.queue(record('first', 'one'))
  h.api.saveChatTurn = () => pending.promise
  const saving = records.queue(record('first', 'two'))
  records.finishConversation('first', { summarize: true })
  records.clearSaved()
  pending.resolve({ saved: true, conversation_id: 'first', turn_id: 'two' })
  await saving; await flush()
  assert.deepEqual(calls, ['first'])
  h.api.saveChatTurn = save
})

test('chat disposal schedules memory without waiting or keeping captions/draft alive', async () => {
  const h = harness(), pending = deferred(), calls = []
  enableMemory(h.api)
  h.api.generateMemorySummary = (id, retry) => { calls.push({ id, retry }); return pending.promise }
  const records = useConversationRecords({ api: h.api })
  const chat = useChat({ ...h.options, records })
  await flush()
  chat.draft.value = 'Fictional exam topic'; await chat.send(); await flush()
  assert.equal(calls.length, 0)
  chat.dispose(); chat.dispose()
  assert.deepEqual(chat.messages.value, []); assert.equal(chat.draft.value, '')
  assert.equal(calls.length, 1)
  pending.resolve({ status: 'ready' }); await flush()
  assert.equal(records.summaries.value[0].state, 'saved')
})

test('off permissions and chats without successful records never request summaries', async () => {
  const h = harness(); let calls = 0
  h.api.generateMemorySummary = async () => { calls++; return { status: 'ready' } }
  const chat = useChat(h.options)
  chat.draft.value = 'Fictional topic'; await chat.send(); await flush(); chat.dispose()
  assert.equal(calls, 0)
  enableMemory(h.api)
  const empty = useChat(h.options); await flush(); empty.dispose()
  assert.equal(calls, 0)
})

test('a save retry already in flight when chat ends still requires explicit summary retry', async () => {
  const h = harness(), pending = deferred(); let summaryCalls = 0
  h.api.saveChatTurn = async () => { throw new Error('mock storage failure') }
  h.api.generateMemorySummary = async () => { summaryCalls++; return { status: 'ready' } }
  const records = useConversationRecords({ api: h.api }), item = record()
  await records.queue(item)
  h.api.saveChatTurn = () => pending.promise
  const saving = records.retry(records.records.value[0])
  records.finishConversation(item.conversationId, { summarize: true })
  assert.equal(records.summaries.value[0].state, 'failed')
  pending.resolve({ saved: true, conversation_id: item.conversationId, turn_id: item.turnId })
  await saving; await flush()
  assert.equal(summaryCalls, 0)
  await records.retrySummary(records.summaries.value[0])
  assert.equal(summaryCalls, 1)
})
