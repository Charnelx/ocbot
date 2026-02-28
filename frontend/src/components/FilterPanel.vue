<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import CategoryFilter from './CategoryFilter.vue'
import PriceRangeFilter from './PriceRangeFilter.vue'
import CurrencyFilter from './CurrencyFilter.vue'
import DateRangeFilter from './DateRangeFilter.vue'
import MinScoreFilter from './MinScoreFilter.vue'
import type { SearchFilters, SearchMode, Category } from '../types/search'

const filters = defineModel<SearchFilters>('filters', { required: true })
const activeCount = defineModel<number>('activeCount', { required: true })
const mode = defineModel<SearchMode>('mode', { required: true })

const emit = defineEmits<{
  reset: []
}>()

const STORAGE_KEY = 'hw_search_filters_open'

const isOpen = ref(false)

onMounted(() => {
  const saved = localStorage.getItem(STORAGE_KEY)
  if (saved !== null) {
    isOpen.value = saved === 'true'
  } else {
    isOpen.value = false
  }
})

watch(isOpen, (value) => {
  localStorage.setItem(STORAGE_KEY, String(value))
})

const activeFilters = computed(() => {
  const items: { key: string; label: string; clear: () => void }[] = []
  
  if (filters.value.categories && filters.value.categories.length > 0) {
    const labels = filters.value.categories.map(c => c.toUpperCase()).join(', ')
    items.push({
      key: 'categories',
      label: labels,
      clear: () => filters.value.categories = null
    })
  }
  
  if (filters.value.priceMin !== null || filters.value.priceMax !== null) {
    const min = filters.value.priceMin ?? ''
    const max = filters.value.priceMax ?? ''
    const label = min && max ? `$${min} - $${max}` : min ? `> $${min}` : `< $${max}`
    items.push({
      key: 'price',
      label,
      clear: () => {
        filters.value.priceMin = null
        filters.value.priceMax = null
      }
    })
  }
  
  if (filters.value.currency !== 'any') {
    items.push({
      key: 'currency',
      label: filters.value.currency,
      clear: () => filters.value.currency = 'any'
    })
  }
  
  if (filters.value.standaloneOnly) {
    items.push({
      key: 'standalone',
      label: 'Standalone',
      clear: () => filters.value.standaloneOnly = false
    })
  }
  
  if (filters.value.dateFrom || filters.value.dateTo) {
    const from = filters.value.dateFrom ? new Date(filters.value.dateFrom).toLocaleDateString() : ''
    const to = filters.value.dateTo ? new Date(filters.value.dateTo).toLocaleDateString() : ''
    const label = from && to ? `${from} - ${to}` : from ? `From ${from}` : `To ${to}`
    items.push({
      key: 'date',
      label,
      clear: () => {
        filters.value.dateFrom = null
        filters.value.dateTo = null
      }
    })
  }

  if (mode.value === 'smart' && filters.value.minScore !== null && !filters.value.scoreAutoTune) {
    items.push({
      key: 'minScore',
      label: `Min score: ${filters.value.minScore.toFixed(2)}`,
      clear: () => filters.value.minScore = 0.6
    })
  }

  if (mode.value === 'smart' && filters.value.scoreAutoTune) {
    items.push({
      key: 'scoreAutoTune',
      label: 'Score: auto',
      clear: () => filters.value.scoreAutoTune = false
    })
  }
  
  return items
})

function clearAll() {
  emit('reset')
}
</script>

<template>
  <div class="space-y-3">
    <div
      v-if="activeFilters.length > 0"
      class="flex flex-wrap items-center gap-2 py-2"
    >
      <span
        v-for="filter in activeFilters"
        :key="filter.key"
        class="inline-flex items-center gap-1 px-3 py-1 text-sm bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded-full"
      >
        {{ filter.label }}
        <button
          type="button"
          class="ml-1 hover:text-blue-900 dark:hover:text-blue-100"
          @click="filter.clear"
        >
          ×
        </button>
      </span>
      <button
        type="button"
        class="ml-auto text-sm text-blue-600 dark:text-blue-400 hover:underline"
        @click="clearAll"
      >
        Clear all
      </button>
    </div>
    
    <button
      type="button"
      class="flex items-center gap-3 text-lg text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors"
      @click="isOpen = !isOpen"
    >
      <svg
        class="w-6 h-6 transition-transform"
        :class="isOpen ? 'rotate-90' : ''"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
      </svg>
      <span class="font-medium">⚙ Filters</span>
      <span
        v-if="activeCount > 0"
        class="px-2 py-0.5 text-sm font-medium bg-blue-500 text-white rounded-full"
      >
        {{ activeCount }}
      </span>
    </button>
    
    <div
      v-show="isOpen"
      class="p-4 bg-white/95 dark:bg-gray-800/95 rounded-lg border-2 border-gray-400 dark:border-gray-500"
      style="box-shadow: 0 2px 8px rgba(0,0,0,0.15)"
    >
      <div class="grid grid-cols-1 xl:grid-cols-3 gap-x-6 gap-y-4">
        <CategoryFilter 
          v-if="mode === 'simple'"
          v-model:model-value="filters.categories"
          v-model:standalone-only="filters.standaloneOnly"
        />
        <div v-else>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Topics
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="filters.standaloneOnly"
              type="checkbox"
              class="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
            />
            <span class="text-sm text-gray-700 dark:text-gray-300">Standalone only</span>
          </label>
        </div>
        
        <div class="space-y-4">
          <PriceRangeFilter
            v-model:priceMin="filters.priceMin"
            v-model:priceMax="filters.priceMax"
            v-model:currency="filters.currency"
          />
          
          <div v-if="mode === 'smart'" class="flex items-end gap-4">
            <div class="flex-1">
              <MinScoreFilter v-if="!filters.scoreAutoTune" v-model="filters.minScore" />
              <div v-else class="pt-2">
                <label class="text-sm text-gray-700 dark:text-gray-300">
                  Score auto-tuned to: {{ filters.minScore?.toFixed(2) ?? '0.00' }}
                </label>
              </div>
            </div>
            <label class="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300 cursor-pointer mb-1">
              <input
                v-model="filters.scoreAutoTune"
                type="checkbox"
                class="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              Auto-tune
            </label>
          </div>
        </div>
        
        <CurrencyFilter v-model="filters.currency" />
      </div>
      
      <div class="mt-4">
        <DateRangeFilter
          v-model:dateFrom="filters.dateFrom"
          v-model:dateTo="filters.dateTo"
        />
      </div>

      <div class="mt-4 flex justify-end">
        <button
          v-if="activeCount > 0"
          type="button"
          class="text-sm text-blue-600 dark:text-blue-400 hover:underline"
          @click="emit('reset')"
        >
          Reset filters
        </button>
      </div>
    </div>
  </div>
</template>
