import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { Buffer } from 'node:buffer'
import { parse, compileScript } from '@vue/compiler-sfc'
import { createSSRApp, ref } from 'vue'
import { renderToString } from 'vue/server-renderer'

const source = readFileSync(new URL('../ConversationHistoryView.vue', import.meta.url), 'utf8')
const { descriptor } = parse(source)
const compiled = compileScript(descriptor, { id: 'history-mock', inlineTemplate: true, templateOptions: { ssr: true } }).content
  .replace(/import AppIcon from ['"][^'"]+['"]/, 'const AppIcon = { render: () => null }')
  .replace(/import \{ useConversationHistory \} from ['"][^'"]+['"]/, 'const useConversationHistory = () => globalThis.historyViewMock')
  .replace(/from (['"])(vue(?:\/server-renderer)?)\1/g, (_match, _quote, name) => `from '${import.meta.resolve(name)}'`)
const { default: HistoryView } = await import(`data:text/javascript;base64,${Buffer.from(compiled).toString('base64')}`)

for (const hasMessages of [false, true]) {
  test(`history ${hasMessages ? 'detail' : 'empty state'} uses ordinary chat wording and a header New button`, async () => {
    globalThis.historyViewMock = {
      conversations: ref([]), selected: ref(hasMessages ? { id: 'fake', created_at: '2026-10-27T12:00:00Z', message_count: 2, messages: [
        { turn_id: 'voice', role: 'user', content: 'A fictional day', source: 'voice' },
        { turn_id: 'text', role: 'assistant', content: 'Tell me more', source: 'text' },
      ] } : null), loading: ref(false), error: ref(''), confirming: ref(false),
      load() {}, open() {}, remove() {}, dispose() {},
    }
    try {
      const html = await renderToString(createSSRApp(HistoryView))
      assert.match(html, /Saved chats/)
      assert.match(html, /chat-history-heading[\s\S]*?>New<\/button>/)
      assert.doesNotMatch(html, /typed chats|Start a new chat|Spoken|Voice caption/)
      if (hasMessages) { assert.match(html, /A fictional day/); assert.match(html, /Tell me more/) }
    } finally { delete globalThis.historyViewMock }
  })
}
