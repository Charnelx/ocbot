<script setup lang="ts">
import { ref } from 'vue'
import { CATEGORIES, type Category } from '../types/search'

const model = defineModel<Category[] | null>({ required: true })
const standalone = defineModel<boolean>('standaloneOnly', { required: true })

const isTooltipVisible = ref(false)

const categoryGroups = [
  {
    label: 'Processors & Graphics',
    categories: ['cpu', 'gpu'] as Category[],
  },
  {
    label: 'Memory & Storage',
    categories: ['ram', 'ssd', 'hdd'] as Category[],
  },
  {
    label: 'System & Peripherals',
    categories: ['motherboard', 'psu', 'case', 'soundcard', 'monitor', 'laptop', 'other'] as Category[],
  },
]

const categoryLabels: Record<Category, string> = {
  cpu: 'CPU',
  gpu: 'GPU',
  ram: 'RAM',
  motherboard: 'Motherboard',
  ssd: 'SSD',
  hdd: 'HDD',
  psu: 'PSU',
  monitor: 'Monitor',
  laptop: 'Laptop',
  case: 'Case',
  soundcard: 'Sound Card',
  other: 'Other',
}

function isAnySelected(): boolean {
  return model.value === null
}

function selectAny() {
  model.value = null
}

function toggleCategory(category: Category) {
  if (!model.value) {
    model.value = [category]
  } else if (model.value.includes(category)) {
    if (model.value.length === 1) {
      model.value = null
    } else {
      model.value = model.value.filter(c => c !== category)
    }
  } else {
    model.value = [...model.value, category]
  }
}

function isSelected(category: Category): boolean {
  if (!model.value) return false
  return model.value.includes(category)
}
</script>

<template>
  <div class="space-y-3">
    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
      Category
    </label>
    
    <div class="flex flex-wrap gap-2">
      <button
        type="button"
        class="px-3 py-1.5 text-sm rounded-md border transition-colors"
        :class="isAnySelected()
          ? 'bg-blue-500 text-white border-blue-500'
          : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:border-gray-400'"
        @click="selectAny"
      >
        ANY
      </button>
    </div>

    <div class="space-y-3">
      <div v-for="group in categoryGroups" :key="group.label" class="space-y-2">
        <p class="text-[11px] font-medium text-gray-400 uppercase tracking-wide">
          {{ group.label }}
        </p>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="category in group.categories"
            :key="category"
            type="button"
            class="px-3 py-1.5 text-sm rounded-md border transition-colors"
            :class="isSelected(category)
              ? 'bg-blue-500 text-white border-blue-500'
              : 'bg-800 text-gray-white dark:bg-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:border-gray-400'"
            @click="toggleCategory(category)"
          >
            {{ categoryLabels[category] }}
          </button>
        </div>
      </div>
    </div>

    <div class="pt-2">
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        Topics
      </label>
      <div class="relative" @mouseenter="isTooltipVisible = true" @mouseleave="isTooltipVisible = false">
        <label class="flex items-center gap-2 cursor-pointer">
          <input
            v-model="standalone"
            type="checkbox"
            class="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
          />
          <span class="text-sm text-gray-700 dark:text-gray-300">Standalone only</span>
        </label>
        <div
          v-if="isTooltipVisible"
          role="tooltip"
          class="absolute top-full left-0 mt-2 z-50 w-64 p-3 bg-gray-900 text-white text-xs rounded-lg shadow-lg"
        >
          Show only items from topics with a single listing
        </div>
      </div>
    </div>
  </div>
</template>
