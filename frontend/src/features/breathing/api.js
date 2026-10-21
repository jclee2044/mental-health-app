import { request } from '../../api/client.js'
export const saveSession = (id, body) => request(`/sessions/${id}`, { method: 'PUT', body })
export const listSessions = (options) => request('/sessions', options)
