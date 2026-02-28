<script setup lang="ts">
const modelFrom = defineModel<string | null>('dateFrom')
const modelTo = defineModel<string | null>('dateTo')

type DatePreset = 'last7' | 'last30' | 'last3m' | 'custom'

const presets: { value: DatePreset; label: string }[] = [
  { value: 'last7', label: 'Last 7 days' },
  { value: 'last30', label: 'Last 30 days' },
  { value: 'last3m', label: 'Last 3 months' },
  { value: 'custom', label: 'Custom' },
]

function formatDate(date: Date): string {
  return date.toISOString().split('T')[0]
}

function applyPreset(preset: DatePreset) {
  const today = new Date()
  
  if (preset === 'custom') {
    modelFrom.value = null
    modelTo.value = null
    return
  }
  
  let fromDate: Date
  
  if (preset === 'last7') {
    fromDate = new Date(today)
    fromDate.setDate(today.getDate() - 7)
  } else if (preset === 'last30') {
    fromDate = new Date(today)
    fromDate.setDate(today.getDate() - 30)
  } else if (preset === 'last3m') {
    fromDate = new Date(today)
    fromDate.setMonth(today.getMonth() - 3)
  }
  
  modelFrom.value = formatDate(fromDate)
  modelTo.value = formatDate(today)
}

function isPresetActive(preset: DatePreset): boolean {
  if (preset === 'custom') {
    return !modelFrom.value && !modelTo.value
  }
  
  if (!modelFrom.value || !modelTo.value) return false
  
  const today = new Date()
  const from = new Date(modelFrom.value)
  const to = new Date(modelTo.value)
  const todayStr = formatDate(today)
  
  if (modelTo.value !== todayStr) return false
  
  if (preset === 'last7') {
    const expectedFrom = new Date(today)
    expectedFrom.setDate(today.getDate() - 7)
    return formatDate(expectedFrom) === modelFrom.value
  } else if (preset === 'last30') {
    const expectedFrom = new Date(today)
    expectedFrom.setDate(today.getDate() - 30)
    return formatDate(expectedFrom) === modelFrom.value
  } else if (preset === 'last3m') {
    const expectedFrom = new Date(today)
    expectedFrom.setMonth(today.getMonth() - 3)
    return formatDate(expectedFrom) === modelFrom.value
  }
  
  return false
}
</script>

<template>
  <div class="space-y-2">
    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
      Date range
    </label>
    
    <div class="flex flex-wrap gap-2 mb-2">
      <button
        v-for="preset in presets"
        :key="preset.value"
        type="button"
        class="px-3 py-1 text-sm rounded-full border transition-colors"
        :class="isPresetActive(preset.value)
          ? 'bg-blue-500 text-white border-blue-500'
          : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:border-gray-400'"
        @click="applyPreset(preset.value)"
      >
        {{ preset.label }}
      </button>
    </div>
    
    <div class="flex items-center gap-2">
      <div class="flex items-center gap-1">
        <span class="text-xs text-gray-500">From</span>
        <input
          v-model="modelFrom"
          type="date"
          class="w-28 px-2 py-1.5 text-sm rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
      <div class="flex items-center gap-1">
        <span class="text-xs text-gray-500">To</span>
        <input
          v-model="modelTo"
          type="date"
          class="w-28 px-2 py-1.5 text-sm rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
    </div>
  </div>
</template>
