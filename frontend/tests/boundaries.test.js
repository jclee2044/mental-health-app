import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readdirSync, readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'

function files(directory) {
  return readdirSync(directory, { withFileTypes: true }).flatMap(entry => entry.isDirectory() ? files(`${directory}/${entry.name}`) : [`${directory}/${entry.name}`])
}
test('HTTP transport is confined to the API client', () => {
  const root = fileURLToPath(new URL('../src', import.meta.url))
  for (const file of files(root).filter(path => /\.(vue|js)$/.test(path))) {
    if (file.endsWith('/api/client.js')) continue
    assert.doesNotMatch(readFileSync(file, 'utf8'), /\bfetch\s*\(|XMLHttpRequest|\baxios\b/, file)
  }
})
test('pure feature domain rules have no Vue or API imports', () => {
  const root = fileURLToPath(new URL('../src/features', import.meta.url))
  for (const file of files(root).filter(path => /\/(?:domain|clock)\.js$/.test(path))) assert.doesNotMatch(readFileSync(file, 'utf8'), /from ['"](?:vue|.*api\/)|\b(?:document|window|localStorage)\b/, file)
})
test('feature code never imports a sibling feature', () => {
  const root = fileURLToPath(new URL('../src/features', import.meta.url))
  for (const file of files(root).filter(path => /\.(vue|js)$/.test(path))) assert.doesNotMatch(readFileSync(file, 'utf8'), /from ['"](?:\.\.\/(?:emotion|breathing)\/|.*features\/(?:emotion|breathing)\/)/, file)
})
