import { readFileSync } from 'node:fs'
import { Buffer } from 'node:buffer'
import { parse, compileScript } from '@vue/compiler-sfc'
import { createRenderer } from 'vue'

// Execute real SFC handlers/lifecycle with injected boundaries; no browser audio,
// microphone, HTTP or provider. Feature tests supply their own mocks.
export async function setupView(url, replacements, props = {}, emit = () => {}, provides = {}) {
  const { descriptor } = parse(readFileSync(url, 'utf8'))
  let code = compileScript(descriptor, { id: 'completion-test' }).content
  for (const [pattern, replacement] of replacements) code = code.replace(pattern, replacement)
  code = code.replace(/from (['"])([^'"]+)\1/g, (_all, _quote, path) =>
    `from '${path.startsWith('.') ? new URL(path, url).href : import.meta.resolve(path)}'`)
  const { default: View } = await import(`data:text/javascript;base64,${Buffer.from(code).toString('base64')}`)
  const renderer = createRenderer({
    createComment: () => ({}), insert() {}, remove() {}, parentNode() {}, nextSibling() {},
  })
  let state
  const app = renderer.createApp({ setup() {
    state = View.setup(props, { expose() {}, emit })
    return () => null
  } })
  for (const [key, value] of Object.entries(provides)) app.provide(key, value)
  app.mount({})
  return { state, unmount: () => app.unmount() }
}
