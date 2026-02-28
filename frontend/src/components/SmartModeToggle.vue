<script setup lang="ts">
import { ref } from 'vue'
import type { SearchMode } from '../types/search'

const model = defineModel<SearchMode>({ required: true })

const isTooltipVisible = ref(false)

function toggle() {
  model.value = model.value === 'simple' ? 'smart' : 'simple'
}

function showTooltip() {
  isTooltipVisible.value = true
}

function hideTooltip() {
  isTooltipVisible.value = false
}
</script>

<template>
  <div 
    class="flex items-center gap-2 relative"
    @mouseenter="showTooltip"
    @mouseleave="hideTooltip"
    @focus="showTooltip"
    @blur="hideTooltip"
  >
    <span class="text-sm text-gray-600 dark:text-gray-400">Simple</span>
    <button
      type="button"
      role="switch"
      :aria-checked="model === 'smart'"
      aria-describedby="smart-tooltip"
      class="relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500"
      :class="model === 'smart' ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700'"
      @click="toggle"
    >
      <span
        class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out"
        :class="model === 'smart' ? 'translate-x-5' : 'translate-x-0'"
      />
    </button>
    <span class="text-sm text-gray-600 dark:text-gray-400">Smart</span>
    
    <div
      v-if="isTooltipVisible"
      id="smart-tooltip"
      role="tooltip"
      class="absolute top-full mt-2 left-1/2 -translate-x-1/2 z-50 w-64 p-3 bg-gray-900 text-white text-xs rounded-lg shadow-lg"
    >
      <p class="font-medium mb-1"><span class="text-blue-400">Smart:</span> Interprets intent, synonyms, and related terms automatically.</p>
      <p><span class="text-gray-400">Simple:</span> Exact keyword match only - no interpretation.</p>
    </div>
  </div>
</template>
