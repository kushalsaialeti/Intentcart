/**
 * IntentCart Frontend API Service
 * Module: src/services/api.js
 *
 * Connects directly to FastAPI backend with proxy fallback:
 * - Primary: http://127.0.0.1:8000 (direct with CORS)
 * - Fallback: relative path /api (via Vite proxy)
 */

const RAW_API = import.meta.env.VITE_API_URL;
const CONFIGURED_API = RAW_API ? RAW_API.replace(/\/+$/, '') : null;
const DEFAULT_API = 'http://127.0.0.1:8000' || 'https://intentcart.onrender.com';

async function fetchWithFallback(endpointPath, options) {
  const primaryUrl = CONFIGURED_API ? `${CONFIGURED_API}${endpointPath}` : `${DEFAULT_API}${endpointPath}`;
  
  try {
    const res = await fetch(primaryUrl, options);
    if (res.ok || res.status === 400 || res.status === 422) {
      return res;
    }
  } catch (err) {
    if (err.name === 'AbortError') throw err;
    console.warn(`Direct fetch to ${primaryUrl} failed, trying relative proxy...`, err);
  }

  // Fallback to relative path via Vite dev proxy
  return await fetch(endpointPath, options);
}

export async function searchProducts(query, topK = 5, signal = null) {
  if (!query || !query.trim()) {
    throw new Error('Search query cannot be empty');
  }

  const response = await fetchWithFallback('/api/search', {
    method: 'POST',
    signal,
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: query.trim(),
      top_k: topK,
    }),
  });

  if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    throw new Error(errData.detail || errData.error || `Server responded with status ${response.status}`);
  }

  const data = await response.json();
  if (data.success === false) {
    throw new Error(data.error || 'Search failed');
  }

  return data;
}

export async function checkHealth() {
  try {
    const response = await fetchWithFallback('/api/health');
    if (!response.ok) return { status: 'offline' };
    return await response.json();
  } catch {
    return { status: 'offline' };
  }
}
