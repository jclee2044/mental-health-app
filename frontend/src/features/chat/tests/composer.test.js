import { test } from 'node:test'
import assert from 'node:assert/strict'
import { submitOnEnter } from '../composer.js'
import { useChat } from '../useChat.js'
import { deferred, harness } from './fakes.js'

test('Enter sends; Shift+Enter and composition keep native editor behavior', () => {
  let sends = 0, prevented = 0
  const event = properties => ({ key: 'Enter', preventDefault: () => prevented++, ...properties })
  submitOnEnter(event({}), () => sends++)
  assert.equal(sends, 1); assert.equal(prevented, 1)
  for (const properties of [{ shiftKey: true }, { isComposing: true }, { keyCode: 229 }, { key: 'a' }]) submitOnEnter(event(properties), () => sends++)
  assert.equal(sends, 1); assert.equal(prevented, 1)
  submitOnEnter(event({ repeat: true }), () => sends++)
  assert.equal(sends, 1); assert.equal(prevented, 2)
})

test('Send immediately clears the draft and preserves a newly typed next message on success', async () => {
  const h = harness(), response = deferred()
  h.api.sendTextMessage = () => response.promise
  const chat = useChat(h.options)
  chat.draft.value = 'Fictional first message'
  const pending = chat.send()
  assert.equal(chat.draft.value, '')
  assert.equal(chat.messages.value[0].text, 'Fictional first message')
  assert.equal(chat.textBusy.value, true)
  chat.draft.value = 'Fictional second message'
  response.resolve({ reply: 'Fictional reply' }); await pending
  assert.equal(chat.draft.value, 'Fictional second message')
  chat.dispose()
})

test('Failure restores an untouched cleared draft without repeating the request', async () => {
  const h = harness(), response = deferred(); let requests = 0
  h.api.sendTextMessage = () => { requests++; return response.promise }
  const chat = useChat(h.options)
  chat.draft.value = 'Fictional retry message'
  const pending = chat.send()
  assert.equal(chat.draft.value, '')
  response.reject(new Error('Mock failure')); await pending
  assert.equal(chat.draft.value, 'Fictional retry message')
  assert.equal(chat.messages.value[0].status, 'failed')
  assert.equal(requests, 1)
  chat.dispose()
})

test('Failure never overwrites a changed draft; explicit restore is available when empty', async () => {
  const h = harness(), response = deferred()
  h.api.sendTextMessage = () => response.promise
  const chat = useChat(h.options)
  chat.draft.value = 'Fictional failed message'
  const pending = chat.send()
  chat.draft.value = 'Fictional newer draft'
  response.reject(new Error('Mock failure')); await pending
  assert.equal(chat.draft.value, 'Fictional newer draft')
  chat.restoreDraft(chat.messages.value[0])
  assert.equal(chat.draft.value, 'Fictional newer draft')
  chat.draft.value = ''
  chat.restoreDraft(chat.messages.value[0])
  assert.equal(chat.draft.value, 'Fictional failed message')
  chat.dispose()
})

test('Successful response does not clear identical text intentionally entered again', async () => {
  const h = harness(), response = deferred()
  h.api.sendTextMessage = () => response.promise
  const chat = useChat(h.options)
  chat.draft.value = 'Fictional same text'
  const pending = chat.send()
  chat.draft.value = 'Fictional same text'
  response.resolve({ reply: 'Fictional reply' }); await pending
  assert.equal(chat.draft.value, 'Fictional same text')
  chat.dispose()
})
