import { test } from 'node:test'
import assert from 'node:assert/strict'
import { graphInteraction } from '../graph.js'

function fixture() {
  const points = [], captured = new Set()
  const target = {
    getBoundingClientRect: () => ({ left: 20, top: 40, width: 200, height: 200 }),
    setPointerCapture: id => captured.add(id), hasPointerCapture: id => captured.has(id),
    releasePointerCapture: id => captured.delete(id),
  }
  return { points, captured, graph: graphInteraction((...point) => points.push(point)),
    event: (x, y, extra = {}) => ({ pointerId: 1, isPrimary: true, button: 0, clientX: x, clientY: y, currentTarget: target, ...extra }) }
}

test('tap places a point; captured drag follows outside bounds and commits release', () => {
  const { graph, points, captured, event } = fixture()
  graph.down(event(120, 140)); assert.deepEqual(points.at(-1), [0, 0])
  assert.ok(captured.has(1))
  graph.move(event(170, 90)); assert.deepEqual(points.at(-1), [50, 50])
  graph.move(event(900, -100)); assert.deepEqual(points.at(-1), [100, 100])
  graph.up(event(20, 240)); assert.deepEqual(points.at(-1), [-100, -100])
  assert.equal(captured.size, 0)
  const count = points.length
  graph.move(event(120, 140)); assert.equal(points.length, count)
})

test('hover, secondary pointers/buttons, cancellation and lost capture cannot move the point', () => {
  const { graph, points, event } = fixture()
  graph.move(event(120, 140)); graph.down(event(120, 140, { button: 2 }))
  graph.down(event(120, 140, { isPrimary: false })); assert.equal(points.length, 0)
  graph.down(event(120, 140))
  graph.down(event(220, 40, { pointerId: 2 })); graph.move(event(220, 40, { pointerId: 2 }))
  assert.equal(points.length, 1)
  graph.cancel(event(120, 140)); graph.move(event(220, 40)); graph.up(event(220, 40))
  assert.equal(points.length, 1)
  graph.down(event(220, 40)); assert.deepEqual(points.at(-1), [100, 100])
})
