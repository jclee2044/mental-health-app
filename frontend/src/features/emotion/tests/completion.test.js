import { test } from 'node:test'
import assert from 'node:assert/strict'
import { setupView } from '../../../../tests/setupView.js'

test('emotion cue follows successful storage only, including storage retry', async () => {
  let finish, calls = 0
  const cues = []
  globalThis.emotionSound = { arm: () => ++calls, complete: ticket => cues.push(ticket) }
  globalThis.saveEmotion = () => new Promise((resolve, reject) => { finish = { resolve, reject } })
  const view = await setupView(new URL('../EmotionView.vue', import.meta.url), [
    [/import AppIcon from [^\n]+/, 'const AppIcon = {}'],
    [/import \{ saveEntry \} from [^\n]+/, 'const saveEntry = (...args) => globalThis.saveEmotion(...args)'],
    [/import \{ useCompletionSound \} from [^\n]+/, 'const useCompletionSound = () => globalThis.emotionSound'],
  ], { entry: null, interrupted: false })
  try {
    await view.state.save()
    assert.equal(calls, 0) // Invalid form cannot prime/play a cue.
    view.state.chosenPoint.value = true
    view.state.draft.color = '#123456'
    const failed = view.state.save()
    assert.deepEqual(cues, [])
    finish.reject(new Error('Mock save failed'))
    await failed
    assert.deepEqual(cues, [])
    assert.equal(view.state.saved.value, false)
    const retry = view.state.save()
    finish.resolve({})
    await retry
    assert.equal(view.state.saved.value, true)
    assert.deepEqual(cues, [2])
  } finally { view.unmount(); delete globalThis.emotionSound; delete globalThis.saveEmotion }
})
