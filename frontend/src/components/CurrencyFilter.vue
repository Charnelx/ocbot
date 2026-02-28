<script setup lang="ts">
import type { Currency } from '../types/search'

const model = defineModel<Currency>({ required: true })

const currencyOptions: { value: Currency; label: string }[] = [
  { value: 'any', label: 'ANY' },
  { value: 'UAH', label: 'UAH' },
  { value: 'USD', label: 'USD' },
]
</script>

<template>
  <div class="space-y-2">
    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
      Currency
    </label>
    <div class="flex flex-wrap gap-2">
      <button
        v-for="option in currencyOptions"
        :key="option.value"
        type="button"
        class="px-3 py-1.5 text-sm rounded-full border transition-colors"
        :class="model === option.value
          ? 'bg-blue-500 text-white border-blue-500'
          : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:border-gray-400'"
        @click="model = option.value"
      >
        {{ option.label }}
      </button>
    </div>
  </div>
</template>
