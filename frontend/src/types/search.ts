export type SearchMode = 'simple' | 'smart'

export type SearchModeUsed = 'simple' | 'smart' | 'smart_fallback' | 'latest'

export type SortOrder = 'relevance' | 'price_asc' | 'price_desc' | 'newest' | 'oldest' | 'updated'

export type Currency = 'UAH' | 'USD' | 'any'

export const CATEGORIES = [
  'cpu',
  'gpu',
  'ram',
  'motherboard',
  'ssd',
  'hdd',
  'psu',
  'monitor',
  'laptop',
  'case',
  'soundcard',
  'other',
] as const

export type Category = (typeof CATEGORIES)[number]

export interface SearchResultItem {
  item_id: number
  topic_id: number
  topic_url: string
  title: string
  category: string
  labels: string[]
  price: number | null
  currency: string | null
  is_standalone: boolean
  raw_text_segment: string
  author: string
  created_at: string
  last_update_at: string
  score: number
}

export interface SearchResponse {
  total_matches: number
  total_filtered: number
  search_mode_used: SearchModeUsed
  results: SearchResultItem[]
  search_time_seconds: number | null
  identified_category: string | null
  identified_labels: string[] | null
  auto_tuned_threshold: number | null
}

export interface SearchFilters {
  categories: Category[] | null
  priceMin: number | null
  priceMax: number | null
  currency: Currency
  standaloneOnly: boolean
  dateFrom: string | null
  dateTo: string | null
  sort: SortOrder
  limit: number | null
  offset: number
  minScore: number | null
  scoreAutoTune: boolean
}

export const DEFAULT_FILTERS: SearchFilters = {
  categories: null,
  priceMin: null,
  priceMax: null,
  currency: 'any',
  standaloneOnly: false,
  dateFrom: null,
  dateTo: null,
  sort: 'relevance',
  limit: 21,
  offset: 0,
  minScore: 0.6,
  scoreAutoTune: true,
}

export function buildSearchParams(
  query: string,
  mode: SearchMode,
  filters: SearchFilters
): Record<string, string | string[] | number | undefined> {
  const params: Record<string, string | string[] | number | undefined> = {
    q: query,
    mode,
    sort: filters.sort,
    offset: filters.offset,
  }

  if (filters.limit !== null) {
    params.limit = filters.limit
  }

  if (filters.categories && filters.categories.length > 0) {
    params.category = filters.categories
  }

  if (filters.priceMin !== null) {
    params.price_min = filters.priceMin
  }

  if (filters.priceMax !== null) {
    params.price_max = filters.priceMax
  }

  if (filters.currency !== 'any') {
    params.currency = filters.currency
  }

  if (filters.standaloneOnly) {
    params.standalone_only = 'true'
  }

  if (filters.dateFrom) {
    params.date_from = filters.dateFrom
  }

  if (filters.dateTo) {
    params.date_to = filters.dateTo
  }

  if (filters.minScore !== null) {
    params.min_score = filters.minScore
  }

  if (filters.scoreAutoTune) {
    params.score_auto_tune = 'true'
  }

  return params
}
