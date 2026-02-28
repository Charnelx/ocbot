<script setup lang="ts">
import { ref } from 'vue'

const model = defineModel<number | null>({ required: true })

const isTooltipVisible = ref(false)

function handleInput(event: Event) {
  const target = event.target as HTMLInputElement
  const val = parseFloat(target.value)
  model.value = isNaN(val) ? null : val
}

function showTooltip() {
  isTooltipVisible.value = true
}

function hideTooltip() {
  isTooltipVisible.value = false
}
</script>

<template>
  <div class="space-y-2">
    <div class="flex items-center justify-between">
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
        Min score
      </label>
      <span class="text-sm font-mono text-blue-600 dark:text-blue-400">
        {{ model?.toFixed(2) ?? '-' }}
      </span>
    </div>

    <div class="relative" @mouseenter="showTooltip" @mouseleave="hideTooltip">
      <input
        :value="model ?? 0.6"
        @input="handleInput"
        type="range"
        min="0.1"
        max="1"
        step="0.05"
        class="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-600"
      />

      <div
        v-if="isTooltipVisible"
        role="tooltip"
        class="absolute top-full left-1/2 -translate-x-1/2 mt-2 z-50 w-80 p-3 bg-gray-900 text-white text-xs rounded-lg shadow-lg"
      >
        <p>With lower score more irrelevant results might be added to search results.</p>
        <p class="mt-1">Note that score set to 1 does not guarantee relevant results, it only guarantees that <strong>only results AI search agent considers 100% relevant</strong> will appear in search results.</p>
      </div>
    </div>

    <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400">
      <span>0.1</span>
      <span>1.0</span>
    </div>
  </div>
</template>
