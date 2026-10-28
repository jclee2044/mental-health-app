// Live has no completed-turn marker. Rebuild this session by speech timeline,
// not packet arrival, so a late speaker change can split an earlier bubble.
export function appendCaption(messages, fragment) {
  const belongs = message => message.source === 'voice' && message.session === fragment.session
  const first = messages.findIndex(belongs)
  const fragments = messages.filter(belongs).flatMap(message => message.fragments)
  if (fragments.some(part => part.id === fragment.id)) return
  fragments.push(fragment)
  fragments.sort((a, b) => a.start - b.start || a.end - b.end || a.id.localeCompare(b.id))
  const bubbles = [], latest = {}
  for (const part of fragments) {
    const previous = latest[part.role], other = latest[part.role === 'user' ? 'assistant' : 'user']
    const gap = previous ? part.start - previous.end : Infinity
    const speakerChanged = other && previous && other.lastStart >= previous.lastStart
    // Contiguous/overlapping speech can grow through a short backchannel.
    // A timeline gap after another speaker, or >=1s silence, starts a new bubble.
    if (previous && gap < 1000 && (gap <= 0 || !speakerChanged)) {
      previous.fragments.push(part); previous.text += part.text
      previous.end = Math.max(previous.end, part.end); previous.lastStart = part.start
    } else {
      const bubble = { id: `voice-${part.session}-${part.id}`, source: 'voice', session: part.session, role: part.role, text: part.text, start: part.start, end: part.end, lastStart: part.start, fragments: [part] }
      bubbles.push(bubble); latest[part.role] = bubble
    }
  }
  const remaining = messages.filter(message => !belongs(message))
  remaining.splice(first < 0 ? remaining.length : first, 0, ...bubbles)
  messages.splice(0, messages.length, ...remaining)
}

export function conversationHistory(messages) {
  const recent = messages.filter(message => ['user', 'assistant'].includes(message.role) &&
    (message.source === 'voice' || message.status === 'complete') && message.text.trim()).slice(-16)
  const selected = []; let bytes = 0
  for (const message of recent.reverse()) {
    const size = new TextEncoder().encode(message.text).length
    // Conservative startup budget below Live's rendered-history token limit.
    if (bytes + size > 6000) break
    bytes += size; selected.unshift({ role: message.role, content: message.text })
  }
  return selected
}

// Small immutable storage batches, preserving speaker order without audio/fragments.
export function voiceTranscriptBatches(messages) {
  const batches = []; let batch = [], bytes = 0
  const add = (role, content) => {
    if (!content.trim()) return
    const size = new TextEncoder().encode(content).length
    if (batch.length >= 50 || bytes + size > 8000) { batches.push(batch); batch = []; bytes = 0 }
    batch.push({ role, content }); bytes += size
  }
  for (const message of messages) {
    let content = '', size = 0
    for (const character of message.text) {
      const length = new TextEncoder().encode(character).length
      if (size + length > 8000) { add(message.role, content); content = ''; size = 0 }
      content += character; size += length
    }
    add(message.role, content)
  }
  if (batch.length) batches.push(batch)
  return batches
}
