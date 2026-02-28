import { ref, computed } from 'vue'
import type { SearchFilters, Currency, Category } from '../types/search'
import { DEFAULT_FILTERS } from '../types/search'

export function useFilters() {
  const filters = ref<SearchFilters>({ ...DEFAULT_FILTERS })
  
  const activeFilterCount = computed(() => {
    let count = 0
    
    if (filters.value.categories && filters.value.categories.length > 0) {
      count += 1
    }
    
    if (filters.value.priceMin !== null || filters.value.priceMax !== null) {
      count += 1
    }
    
    if (filters.value.currency !== 'any') {
      count += 1
    }
    
    if (filters.value.standaloneOnly) {
      count += 1
    }
    
    if (filters.value.dateFrom || filters.value.dateTo) {
      count += 1
    }
    
    return count
  })
  
  function setFilter<K extends keyof SearchFilters>(key: K, value: SearchFilters[K]) {
    filters.value = { ...filters.value, [key]: value }
  }
  
  function resetFilters() {
    filters.value = { ...DEFAULT_FILTERS }
  }
  
  function updateCategories(categories: Category[] | null) {
    filters.value = { ...filters.value, categories }
  }
  
  function updatePriceRange(min: number | null, max: number | null) {
    filters.value = { ...filters.value, priceMin: min, priceMax: max }
  }
  
  function updateCurrency(currency: Currency) {
    filters.value = { ...filters.value, currency }
  }
  
  return {
    filters,
    activeFilterCount,
    setFilter,
    resetFilters,
    updateCategories,
    updatePriceRange,
    updateCurrency,
  }
}
