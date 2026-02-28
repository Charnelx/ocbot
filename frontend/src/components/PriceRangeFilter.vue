<script setup lang="ts">
import { computed } from 'vue'

const modelMin = defineModel<number | null>('priceMin')
const modelMax = defineModel<number | null>('priceMax')
const currency = defineModel<string>('currency', { required: true })

type PricePreset = 'under100' | '100to300' | '300to600' | 'over600'

const presets: { value: PricePreset; label: string; min: number | null; max: number | null }[] = [
  { value: 'under100', label: 'Under $100', min: null, max: 100 },
  { value: '100to300', label: '$100 – $300', min: 100, max: 300 },
  { value: '300to600', label: '$300 – $600', min: 300, max: 600 },
  { value: 'over600', label: '$600+', min: 600, max: null },
]

const currencySymbol = computed(() => {
  return currency.value === 'USD' ? '$' : '₴'
})

const uahPresets = [
  { value: 'under100', label: 'Under ₴5,000', min: null, max: 5000 },
  { value: '100to300', label: '₴5,000 – ₴15,000', min: 5000, max: 15000 },
  { value: '300to600', label: '₴15,000 – ₴30,000', min: 15000, max: 30000 },
  { value: 'over600', label: '₴30,000+', min: 30000, max: null },
]

const activePresets = computed(() => {
  return currency.value === 'USD' ? presets : uahPresets
})

function isPresetActive(preset: { min: number | null; max: number | null }): boolean {
  return modelMin.value === preset.min && modelMax.value === preset.max
}

function applyPreset(preset: { min: number | null; max: number | null }) {
  modelMin.value = preset.min
  modelMax.value = preset.max
}

function handleMinChange(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.value === '') {
    modelMin.value = null
  } else {
    const val = parseFloat(target.value)
    modelMin.value = isNaN(val) ? null : val
  }
}

function handleMaxChange(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.value === '') {
    modelMax.value = null
  } else {
    const val = parseFloat(target.value)
    modelMax.value = isNaN(val) ? null : val
  }
}
</script>

<template>
  <div class="space-y-2">
    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
      Price range
    </label>
    
    <div class="flex flex-wrap gap-2 mb-2">
      <button
        v-for="preset in activePresets"
        :key="preset.value"
        type="button"
        class="px-3 py-1 text-sm rounded-full border transition-colors"
        :class="isPresetActive(preset)
          ? 'bg-blue-500 text-white border-blue-500'
          : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:border-gray-400'"
        @click="applyPreset(preset)"
      >
        {{ preset.label }}
      </button>
    </div>
    
    <div class="flex items-center gap-2">
      <input
        :value="modelMin ?? ''"
        @input="handleMinChange"
        type="number"
        min="0"
        placeholder="Min"
        class="w-24 px-3 py-1.5 text-sm rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <span class="text-gray-500">—</span>
      <input
        :value="modelMax ?? ''"
        @input="handleMaxChange"
        type="number"
        min="0"
        placeholder="Max"
        class="w-24 px-3 py-1.5 text-sm rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
    </div>
  </div>
</template>
