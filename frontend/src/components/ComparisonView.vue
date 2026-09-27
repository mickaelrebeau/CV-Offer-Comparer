<template>
  <div class="space-y-10">
    <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
      <!-- Offre -->
      <div class="panel overflow-hidden">
        <div class="panel-header justify-between">
          <label for="compare-offer">{{ t('cvInput.offerHeader') }}</label>
          <FileText class="h-3.5 w-3.5" aria-hidden="true" />
        </div>
        <div class="p-4 sm:p-5">
          <Textarea
            id="compare-offer"
            :model-value="compareStore.offerText"
            :placeholder="t('comparison.offerPlaceholder')"
            class="min-h-[220px]"
            @input="handleOfferInput"
          />
        </div>
      </div>

      <!-- CV -->
      <div class="panel overflow-hidden">
        <div class="panel-header justify-between">
          <span id="compare-cv-label">{{ t('cvInput.cvHeader') }}</span>
          <div class="flex gap-1" role="group" :aria-label="t('cvInput.cvFormat')">
            <button
              type="button"
              :aria-pressed="activeTab === 'upload'"
              @click="activeTab = 'upload'"
              class="rounded px-2 py-0.5 transition-colors"
              :class="activeTab === 'upload' ? 'bg-ink text-paper' : 'text-ink-soft hover:text-ink'"
            >
              {{ t('common.pdf') }}
            </button>
            <button
              type="button"
              :aria-pressed="activeTab === 'manual'"
              @click="activeTab = 'manual'"
              class="rounded px-2 py-0.5 transition-colors"
              :class="activeTab === 'manual' ? 'bg-ink text-paper' : 'text-ink-soft hover:text-ink'"
            >
              {{ t('common.text') }}
            </button>
          </div>
        </div>
        <div class="p-4 sm:p-5">
          <PDFUpload v-if="activeTab === 'upload'" :model-value="compareStore.cvText" @update:model-value="(val) => compareStore.updateCVText(val)" />
          <Textarea
            v-else
            aria-labelledby="compare-cv-label"
            :model-value="compareStore.cvText"
            :placeholder="t('comparison.cvPlaceholder')"
            class="min-h-[220px]"
            @input="handleCVInput"
          />
        </div>
      </div>
    </div>

    <div class="mx-auto flex max-w-xl flex-col items-center gap-4">
      <div v-if="compareStore.loading" class="w-full space-y-2">
        <div class="flex items-center justify-between font-mono text-micro uppercase text-ink-soft">
          <span>{{ compareStore.status }}</span>
          <span>{{ Math.round(compareStore.progress) }}%</span>
        </div>
        <div
          class="progress-track"
          role="progressbar"
          :aria-label="t('comparison.progressAria')"
          :aria-valuenow="Math.round(compareStore.progress)"
          aria-valuemin="0"
          aria-valuemax="100"
        >
          <div class="progress-fill" :style="{ width: compareStore.progress + '%' }"></div>
        </div>
      </div>

      <Button
        :disabled="!compareStore.hasData || compareStore.loading"
        size="lg"
        @click="compareStore.compareCVWithOfferStream"
      >
        <Loader2 v-if="compareStore.loading" class="mr-2 h-4 w-4 animate-spin" aria-hidden="true" />
        <ArrowRightLeft v-else class="mr-2 h-4 w-4" aria-hidden="true" />
        {{ t('comparison.run') }}
      </Button>
    </div>

    <LlmErrorNotice v-if="compareStore.error" :message="compareStore.error" :code="compareStore.errorCode" />

    <div v-if="compareStore.comparisonResult" class="space-y-8">
      <div class="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <div v-for="stat in summaryStats" :key="stat.label" class="panel p-5 text-center">
          <div class="mb-1 font-mono text-micro uppercase text-ink-soft">{{ stat.label }}</div>
          <div class="text-3xl font-medium tabular-nums" :class="stat.color">{{ stat.value }}</div>
        </div>
      </div>

      <div class="panel-dark">
        <div class="panel-dark-inner">
          <div class="panel-dark-header">{{ t('comparison.report') }}</div>
          <div class="space-y-0 p-4 sm:p-6">
            <div
              v-for="item in compareStore.comparisonResult.items"
              :key="item.id"
              class="border-b border-white/5 py-4 last:border-0"
            >
              <div class="flex items-start justify-between gap-4">
                <div class="flex-1 space-y-2">
                  <div class="flex flex-wrap items-center gap-3 font-mono text-micro uppercase">
                    <span class="text-paper/60">{{ item.category }}</span>
                    <span class="text-paper/60">{{ t('comparison.confidence', { value: formatPercent(item.confidence) }) }}</span>
                  </div>
                  <p class="text-sm text-paper/90">{{ item.offerText }}</p>
                  <p v-if="item.cvText" class="text-xs text-paper/60">
                    <span class="text-paper/70">{{ t('comparison.cvExcerpt') }}</span> {{ item.cvText }}
                  </p>
                  <div v-if="item.suggestions?.length" class="mt-3 space-y-1.5 border-t border-white/10 pt-3">
                    <div class="font-mono text-micro uppercase text-paper/60">{{ t('comparison.rewrites') }}</div>
                    <ul class="space-y-1.5 text-xs text-paper/70">
                      <li v-for="sug in item.suggestions" :key="sug" class="flex items-start justify-between gap-3">
                        <span>{{ sug }}</span>
                        <button
                          type="button"
                          :aria-label="t('comparison.copyAria')"
                          @click="copyToClipboard(sug)"
                          class="shrink-0 font-mono text-micro uppercase text-paper/60 hover:text-paper"
                        >
                          {{ t('common.copy') }}
                        </button>
                      </li>
                    </ul>
                  </div>
                </div>
                <div class="shrink-0 font-mono text-micro uppercase" :class="statusTone(item.status)">
                  {{ statusLabel(item.status) }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { FileText, ArrowRightLeft, Loader2 } from 'lucide-vue-next'
import { useLocale } from '@/i18n/useLocale'
import { useCompareStore } from '@/stores/compare'
import PDFUpload from './PDFUpload.vue'
import LlmErrorNotice from '@/components/LlmErrorNotice.vue'

const { t } = useI18n()
const { formatPercent } = useLocale()
const compareStore = useCompareStore()
const activeTab = ref<'upload' | 'manual'>('upload')

const summaryStats = computed(() => {
  const s = compareStore.comparisonResult?.summary
  if (!s) return []
  return [
    { label: t('comparison.stats.matches'), value: s.matches, color: 'text-emerald-500' },
    { label: t('comparison.stats.missing'), value: s.missing, color: 'text-rose-500' },
    { label: t('comparison.stats.unclear'), value: s.unclear, color: 'text-amber-500' },
    { label: t('comparison.stats.score'), value: formatPercent(s.matchPercentage), color: 'text-ink' },
  ]
})

const handleOfferInput = (event: Event) => {
  compareStore.updateOfferText((event.target as HTMLTextAreaElement).value)
}

const handleCVInput = (event: Event) => {
  compareStore.updateCVText((event.target as HTMLTextAreaElement).value)
}

const statusTone = (st: string) => {
  if (st === 'match') return 'text-emerald-400'
  if (st === 'missing') return 'text-rose-400'
  return 'text-amber-400'
}

const statusLabel = (st: string) => {
  if (st === 'match') return t('comparison.status.match')
  if (st === 'missing') return t('comparison.status.missing')
  return t('comparison.status.partial')
}

const copyToClipboard = (text: string) => {
  navigator.clipboard.writeText(text)
}
</script>
