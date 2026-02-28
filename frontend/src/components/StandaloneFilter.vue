<script setup lang="ts">
const model = defineModel<boolean>({ required: true })
</script>

<template>
  <div class="space-y-2">
    <label class="flex items-center gap-2 cursor-pointer">
      <input
        v-model="model"
        type="checkbox"
        class="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
      />
      <span class="text-sm text-gray-700 dark:text-gray-300">Standalone only</span>
    </label>
    <p class="text-xs text-gray-500 dark:text-gray-400 ml-6">
      Show only items from topics with a single listing
    </p>
  </div>
</template>
