<script setup lang="ts">
import ItemCard from './ItemCard.vue'
import type { SearchResultItem } from '../types/search'

defineProps<{
  results: SearchResultItem[]
  isLoading: boolean
}>()
</script>

<template>
  <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
    <template v-if="isLoading">
      <div
        v-for="i in 6"
        :key="i"
        class="bg-white/95 dark:bg-gray-800/95 rounded-lg border-2 border-gray-400 dark:border-gray-500 p-4 animate-pulse"
      >
        <div class="flex items-start justify-between gap-2 mb-4">
          <div class="h-5 w-16 bg-gray-200 dark:bg-gray-700 rounded" />
          <div class="h-5 w-12 bg-gray-200 dark:bg-gray-700 rounded" />
        </div>
        <div class="h-6 w-3/4 bg-gray-200 dark:bg-gray-700 rounded mb-3" />
        <div class="flex gap-1 mb-3">
          <div class="h-5 w-16 bg-gray-200 dark:bg-gray-700 rounded" />
          <div class="h-5 w-20 bg-gray-200 dark:bg-gray-700 rounded" />
          <div class="h-5 w-14 bg-gray-200 dark:bg-gray-700 rounded" />
        </div>
        <div class="h-8 w-24 bg-gray-200 dark:bg-gray-700 rounded mb-3" />
        <div class="h-4 w-1/2 bg-gray-200 dark:bg-gray-700 rounded" />
      </div>
    </template>
    
    <ItemCard
      v-else
      v-for="item in results"
      :key="item.item_id"
      :item="item"
    />
  </div>
</template>
