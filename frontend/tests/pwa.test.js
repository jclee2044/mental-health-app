import { test } from 'node:test'
import assert from 'node:assert/strict'
import { runInNewContext } from 'node:vm'
import { workerSource } from '../pwa/buildPwa.js'

test('offline worker intercepts only known shell assets, never API or writes', () => {
  const handlers = {}, cached = []
  runInNewContext(workerSource(['/', '/index.html', '/assets/app.js'], 'test'), {
    self: { location: { origin: 'http://localhost' }, addEventListener: (name, callback) => { handlers[name] = callback } },
    URL, caches: { match: request => { cached.push(request); return Promise.resolve('cached-shell') } }, fetch: () => Promise.reject(new Error('offline')),
  })
  const ignored = [
    { url: 'http://localhost/api/entries', method: 'GET' },
    { url: 'http://localhost/', method: 'POST' },
    { url: 'https://other.example/', method: 'GET' },
    { url: 'http://localhost/unknown', method: 'GET' },
  ]
  for (const request of ignored) handlers.fetch({ request, respondWith: () => assert.fail('Intercepted a non-shell request') })
  let response
  handlers.fetch({ request: { url: 'http://localhost/', method: 'GET', mode: 'navigate' }, respondWith: result => { response = result } })
  return response.then(result => { assert.equal(result, 'cached-shell'); assert.deepEqual(cached, ['/index.html']) })
})
