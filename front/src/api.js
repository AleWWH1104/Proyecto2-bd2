const BASE = 'http://localhost:8000'

export async function api(method, path, body) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } }
  if (body) opts.body = JSON.stringify(body)
  const r = await fetch(BASE + path, opts)
  if (!r.ok) {
    const e = await r.json().catch(() => ({}))
    throw new Error(e.detail || r.statusText)
  }
  return r.json().catch(() => null)
}

export function toList(data, keys = ['series','usuarios','actores','data','resenas']) {
  if (Array.isArray(data)) return data
  for (const k of keys) if (data?.[k]) return data[k]
  return []
}
