<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { fetchStats, type StatsResponse } from '../api/stats'
import { exactTime, relativeTime } from '../utils/date'

const lastScrapeAt = ref<string | null>(null)
const loading = ref(true)
const error = ref(false)

const REFRESH_INTERVAL = 5 * 60 * 1000 // 5 minutes

async function loadStats() {
  try {
    const stats: StatsResponse = await fetchStats()
    lastScrapeAt.value = stats.last_scrape_at
    error.value = false
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
}

let intervalId: number | undefined

onMounted(() => {
  loadStats()
  intervalId = window.setInterval(loadStats, REFRESH_INTERVAL)
})

onUnmounted(() => {
  if (intervalId) {
    clearInterval(intervalId)
  }
})
</script>

<template>
  <header class="bg-white/95 dark:bg-gray-800/95 shadow-md border-b-2 border-gray-500 dark:border-gray-400">
    <div class="max-w-7xl mx-auto px-4 py-4">
      <h1 class="text-2xl font-bold text-black dark:text-white">
        OCBot
      </h1>
      <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
        Search used computer parts from Overclockers.ua
      </p>
      <p v-if="loading" class="text-xs text-gray-500 dark:text-gray-500 mt-1">
        Loading...
      </p>
      <p v-else-if="error" class="text-xs text-red-500 dark:text-red-400 mt-1">
        Data last updated: N/A
      </p>
      <p v-else-if="lastScrapeAt" class="text-xs text-gray-500 dark:text-gray-500 mt-1">
        Data last updated: {{ exactTime(lastScrapeAt) }} ({{ relativeTime(lastScrapeAt) }})
      </p>
      <p v-else class="text-xs text-gray-500 dark:text-gray-500 mt-1">
        Data last updated: N/A
      </p>
    </div>
  </header>
</template>
