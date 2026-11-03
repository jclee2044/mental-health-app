import { test } from 'node:test'
import assert from 'node:assert/strict'
import { Buffer } from 'node:buffer'
import { readFileSync } from 'node:fs'
import { parse, compileScript } from '@vue/compiler-sfc'
import { createSSRApp, ref } from 'vue'
import { renderToString } from 'vue/server-renderer'
import { usePersonalMemory } from '../usePersonalMemory.js'
import { flush } from './fakes.js'

const { descriptor } = parse(readFileSync(new URL('../PersonalMemoryPanel.vue', import.meta.url), 'utf8'))
const code = compileScript(descriptor, { id: 'memory-compact', inlineTemplate: true, templateOptions: { ssr: true } }).content
  .replace(/from (['"])(vue(?:\/server-renderer)?)\1/g, (_match, _quote, name) => `from '${import.meta.resolve(name)}'`)
const { default: Panel } = await import(`data:text/javascript;base64,${Buffer.from(code).toString('base64')}`)

test('compact memory disclosure retains only consent, lifecycle disclosure and status', async () => {
  const model = { preferences: ref({ emotions: true, conversations: true, facts: false }), loaded: ref(true), busy: ref(false), error: ref(''),
    report: ref(null), load() {}, updatePreference() {}, interrupt() {} }
  const html = await renderToString(createSSRApp(Panel, { model }))
  assert.equal((html.match(/type="checkbox"/g) ?? []).length, 3)
  for (const label of ['Use recent emotion logs', 'Use saved conversation text', 'Use facts I confirm', 'last seven days', 'Opening these controls stops voice and dictation']) assert.ok(html.includes(label))
  assert.doesNotMatch(html, /Facts you choose|Review context|Confirm fact|Preview permitted|<textarea|<form/)
  model.report.value = { status: 'ready', sources: [], chat_coverage: { status: 'partial', included_conversations: 20, eligible_conversations: 100 } }
  const partial = await renderToString(createSSRApp(Panel, { model }))
  assert.match(partial, /20 of 100 recent chats fit/)
})

test('loading compact controls requests preferences only, without loading removed editor/review data', async () => {
  let calls = 0
  const memory = usePersonalMemory({ api: { async getMemoryPreferences() { calls++; return { emotions: false, conversations: false, facts: false } } }, conversationId: 'fictional' })
  await flush()
  assert.equal(calls, 1); assert.equal(memory.loaded.value, true)
  assert.equal(memory.error.value, '')
  memory.dispose()
})
