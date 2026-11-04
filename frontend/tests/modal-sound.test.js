import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { Buffer } from 'node:buffer'
import { parse, compileScript } from '@vue/compiler-sfc'
import { createRenderer, h, nextTick, ref } from 'vue'

// Render the real shared dialog and sound button, including their templates.
// No feature imports: this regression also runs at the interface checkpoint.
function componentModule(name, replacements = []) {
  const url = new URL(`../src/components/${name}.vue`, import.meta.url)
  const { descriptor } = parse(readFileSync(url, 'utf8'))
  let code = compileScript(descriptor, { id: name, inlineTemplate: true }).content
  code = code.replace(/import AppIcon from [^\n]+/, 'const AppIcon = { render: () => null }')
  for (const [pattern, replacement] of replacements) code = code.replace(pattern, replacement)
  code = code.replace(/from (['"])([^'"]+)\1/g, (_all, _quote, path) =>
    `from '${path.startsWith('data:') ? path : import.meta.resolve(path)}'`)
  return `data:text/javascript;base64,${Buffer.from(code).toString('base64')}`
}

function renderHost() {
  const node = tag => ({ tag, props: {}, children: [], parent: null, showModal() { this.open = true } })
  const renderer = createRenderer({
    createElement: node, createText: text => ({ ...node('#text'), text }), createComment: () => node('#comment'),
    insert(child, parent, anchor = null) {
      if (child.parent) child.parent.children.splice(child.parent.children.indexOf(child), 1)
      child.parent = parent
      const index = anchor ? parent.children.indexOf(anchor) : -1
      parent.children.splice(index < 0 ? parent.children.length : index, 0, child)
    },
    remove(child) { child.parent.children.splice(child.parent.children.indexOf(child), 1); child.parent = null },
    setElementText(element, text) { element.text = text; element.children = [] },
    setText(element, text) { element.text = text },
    patchProp(element, key, _old, value) { element.props[key] = value },
    parentNode: element => element.parent,
    nextSibling: element => element.parent?.children[element.parent.children.indexOf(element) + 1],
  })
  return { renderer, root: node('root') }
}

function descendants(node) { return [node, ...node.children.flatMap(descendants)] }

test('deletion dialog owns a working sound control across nested Emergency, resize and close', async () => {
  const soundModule = componentModule('SoundToggle')
  const { default: ModalSheet } = await import(componentModule('ModalSheet', [
    [/import SoundToggle from [^\n]+/, `import SoundToggle from '${soundModule}'`],
  ]))
  const originalWindow = globalThis.window
  const originalDocument = globalThis.document
  const resizeListeners = new Set()
  let restoredFocus = 0
  globalThis.window = {
    addEventListener(type, handler) { assert.equal(type, 'resize'); resizeListeners.add(handler) },
    removeEventListener(type, handler) { assert.equal(type, 'resize'); resizeListeners.delete(handler) },
  }
  globalThis.document = { activeElement: { focus() { restoredFocus++ } } }
  const enabled = ref(false)
  const modalCount = ref(0)
  const deletionOpen = ref(true)
  const emergencyOpen = ref(false)
  let deletions = 0
  let rect = { left: 300, top: 600, width: 84, height: 44 }
  const { renderer, root } = renderHost()
  const app = renderer.createApp({ render: () => h('main', [
    deletionOpen.value ? h(ModalSheet, {
      title: 'Delete this entry?', onClose: () => { deletionOpen.value = false },
      onEmergency: () => { emergencyOpen.value = true },
    }, { default: () => h('button', { onClick: () => { deletions++ } }, 'Delete entry') }) : null,
    emergencyOpen.value ? h(ModalSheet, {
      title: 'Emergency & crisis support', emergency: true,
      onClose: () => { emergencyOpen.value = false },
    }) : null,
  ]) })
  app.provide('appSoundEnabled', enabled)
  app.provide('appSoundAnchor', ref({ getBoundingClientRect: () => rect }))
  app.provide('appModalCount', modalCount)
  const dialogs = () => descendants(root).filter(node => node.tag === 'dialog')
  const sound = dialog => descendants(dialog).find(node => node.props['aria-label']?.includes('app sounds'))
  const clickSound = async dialog => {
    const button = sound(dialog)
    assert.ok(button, 'sound button must be inside the native dialog without a custom slot')
    button.props.onClick()
    dialog.props.onClick({ target: button }) // bubbling must not count as a backdrop click
    await nextTick()
  }
  try {
    app.mount(root)
    await nextTick()
    const deletion = dialogs()[0]
    assert.equal(deletion.open, true)
    assert.equal(modalCount.value, 1)
    assert.deepEqual(sound(deletion).props.style, { left: '300px', top: '600px', width: '84px', height: '44px' })
    await clickSound(deletion)
    assert.equal(enabled.value, true)
    assert.equal(sound(deletion).props['aria-label'], 'Mute all app sounds')
    assert.equal(deletionOpen.value, true)
    assert.equal(deletions, 0)

    descendants(deletion).find(node => node.props.class === 'emergency-button').props.onClick()
    await nextTick()
    assert.equal(modalCount.value, 2)
    assert.equal(sound(dialogs()[1]).props['aria-label'], 'Mute all app sounds')
    await clickSound(dialogs()[1])
    assert.equal(enabled.value, false)
    assert.equal(sound(deletion).props['aria-label'], 'Enable app sounds')
    descendants(dialogs()[1]).find(node => node.props['aria-label'] === 'Close panel').props.onClick()
    await nextTick()
    assert.equal(modalCount.value, 1)
    assert.equal(dialogs()[0], deletion)
    assert.equal(resizeListeners.size, 1)

    rect = { left: 200, top: 500, width: 84, height: 44 }
    for (const listener of resizeListeners) listener()
    await nextTick()
    assert.equal(sound(deletion).props.style.left, '200px')
    assert.equal(sound(deletion).props.style.top, '500px')
    descendants(deletion).find(node => node.props['aria-label'] === 'Close panel').props.onClick()
    await nextTick()
    assert.equal(modalCount.value, 0)
    assert.equal(dialogs().length, 0)
    assert.equal(resizeListeners.size, 0)
    assert.equal(restoredFocus, 2)
    assert.equal(deletions, 0)
  } finally {
    app.unmount()
    globalThis.window = originalWindow
    globalThis.document = originalDocument
  }
})
