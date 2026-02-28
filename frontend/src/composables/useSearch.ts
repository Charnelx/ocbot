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
  
  const totalMatches = ref<number | null>(null)
  const totalFiltered = ref<number | null>(null)
  const searchModeUsed = ref<SearchModeUsed>('simple')
  const searchTimeSeconds = ref<number | null>(null)
  const identifiedCategory = ref<string | null>(null)
  const identifiedLabels = ref<string[] | null>(null)
  const autoTunedThreshold = ref<number | null>(null)
  
  async function search(q: string, searchMode: SearchMode, filters: SearchFilters = DEFAULT_FILTERS) {
    if (!q.trim()) {
      results.value = []
      totalMatches.value = 0
      totalFiltered.value = 0
      searchModeUsed.value = 'simple'
      searchTimeSeconds.value = null
      identifiedCategory.value = null
      identifiedLabels.value = null
      autoTunedThreshold.value = null
      return
    }
    
    isLoading.value = true
    error.value = null
    
    try {
      const response = await searchItems(q, searchMode, filters)
      results.value = response.results
      totalMatches.value = response.total_matches
      totalFiltered.value = response.total_filtered
      searchModeUsed.value = response.search_mode_used
      searchTimeSeconds.value = response.search_time_seconds ?? null
      identifiedCategory.value = response.identified_category ?? null
      identifiedLabels.value = response.identified_labels ?? null
      autoTunedThreshold.value = response.auto_tuned_threshold ?? null
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Search failed'
      results.value = []
      totalMatches.value = 0
      totalFiltered.value = 0
    } finally {
      isLoading.value = false
    }
  }
  
  return {
    query,
    mode,
    results,
    isLoading,
    error,
    totalMatches,
    totalFiltered,
    searchModeUsed,
    searchTimeSeconds,
    identifiedCategory,
    identifiedLabels,
    autoTunedThreshold,
    search,
  }
}
