const API_BASE = '/api'

export interface StatsResponse {
  last_scrape_at: string | null
}

export async function fetchStats(): Promise<StatsResponse> {
  const response = await fetch(`${API_BASE}/stats`, {
    method: 'GET',
    headers: {
      'Accept': 'application/json',
    },
  })

  if (!response.ok) {
    throw new Error(`Failed to fetch stats: ${response.statusText}`)
  }

  return response.json() as Promise<StatsResponse>
}
