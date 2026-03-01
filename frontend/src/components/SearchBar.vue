<script setup lang="ts">
import { computed, ref } from 'vue'
import SmartModeToggle from './SmartModeToggle.vue'
import type { SearchMode, SearchModeUsed } from '../types/search'

const query = defineModel<string>('query', { required: true })
const mode = defineModel<SearchMode>('mode', { required: true })

const props = defineProps<{
  isLoading: boolean
  searchModeUsed: SearchModeUsed
  totalMatches: number | null
}>()

const emit = defineEmits<{
  search: [query: string, mode: SearchMode]
}>()

const statusMessage = computed(() => {
  if (!props.isLoading) return null
  if (props.searchModeUsed === 'smart') {
    return 'Agent is analyzing your query…'
  }
  return null
})

const isCountZero = computed(() => {
  if (!query.value.trim()) return false
  return props.totalMatches !== null && props.totalMatches === 0
})

function handleSubmit(e: Event) {
  e.preventDefault()
  emit('search', query.value, mode.value)
}
</script>

<template>
  <div class="space-y-3">
    <form @submit="handleSubmit" class="flex gap-4 items-center">
      <div class="flex-1 relative">
        <input
          v-model="query"
          type="text"
          placeholder="Search parts..."
          class="w-full h-12 pl-10 pr-4 rounded-lg border-2 border-gray-500 dark:border-gray-400 bg-white/95 dark:bg-gray-800/95 text-gray-900 dark:text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <svg
          class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </div>
      
      <button
        type="submit"
        class="px-4 py-2 font-medium rounded-lg transition-colors flex items-center gap-2"
        :class="[
          isCountZero && query.trim()
            ? 'bg-gray-300 dark:bg-gray-700 text-gray-500 dark:text-gray-400'
            : 'bg-blue-500 hover:bg-blue-600 text-white',
          isLoading ? 'opacity-50 cursor-wait' : ''
        ]"
        :disabled="isLoading"
        :title="isCountZero && query.trim() ? 'No listings match the current filters.' : undefined"
      >
        <svg
          v-if="isLoading"
          class="animate-spin h-4 w-4"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
        </svg>
        <span>Search</span>
      </button>
      
      <SmartModeToggle v-model="mode" />
    </form>
    
    <div
      v-if="statusMessage"
      class="flex items-center gap-2 text-sm text-blue-600 dark:text-blue-400"
    >
      <span class="animate-pulse">●</span>
      <span>{{ statusMessage }}</span>
    </div>
  </div>
</template>
