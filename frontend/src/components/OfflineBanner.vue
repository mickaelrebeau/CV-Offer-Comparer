<template>
  <div
    role="status"
    aria-live="polite"
    class="pointer-events-none fixed inset-x-0 bottom-4 z-[95] flex justify-center px-4"
  >
    <p
      v-if="!isOnline"
      class="pointer-events-auto flex items-center gap-2 rounded-full border border-ink/15 bg-ink px-4 py-2 font-mono text-micro uppercase text-paper shadow-lg"
    >
      <WifiOff class="h-3.5 w-3.5" aria-hidden="true" />
      {{ t('pwa.offline') }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { WifiOff } from 'lucide-vue-next'
import { isOnline } from '@/lib/pwa'

const { t } = useI18n()
</script>
