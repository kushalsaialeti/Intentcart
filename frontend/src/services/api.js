/**
 * IntentCart Frontend API Service
 * Module: src/services/api.js
 *
 * Interacts with FastAPI backend endpoints:
 * - POST /api/search
 * - GET  /api/health
 */

const API_BASE = import.meta.env.VITE_API_URL || '';

export async function searchProducts(query, topK = 5) {
  if (!query || !query.trim()) {
    throw new Error('Search query cannot be empty');
  }

  const endpoint = `${API_BASE}/api/search`;
  const response = await fetch(endpoint, {
    method: 'POST',
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
    const response = await fetch(`${API_BASE}/api/health`);
    if (!response.ok) return { status: 'offline' };
    return await response.json();
  } catch {
    return { status: 'offline' };
  }
}
