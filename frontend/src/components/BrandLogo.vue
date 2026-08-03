<template>
  <component :is="tag" :class="['inline-flex items-center gap-2', props.class]">
    <img
      :src="logoSrc"
      :alt="alt"
      :class="imageClass"
      class="shrink-0 object-contain"
    />
    <span v-if="showWordmark" :class="wordmarkClass">{{ wordmark }}</span>
  </component>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    tag?: string
    size?: 'sm' | 'md' | 'lg'
    showWordmark?: boolean
    wordmark?: string
    class?: string
    wordmarkClass?: string
  }>(),
  {
    tag: 'span',
    size: 'md',
    showWordmark: true,
    wordmark: 'Talento',
    class: '',
    wordmarkClass: 'font-mono text-caption uppercase tracking-wide',
  },
)

const logoSrc = '/logo.png'
const alt = 'Talento'

const imageClass = computed(() => {
  switch (props.size) {
    case 'sm':
      return 'h-6 w-6'
    case 'lg':
      return 'h-9 w-9'
    default:
      return 'h-7 w-7'
  }
})
</script>
