<script setup lang="ts">
import { ref, computed } from 'vue'
import { relativeTime, fullDate } from '../utils/date'
import { formatCurrency } from '../utils/format'
import type { SearchResultItem } from '../types/search'

const props = defineProps<{
  item: SearchResultItem
}>()

const isExpanded = ref(false)
const labelsExpanded = ref(false)

const categoryClass = computed(() => {
  const cat = props.item.category.toLowerCase()
  const classes: Record<string, string> = {
    cpu: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    gpu: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    ram: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    ssd: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
    hdd: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200',
    psu: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
    monitor: 'bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200',
    laptop: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200',
    case: 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200',
    soundcard: 'bg-cyan-100 text-cyan-800 dark:bg-cyan-900 dark:text-cyan-200',
  }
  return classes[cat] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
})

const visibleLabels = computed(() => {
  if (labelsExpanded.value) {
    return props.item.labels
  }
  return props.item.labels.slice(0, 4)
})

const extraLabelsCount = computed(() => Math.max(0, props.item.labels.length - 4))

function toggleExpand() {
  isExpanded.value = !isExpanded.value
  if (!isExpanded.value) {
    labelsExpanded.value = false
  }
}

function toggleLabels(e: Event) {
  e.stopPropagation()
  labelsExpanded.value = !labelsExpanded.value
}

function openTopic(e: Event) {
  e.stopPropagation()
  window.open(props.item.topic_url, '_blank')
}
</script>

<template>
  <article
    class="bg-white/95 dark:bg-gray-800/95 rounded-lg border-2 border-gray-400 dark:border-gray-500 overflow-hidden transition-shadow hover:shadow-lg cursor-pointer"
    :data-expanded="isExpanded"
    @click="toggleExpand"
  >
    <div class="p-4">
      <div class="flex items-start justify-between gap-2 mb-2">
        <span
          class="px-2 py-0.5 text-xs font-medium rounded-full"
          :class="categoryClass"
        >
          {{ item.category.toUpperCase() }}
        </span>
        
        <span
          v-if="!item.is_standalone"
          class="px-2 py-0.5 text-xs font-medium rounded-full bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300"
        >
          Mixed
        </span>
      </div>
      
      <h3 class="text-base font-medium text-gray-900 dark:text-white truncate mb-2">
        {{ item.title }}
      </h3>
      
      <div v-if="item.labels.length > 0" class="flex flex-wrap gap-1 mb-3">
        <span
          v-for="label in visibleLabels"
          :key="label"
          class="px-2 py-0.5 text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 rounded"
        >
          {{ label }}
        </span>
        <button
          v-if="extraLabelsCount > 0"
          type="button"
          class="px-2 py-0.5 text-xs bg-gray-100 dark:bg-gray-700 text-blue-600 dark:text-blue-400 hover:underline"
          @click="toggleLabels"
        >
          {{ labelsExpanded ? 'Show less' : `+${extraLabelsCount} more` }}
        </button>
      </div>
      
      <p class="text-xl font-bold text-gray-900 dark:text-white mb-3">
        {{ formatCurrency(item.price, item.currency) }}
      </p>
      
      <div class="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400">
        <div class="flex flex-wrap items-center gap-x-2 gap-y-1">
          <span>{{ item.author }}</span>
          <span>·</span>
          <span class="text-green-600 dark:text-green-400" :title="`Created: ${fullDate(item.created_at)}`">
            {{ relativeTime(item.created_at) }}
          </span>
          <span v-if="item.created_at !== item.last_update_at" class="text-gray-400 dark:text-gray-500" :title="`Updated: ${fullDate(item.last_update_at)}`">
            ({{ relativeTime(item.last_update_at) }})
          </span>
        </div>
        
        <button
          type="button"
          class="text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-1"
          @click="openTopic"
        >
          → Topic
        </button>
      </div>
    </div>
    
    <div
      v-show="isExpanded"
      class="border-t border-gray-200 dark:border-gray-700 p-4 bg-gray-50 dark:bg-gray-750"
    >
      <div class="border-l-4 border-gray-300 dark:border-gray-600 pl-4">
        <p class="text-sm text-gray-600 dark:text-gray-300 font-mono whitespace-pre-wrap">
          {{ item.raw_text_segment }}
        </p>
      </div>
      
      <div class="mt-4 flex justify-end gap-2">
        <a
          :href="item.topic_url"
          target="_blank"
          class="px-3 py-1.5 text-sm text-blue-600 dark:text-blue-400 border border-blue-600 dark:border-blue-400 rounded hover:bg-blue-50 dark:hover:bg-gray-700"
        >
          → Open Topic
        </a>
        <button
          type="button"
          class="px-3 py-1.5 text-sm text-gray-600 dark:text-gray-400 border border-gray-300 dark:border-gray-600 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
          @click="isExpanded = false"
        >
          ✕
        </button>
      </div>
    </div>
  </article>
</template>
