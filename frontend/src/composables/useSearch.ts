import { ref } from 'vue'
import type { SearchResultItem, SearchMode, SearchModeUsed, SearchFilters } from '../types/search'
import { searchItems } from '../api/search'
import { DEFAULT_FILTERS } from '../types/search'

export function useSearch() {
  const query = ref('')
  const mode = ref<SearchMode>('simple')
  
  const results = ref<SearchResultItem[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const hasMore = ref(true)
  const isLoadingMore = ref(false)
  
  const totalMatches = ref<number | null>(null)
  const totalFiltered = ref<number | null>(null)
  const searchModeUsed = ref<SearchModeUsed>('simple')
  const searchTimeSeconds = ref<number | null>(null)
  const identifiedCategory = ref<string | null>(null)
  const identifiedLabels = ref<string[] | null>(null)
  const autoTunedThreshold = ref<number | null>(null)

  async function search(q: string, searchMode: SearchMode, filters: SearchFilters = DEFAULT_FILTERS, append = false) {
    if (!append) {
      results.value = []
      filters = { ...filters, offset: 0 }
      hasMore.value = true
    }
    
    isLoading.value = !append
    isLoadingMore.value = append
    error.value = null
    
    try {
      const response = await searchItems(q, searchMode, filters)
      
      if (append) {
        results.value = [...results.value, ...response.results]
      } else {
        results.value = response.results
      }
      
      totalMatches.value = response.total_matches
      totalFiltered.value = response.total_filtered
      searchModeUsed.value = response.search_mode_used
      searchTimeSeconds.value = response.search_time_seconds ?? null
      identifiedCategory.value = response.identified_category ?? null
      identifiedLabels.value = response.identified_labels ?? null
      autoTunedThreshold.value = response.auto_tuned_threshold ?? null
      
      hasMore.value = response.results.length > 0
      
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Search failed'
      if (!append) {
        results.value = []
        totalMatches.value = 0
        totalFiltered.value = 0
      }
    } finally {
      isLoading.value = false
      isLoadingMore.value = false
    }
  }
  
  async function loadMore(q: string, searchMode: SearchMode, filters: SearchFilters) {
    if (isLoadingMore.value || !hasMore.value) return
    
    isLoadingMore.value = true
    const nextOffset = results.value.length
    const newFilters = { ...filters, offset: nextOffset }
    await search(q, searchMode, newFilters, true)
  }
  
  function reset() {
    results.value = []
    totalMatches.value = null
    totalFiltered.value = null
    searchModeUsed.value = 'simple'
    searchTimeSeconds.value = null
    identifiedCategory.value = null
    identifiedLabels.value = null
    autoTunedThreshold.value = null
    hasMore.value = true
    error.value = null
  }
  
  return {
    query,
    mode,
    results,
    isLoading,
    isLoadingMore,
    error,
    hasMore,
    totalMatches,
    totalFiltered,
    searchModeUsed,
    searchTimeSeconds,
    identifiedCategory,
    identifiedLabels,
    autoTunedThreshold,
    search,
    loadMore,
    reset,
  }
}
