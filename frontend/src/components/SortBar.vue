<script setup lang="ts">
import { formatNumber } from '../utils/format'
import type { SortOrder, SearchModeUsed } from '../types/search'

defineProps<{
  totalMatches: number
  totalFiltered: number
  sort: SortOrder
  searchModeUsed: SearchModeUsed
  searchTimeSeconds?: number | null
  identifiedCategory?: string | null
  identifiedLabels?: string[] | null
  autoTunedThreshold?: number | null
}>()

const emit = defineEmits<{
  'update:sort': [value: SortOrder]
}>()

const DEFAULT_MIN_SCORE = 0.6

const sortOptions: { value: SortOrder; label: string }[] = [
  { value: 'relevance', label: 'Relevance' },
  { value: 'price_asc', label: 'Price: Low to High' },
  { value: 'price_desc', label: 'Price: High to Low' },
  { value: 'newest', label: 'Newest' },
  { value: 'oldest', label: 'Oldest' },
  { value: 'updated', label: 'Recently updated' },
]

function getModeLabel(mode: SearchModeUsed): string {
  switch (mode) {
    case 'simple':
      return 'Simple'
    case 'smart':
      return 'Smart'
    case 'smart_fallback':
      return 'Smart (fallback)'
    default:
      return ''
  }
}

function handleSortChange(e: Event) {
  const target = e.target as HTMLSelectElement
  emit('update:sort', target.value as SortOrder)
}
</script>

<template>
  <div class="space-y-1">
    <div class="flex items-center justify-between py-1">
      <p class="text-sm text-gray-700 dark:text-gray-400">
        Showing <span class="font-medium text-gray-900 dark:text-white">{{ formatNumber(totalFiltered) }}</span>
        of <span class="font-medium text-gray-900 dark:text-white">{{ formatNumber(totalMatches) }}</span>
        results in <span class="font-semibold">{{ getModeLabel(searchModeUsed) }} mode</span>
      </p>
      
      <div class="flex items-center gap-2">
        <label for="sort" class="text-sm text-gray-700 dark:text-gray-400">Sort by:</label>
        <select
          id="sort"
          :value="sort"
          class="px-3 py-1.5 text-sm rounded-md border-2 border-gray-500 dark:border-gray-400 bg-white/95 dark:bg-gray-800/95 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          @change="handleSortChange"
        >
          <option
            v-for="option in sortOptions"
            :key="option.value"
            :value="option.value"
          >
            {{ option.label }}
          </option>
        </select>
      </div>
    </div>

    <div class="flex flex-wrap gap-x-4 gap-y-1 text-sm text-gray-700 dark:text-gray-400">
      <p>Search time: <span class="font-medium text-gray-900 dark:text-white">{{ searchTimeSeconds !== null && searchTimeSeconds !== undefined ? `${searchTimeSeconds}s` : 'n/a' }}</span></p>
      <p>Identified category: <span class="font-medium text-gray-900 dark:text-white">{{ identifiedCategory || 'n/a' }}</span></p>
      <p v-if="identifiedLabels && identifiedLabels.length > 0" class="inline-flex items-center gap-1">
        Identified labels:
        <span class="inline-flex flex-wrap gap-1">
          <span
            v-for="label in identifiedLabels"
            :key="label"
            class="px-1.5 py-0.5 text-xs bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded"
          >
            {{ label }}
          </span>
        </span>
      </p>
      <span v-else>Identified labels: n/a</span>
      <span v-if="autoTunedThreshold !== null && autoTunedThreshold !== undefined" class="text-green-600 dark:text-green-400">
        ({{ autoTunedThreshold >= DEFAULT_MIN_SCORE - 0.001 ? `default score of ${autoTunedThreshold.toFixed(2)}` : `auto-tuned to ${autoTunedThreshold.toFixed(2)}` }})
      </span>
    </div>
  </div>
</template>
