import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { Buffer } from 'node:buffer'
import { parse, compileScript } from '@vue/compiler-sfc'
import { createSSRApp, ref } from 'vue'
import { renderToString } from 'vue/server-renderer'

// Render the real SFC with injected chat state; no DOM devices, HTTP or provider.
const source = readFileSync(new URL('../ChatView.vue', import.meta.url), 'utf8')
const { descriptor } = parse(source)
const compiled = compileScript(descriptor, { id: 'chat-mock', inlineTemplate: true, templateOptions: { ssr: true } }).content
  .replace(/import AppIcon from ['"][^'"]+['"]/, 'const AppIcon = { render: () => null }')
  .replace(/import \{ useChat \} from ['"][^'"]+['"]/, 'const useChat = () => globalThis.chatViewMock')
  .replace(/from (['"])(\.\/lifecycle\.js)\1/g, (_match, _quote, path) => `from '${new URL(`../${path}`, import.meta.url).href}'`)
  .replace(/from (['"])(\.\/useTranscriptScroll\.js)\1/g, (_match, _quote, path) => `from '${new URL(`../${path}`, import.meta.url).href}'`)
  .replace(/from (['"])(vue(?:\/server-renderer)?)\1/g, (_match, _quote, name) => `from '${import.meta.resolve(name)}'`)
const { default: ChatView } = await import(`data:text/javascript;base64,${Buffer.from(compiled).toString('base64')}`)

for (const status of ['permission', 'connecting', 'active', 'muted', 'closing', 'closed', 'error']) {
  test(`chat renders ${status} while retaining an enabled text composer and End chat`, async () => {
    globalThis.chatViewMock = {
      messages: ref([{ id: 'one', role: 'user', text: 'Fictional message', source: 'text', status: 'complete' }, { id: 'two', role: 'assistant', text: '  \n Fictional reply', source: 'text', status: 'complete' }]),
      draft: ref('Keep this draft'), textBusy: ref(false), textError: ref(''),
      dictationState: ref({ status: 'idle', message: '' }), dictation: { start() {}, stop() {}, dispose() {} },
      voiceState: ref({ status, message: 'Mocked state', microphoneMuted: status === 'muted', playbackBlocked: status === 'active', mutePending: false }),
      voice: { start() {}, stop() {}, toggleMute() {}, enableAudio() {} }, send() {}, dispose() {},
    }
    try {
      const html = await renderToString(createSSRApp(ChatView, { interrupted: false }))
      assert.match(html, new RegExp(`data-voice-state="${status}"`))
      const textarea = html.match(/<textarea[^>]*>[\s\S]*?<\/textarea>/)[0]
      assert.doesNotMatch(textarea, /disabled/); assert.match(textarea, /Keep this draft/)
      assert.match(html, /End chat/); assert.match(html, />Send/)
      assert.ok(html.indexOf('>End chat</button>') > html.indexOf('>Send'))
      assert.match(html, /role="region" aria-label="Chat window"/)
      const composer = html.match(/<form[\s\S]*?<\/form>/)[0]
      if (['closed', 'error'].includes(status)) assert.match(composer, /<button[^>]*type="button"[^>]*>[\s\S]*?Voice mode/)
      if (['permission', 'connecting', 'active', 'muted', 'closing'].includes(status)) assert.match(composer, /<button[^>]*type="button"[^>]*>[\s\S]*?(?:Cancel voice setup|End voice)/)
      assert.match(html, /chat-user/); assert.match(html, /chat-assistant/)
      assert.match(html, /<p>Fictional reply<\/p>/)
      if (status === 'active') assert.match(html, /Enable assistant audio/)
      if (['active', 'muted'].includes(status)) { assert.match(html, /End voice/); assert.match(html, /billing continue/) }
      if (status === 'permission') assert.match(html, /Cancel voice setup/)
    } finally { delete globalThis.chatViewMock }
  })
}

for (const status of ['closed', 'permission', 'active']) {
  test(`empty chat ${status} shows End chat only after voice starts`, async () => {
    globalThis.chatViewMock = {
      messages: ref([]), draft: ref(''), textBusy: ref(false), textError: ref(''),
      dictationState: ref({ status: 'idle', message: '' }), dictation: { start() {}, stop() {}, dispose() {} },
      voiceState: ref({ status, message: status === 'closed' ? 'Microphone off.' : 'Mocked state' }),
      voice: { start() {}, stop() {}, toggleMute() {}, enableAudio() {} }, send() {}, dispose() {},
    }
    try {
      const html = await renderToString(createSSRApp(ChatView, { interrupted: false }))
      if (status === 'closed') assert.doesNotMatch(html, /End chat/)
      else assert.match(html, /End chat/)
      assert.match(html, /What’s on your mind\?/)
      assert.match(html, /Your day, something weighing on you/)
      assert.match(html, /<details class="chat-privacy-details">/)
    } finally { delete globalThis.chatViewMock }
  })
}
