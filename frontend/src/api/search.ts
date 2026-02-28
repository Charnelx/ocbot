import type { SearchResponse, SearchMode } from '../types/search'
import { buildSearchParams, type SearchFilters } from '../types/search'

const API_BASE = '/api'

class SearchApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public statusText: string
  ) {
    super(message)
    this.name = 'SearchApiError'
  }
}

function paramsToString(params: Record<string, string | string[] | number | undefined>): string {
  const searchParams = new URLSearchParams()
  
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null) continue
    
    if (Array.isArray(value)) {
      for (const v of value) {
        searchParams.append(key, v)
      }
    } else {
      searchParams.append(key, String(value))
    }
  }
  
  return searchParams.toString()
}

export async function searchItems(
  query: string,
  mode: SearchMode,
  filters: SearchFilters
): Promise<SearchResponse> {
  const params = buildSearchParams(query, mode, filters)
  const queryString = paramsToString(params)
  
  const response = await fetch(`${API_BASE}/search?${queryString}`, {
    method: 'GET',
    headers: {
      'Accept': 'application/json',
    },
  })
  
  if (!response.ok) {
    throw new SearchApiError(
      `Search failed: ${response.statusText}`,
      response.status,
      response.statusText
    )
  }
  
  return response.json() as Promise<SearchResponse>
}
