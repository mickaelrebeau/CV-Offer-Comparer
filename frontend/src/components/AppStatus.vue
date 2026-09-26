<template>
  <!-- États communs des pages connectées : chargement, vide, erreur (avec relance) -->
  <div
    :role="kind === 'error' ? 'alert' : 'status'"
    class="panel flex flex-col items-start gap-4 p-6 sm:p-8"
    :class="{
      'border-rose-500/25 bg-rose-500/5': kind === 'error',
      'py-10 sm:py-12': centered,
      'items-center text-center': centered,
    }"
  >
    <div class="flex items-center gap-3">
      <Loader2 v-if="kind === 'loading'" class="h-4 w-4 shrink-0 animate-spin text-ink-soft" aria-hidden="true" />
      <AlertCircle v-else-if="kind === 'error'" class="h-4 w-4 shrink-0 text-rose-700" aria-hidden="true" />
      <p :class="messageClass">{{ message }}</p>
    </div>
    <p v-if="kind === 'error' && !isOnline" class="font-mono text-micro uppercase text-ink-soft">
      {{ t('pwa.retryWhenOnline') }}
    </p>
    <button
      v-if="actionLabel"
      type="button"
      :class="kind === 'empty' ? 'btn-primary' : 'btn-secondary h-9 px-4 text-micro'"
      @click="emit('action')"
    >
      {{ actionLabel }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { AlertCircle, Loader2 } from 'lucide-vue-next'
import { isOnline } from '@/lib/pwa'

const props = withDefaults(
  defineProps<{
    kind: 'loading' | 'empty' | 'error'
    message: string
    actionLabel?: string
    centered?: boolean
  }>(),
  { actionLabel: undefined, centered: false },
)

const emit = defineEmits<{ action: [] }>()
const { t } = useI18n()

const messageClass = computed(() => {
  if (props.kind === 'empty') return 'text-lead text-ink-soft'
  return ['font-mono text-micro uppercase', props.kind === 'error' ? 'text-rose-700' : 'text-ink-soft']
})
</script>
