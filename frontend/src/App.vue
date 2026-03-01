<script setup lang="ts">
import { ref, computed } from 'vue'
import AppHeader from './components/AppHeader.vue'
import SearchBar from './components/SearchBar.vue'
import FilterPanel from './components/FilterPanel.vue'
import SortBar from './components/SortBar.vue'
import ResultsGrid from './components/ResultsGrid.vue'
import EmptyState from './components/EmptyState.vue'
import PcbBackground from './components/PcbBackground.vue'
import { useSearch } from './composables/useSearch'
import { useFilters } from './composables/useFilters'
import type { SearchResultItem } from './types/search'

const { query, mode, results, isLoading, isLoadingMore, hasMore, error, totalMatches, totalFiltered, searchModeUsed, searchTimeSeconds, identifiedCategory, identifiedLabels, autoTunedThreshold, search, loadMore } = useSearch()
const { filters, activeFilterCount, resetFilters, setFilter } = useFilters()

const hasSearched = ref(false)

const sortedResults = computed<SearchResultItem[]>(() => {
  if (!hasSearched.value) return []
  
  const items = [...results.value]
  const sort = filters.value.sort
  
  switch (sort) {
    case 'price_asc':
      return items.sort((a, b) => {
        if (a.price === null && b.price === null) return 0
        if (a.price === null) return 1
        if (b.price === null) return -1
        return a.price - b.price
      })
    case 'price_desc':
      return items.sort((a, b) => {
        if (a.price === null && b.price === null) return 0
        if (a.price === null) return 1
        if (b.price === null) return -1
        return b.price - a.price
      })
    case 'newest':
      return items.sort((a, b) => 
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      )
    case 'oldest':
      return items.sort((a, b) => 
        new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
      )
    case 'updated':
      return items.sort((a, b) => 
        new Date(b.last_update_at).getTime() - new Date(a.last_update_at).getTime()
      )
    case 'relevance':
    default:
      return items // API already returns sorted by relevance
  }
})

function handleSearch(q: string, searchMode: 'simple' | 'smart') {
  hasSearched.value = true
  search(q, searchMode, filters.value)
}
</script>

<template>
  <div class="relative min-h-screen">
    <PcbBackground />
    
    <div class="relative z-10">
      <AppHeader />
      
      <main class="max-w-7xl mx-auto px-4 py-6">
      <div class="space-y-4">
        <SearchBar
          v-model:query="query"
          v-model:mode="mode"
          :is-loading="isLoading"
          :search-mode-used="searchModeUsed"
          @search="handleSearch"
        />
        
        <FilterPanel
          v-model:filters="filters"
          v-model:active-count="activeFilterCount"
          v-model:mode="mode"
          @reset="resetFilters"
        />
        
        <SortBar
          v-if="hasSearched"
          :total-matches="totalMatches"
          :total-filtered="totalFiltered"
          :sort="filters.sort"
          :search-mode-used="searchModeUsed"
          :search-time-seconds="searchTimeSeconds"
          :identified-category="identifiedCategory"
          :identified-labels="identifiedLabels"
          :auto-tuned-threshold="autoTunedThreshold"
          @update:sort="setFilter('sort', $event)"
        />
        
        <EmptyState
          v-if="hasSearched && !isLoading && results.length === 0"
          :error="error"
          :has-query="query.length > 0"
        />
        
        <ResultsGrid
          v-else-if="hasSearched"
          :results="sortedResults"
          :is-loading="isLoading"
          :is-loading-more="isLoadingMore"
          :has-more="hasMore"
          @load-more="loadMore(query, mode, filters)"
        />
        
        <div v-else class="text-center py-12">
          <p class="text-gray-600 dark:text-gray-400 font-medium">
            Press Enter or click Search to see latest parts
          </p>
        </div>
      </div>
    </main>
    </div>
  </div>
</template>
