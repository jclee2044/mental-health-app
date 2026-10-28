import { test } from 'node:test'
import assert from 'node:assert/strict'
import { useChat } from '../useChat.js'
import { useConversationRecords } from '../useConversationRecords.js'
import { useConversationHistory } from '../useConversationHistory.js'
import { deferred, flush, harness } from './fakes.js'

test('save failure retries only SQLite with the same IDs after leaving chat', async () => {
  const h = harness(), records = useConversationRecords({ api: h.api })
  const save = h.api.saveChatTurn
  let attempts = 0
  h.api.saveChatTurn = async (...args) => { if (++attempts === 1) throw new Error('offline'); return save(...args) }
  const chat = useChat({ ...h.options, records })
  chat.draft.value = 'Fictional breathing question'; await chat.send(); await flush()
  assert.equal(chat.messages.value.length, 2); assert.equal(records.records.value[0].state, 'failed')
  const queued = records.records.value[0]
  assert.deepEqual(queued.body, { position: 0, user: 'Fictional breathing question', assistant: 'A fictional reply.' })
  chat.dispose()
  await records.retry(queued)
  assert.equal(queued.state, 'saved'); assert.equal(h.calls.text.length, 1)
  assert.equal(h.calls.saves[0].turnId, queued.turnId)
  assert.equal(h.calls.saves[0].conversationId, queued.conversationId)
  await records.retry(queued); assert.equal(attempts, 2)
})

test('failed replies and ignored late replies never become saved conversations', async () => {
  const h = harness(), reply = deferred(), records = useConversationRecords({ api: h.api })
  h.api.sendTextMessage = () => reply.promise
  const chat = useChat({ ...h.options, records })
  chat.draft.value = 'Leave early'; const pending = chat.send(); chat.dispose()
  reply.resolve({ reply: 'Late' }); await pending
  assert.equal(records.records.value.length, 0)
  h.api.sendTextMessage = async () => { throw new Error('failed provider') }
  const next = useChat({ ...h.options, records }); next.draft.value = 'Fail'; await next.send()
  assert.equal(records.records.value.length, 0); next.dispose()
})

test('mixed chat saves voice separately before typed pairs and new chats do not retrieve history', async () => {
  const h = harness(), records = useConversationRecords({ api: h.api })
  const chat = useChat({ ...h.options, records })
  chat.messages.value.push({ role: 'assistant', source: 'voice', text: 'Unsaved caption' })
  for (const text of ['First typed question', 'Second typed question']) { chat.draft.value = text; await chat.send() }
  await flush()
  assert.deepEqual(h.calls.saves.map(item => item.body.position), [1, 2])
  assert.equal(h.calls.voiceSaves.length, 1)
  assert.deepEqual(h.calls.voiceSaves[0].body, { position: 0, messages: [{ role: 'assistant', content: 'Unsaved caption' }] })
  assert.ok(h.calls.saves.every(item => !JSON.stringify(item.body).includes('Unsaved caption')))
  const id = h.calls.saves[0].conversationId; chat.dispose()
  const next = useChat({ ...h.options, records }); next.draft.value = 'Fresh'; await next.send()
  assert.deepEqual(h.calls.text.at(-1).history, [])
  assert.notEqual(h.calls.saves.at(-1).conversationId, id); next.dispose()
})

test('duplicate Retry cannot send concurrent writes and invalid save responses stay retryable', async () => {
  const save = deferred(); let count = 0
  const records = useConversationRecords({ api: { saveChatTurn: () => { count++; return save.promise } } })
  const pending = records.queue({ conversationId: 'c', turnId: 't', body: {} })
  await records.retry(records.records.value[0]); assert.equal(count, 1)
  save.resolve({ saved: true, conversation_id: 'wrong', turn_id: 't' }); await pending
  assert.equal(records.records.value[0].state, 'failed')
})

