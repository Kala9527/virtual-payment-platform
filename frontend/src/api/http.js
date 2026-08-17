const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.DEV ? 'http://localhost:8006' : '')

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  })

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}))
    throw new Error(payload.detail || '请求失败，请稍后重试')
  }

  return response.json()
}

export const assetUrl = (path) => `${API_BASE_URL}${path}`

export const api = {
  listProducts: () => request('/api/products'),
  createOrder: (payload) =>
    request('/api/orders', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  confirmOrder: (orderNo) =>
    request(`/api/orders/${orderNo}/confirm`, {
      method: 'POST',
    }),
}
