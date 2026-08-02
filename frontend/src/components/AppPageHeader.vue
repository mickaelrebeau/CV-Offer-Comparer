<template>
  <header class="mb-10 space-y-4 lg:mb-14">
    <p v-if="label" class="font-mono text-caption uppercase text-ink-soft">
      {{ label }}
    </p>
    <h1 class="max-w-[22ch] text-balance font-medium text-headline">
      {{ title }}
    </h1>
    <p v-if="description" class="max-w-[52ch] text-lead text-ink-soft">
      {{ description }}
    </p>
    <slot />
  </header>
</template>

<script setup lang="ts">
defineProps<{
  label?: string
  title: string
  description?: string
}>()
</script>
