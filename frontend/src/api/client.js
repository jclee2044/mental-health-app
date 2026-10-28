// The only frontend module allowed to perform HTTP requests.
export class ApiError extends Error {
  constructor(message, fields = {}, code = 'transport_error') {
    super(message)
    this.fields = fields
    this.code = code
  }
}

export async function request(path, { method = 'GET', body, signal, timeoutMs = 8000, keepalive = false } = {}) {
  try {
    const timeout = AbortSignal.timeout(timeoutMs)
    const response = await fetch(`/api${path}`, {
      method, cache: 'no-store',
      ...(keepalive ? { keepalive: true } : {}),
      headers: body ? { 'Content-Type': 'application/json' } : {},
      ...(body && method !== 'GET' ? { body: JSON.stringify(body) } : {}),
      signal: signal ? AbortSignal.any([signal, timeout]) : timeout,
    })
    if (response.status === 204) return null
    const data = await response.json()
    if (!response.ok) throw new ApiError(data.error?.message || 'The request could not be completed.', data.error?.fields, data.error?.code)
    return data
  } catch (error) {
    if (error instanceof ApiError) throw error
    throw new ApiError('Couldn’t reach saved records. Check that the local server is running, then try again.')
  }
}
