<script setup lang="ts">
defineProps<{
  error: string | null
  hasQuery: boolean
}>()
</script>

<template>
  <div class="text-center py-12">
    <template v-if="error">
      <div class="mb-4">
        <svg
          class="mx-auto h-12 w-12 text-red-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          />
        </svg>
      </div>
      <p class="text-red-600 dark:text-red-400 mb-2">
        Search failed — please try again.
      </p>
      <p v-if="error" class="text-sm text-gray-500 dark:text-gray-400">
        {{ error }}
      </p>
    </template>
    
    <template v-else-if="hasQuery">
      <div class="mb-4">
        <svg
          class="mx-auto h-12 w-12 text-blue-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      </div>
      <p class="text-blue-600 dark:text-blue-400">
        Nothing found. Try broader terms or switch to Simple mode.
      </p>
    </template>
    
    <template v-else>
      <div class="mb-4">
        <svg
          class="mx-auto h-12 w-12 text-blue-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
          />
        </svg>
      </div>
      <p class="text-gray-500 dark:text-gray-400">
        Start typing to search for parts
      </p>
    </template>
  </div>
</template>