test('saved history is read-only, requires deletion confirmation, and reports failed deletion', async () => {
  let deletes = 0
  const detail = { id: 'one', messages: [{ role: 'user', content: 'Fictional' }] }
  const api = {
    listConversations: async () => ({ conversations: [{ id: 'one' }] }),
    getConversation: async () => detail,
    deleteConversation: async () => { deletes++; throw new Error('private database detail') },
  }
  const history = useConversationHistory({ api })
  await history.load(); await history.open('one')
  assert.deepEqual(history.selected.value, detail)
  await history.remove(); assert.equal(deletes, 0)
  history.confirming.value = true; await history.remove()
  assert.equal(deletes, 1); assert.match(history.error.value, /unavailable/)
  assert.doesNotMatch(history.error.value, /private/); assert.equal(history.selected.value.id, 'one')
  api.deleteConversation = async () => { deletes++ }
  history.confirming.value = true; await history.remove()
  assert.equal(history.selected.value, null); assert.deepEqual(history.conversations.value, [])
  history.dispose()
})

test('history ignores stale selections and late results after navigation', async () => {
  const first = deferred(), last = deferred()
  const history = useConversationHistory({ api: { getConversation: id => id === 'first' ? first.promise : last.promise } })
  const a = history.open('first'), b = history.open('last')
  last.resolve({ id: 'last' }); await b; first.resolve({ id: 'first' }); await a
  assert.equal(history.selected.value.id, 'last')
  const late = deferred(), disposed = useConversationHistory({ api: { listConversations: () => late.promise } })
  const pending = disposed.load(); disposed.dispose()
  late.resolve({ conversations: [{ id: 'late' }] }); await pending
  assert.deepEqual(disposed.conversations.value, []); history.dispose()
})

test('voice text is queued once on End and retry after navigation never repeats a model call', async () => {
  const h = harness(), records = useConversationRecords({ api: h.api })
  const save = h.api.saveVoiceTurn; let attempts = 0
  h.api.saveVoiceTurn = async (...args) => { if (++attempts === 1) throw new Error('offline'); return save(...args) }
  const chat = useChat({ ...h.options, records })
  const pending = chat.voice.start(); await flush(); h.peer.completeIce(); await pending
  h.event({ type: 'session.started', session: { id: 'live_fake' } })
  h.event({ type: 'session.input_transcript.delta', event_id: 'u1', delta: 'A fictional day', start_ms: 0, end_ms: 200 })
  h.event({ type: 'session.output_transcript.delta', event_id: 'a1', delta: 'Tell me more.', start_ms: 300, end_ms: 500 })
  assert.equal(records.records.value.length, 0)
  chat.voice.stop('Ended', true); await flush()
  assert.equal(records.records.value.length, 1)
  const queued = records.records.value[0]
  assert.equal(queued.kind, 'voice'); assert.equal(queued.state, 'failed')
  assert.deepEqual(queued.body.messages, [{ role: 'user', content: 'A fictional day' }, { role: 'assistant', content: 'Tell me more.' }])
  chat.dispose(); await records.retry(queued)
  assert.equal(records.records.value.length, 1); assert.equal(queued.state, 'saved')
  assert.equal(h.calls.sessions.length, 1); assert.equal(h.calls.text.length, 0)
  assert.equal(h.calls.voiceSaves[0].turnId, queued.turnId)
})

test('leaving an active voice chat saves accepted text and excludes audio/fragment metadata', async () => {
  const h = harness(), chat = useChat(h.options)
  const pending = chat.voice.start(); await flush(); h.peer.completeIce(); await pending
  h.event({ type: 'session.started', session: { id: 'live_fake' } })
  h.event({ type: 'session.output_transcript.delta', event_id: 'a1', delta: 'A fictional reflection', start_ms: 0, end_ms: 200 })
  chat.dispose(); await flush()
  assert.equal(h.calls.voiceSaves.length, 1)
  assert.deepEqual(h.calls.voiceSaves[0].body, { position: 0, messages: [{ role: 'assistant', content: 'A fictional reflection' }] })
})
