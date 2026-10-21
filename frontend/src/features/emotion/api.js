import { request } from '../../api/client.js'
export const listEntries = (options) => request('/entries', options)
export const saveEntry = (id, body, options = {}) => request(`/entries/${id}`, { ...options, method: 'PUT', body })
export const deleteEntry = (id, options = {}) => request(`/entries/${id}`, { ...options, method: 'DELETE' })
