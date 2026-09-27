<template>
  <div class="space-y-10">
    <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
      <div class="panel overflow-hidden">
        <div class="panel-header justify-between">
          <label for="free-offer">{{ t('cvInput.offerHeader') }}</label>
          <FileText class="h-3.5 w-3.5" aria-hidden="true" />
        </div>
        <div class="p-4 sm:p-5">
          <Textarea id="free-offer" v-model="offerText" :placeholder="t('freeTrial.offerPlaceholder')" class="min-h-[220px]" />
        </div>
      </div>

      <div class="panel overflow-hidden">
        <div class="panel-header justify-between">
          <span id="free-cv-label">{{ t('cvInput.cvHeader') }}</span>
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
          <FreeTrialPDFUpload v-if="activeTab === 'upload'" :model-value="cvText" @update:model-value="(v) => { cvText = v }" />
          <Textarea v-else v-model="cvText" aria-labelledby="free-cv-label" :placeholder="t('freeTrial.cvPlaceholder')" class="min-h-[220px]" />
        </div>
      </div>
    </div>

    <div class="mx-auto flex max-w-xl flex-col items-center gap-4">
      <div v-if="loading" class="w-full space-y-2">
        <div class="flex items-center justify-between font-mono text-micro uppercase text-ink-soft">
          <span>{{ status }}</span>
          <span>{{ Math.round(progress) }}%</span>
        </div>
        <div
          class="progress-track"
          role="progressbar"
          :aria-label="t('comparison.progressAria')"
          :aria-valuenow="Math.round(progress)"
          aria-valuemin="0"
          aria-valuemax="100"
        >
          <div class="progress-fill" :style="{ width: progress + '%' }"></div>
        </div>
      </div>

      <Button :disabled="!hasData || loading || !canAnalyze" size="lg" @click="compareCVWithOffer">
        <Loader2 v-if="loading" class="mr-2 h-4 w-4 animate-spin" aria-hidden="true" />
        <ArrowRightLeft v-else class="mr-2 h-4 w-4" aria-hidden="true" />
        {{ canAnalyze ? t('freeTrial.run') : t('freeTrial.alreadyUsed') }}
      </Button>
    </div>

    <LlmErrorNotice v-if="error" :message="error" :code="errorCode" />

    <div v-if="comparisonResult" class="space-y-8">
      <div class="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <div class="panel p-5 text-center">
          <div class="mb-1 font-mono text-micro uppercase text-ink-soft">{{ t('comparison.stats.matches') }}</div>
          <div class="text-3xl font-medium tabular-nums text-emerald-600">{{ comparisonResult.summary.matches }}</div>
        </div>
        <div class="panel p-5 text-center">
          <div class="mb-1 font-mono text-micro uppercase text-ink-soft">{{ t('comparison.stats.missing') }}</div>
          <div class="text-3xl font-medium tabular-nums text-rose-600">{{ comparisonResult.summary.missing }}</div>
        </div>
        <div class="panel p-5 text-center">
          <div class="mb-1 font-mono text-micro uppercase text-ink-soft">{{ t('comparison.stats.unclear') }}</div>
          <div class="text-3xl font-medium tabular-nums text-amber-600">{{ comparisonResult.summary.unclear }}</div>
        </div>
        <div class="panel p-5 text-center">
          <div class="mb-1 font-mono text-micro uppercase text-ink-soft">{{ t('comparison.stats.score') }}</div>
          <div class="text-3xl font-medium tabular-nums">{{ formatPercent(comparisonResult.summary.matchPercentage) }}</div>
        </div>
      </div>

      <div class="panel-dark">
        <div class="panel-dark-inner">
          <div class="panel-dark-header">{{ t('freeTrial.report') }}</div>
          <div class="space-y-0 p-4 sm:p-6">
            <div
              v-for="item in comparisonResult.items"
              :key="item.id"
              class="border-b border-white/5 py-4 last:border-0"
            >
              <div class="flex items-start justify-between gap-4">
                <div class="flex-1 space-y-2">
                  <div class="font-mono text-micro uppercase text-paper/60">{{ item.category }}</div>
                  <p class="text-sm text-paper/90">{{ item.offerText }}</p>
                  <p v-if="item.cvText" class="text-xs text-paper/60">
                    <span class="text-paper/70">{{ t('comparison.cvExcerpt') }}</span> {{ item.cvText }}
                  </p>
                  <div v-if="item.suggestions?.length" class="mt-3 space-y-1.5 border-t border-white/10 pt-3">
                    <div class="font-mono text-micro uppercase text-paper/60">{{ t('comparison.rewrites') }}</div>
                    <ul class="space-y-1.5 text-xs text-paper/70">
                      <li v-for="sug in item.suggestions" :key="sug" class="flex items-start justify-between gap-3">
                        <span>{{ sug }}</span>
                        <button type="button" :aria-label="t('comparison.copyAria')" @click="copyToClipboard(sug)" class="shrink-0 font-mono text-micro uppercase text-paper/60 hover:text-paper">{{ t('common.copy') }}</button>
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

      <div class="panel p-8 text-center">
        <h3 class="mb-2 font-medium text-title">{{ t('freeTrial.upsell.title') }}</h3>
        <p class="mx-auto mb-6 max-w-md text-lead text-ink-soft">
          {{ t('freeTrial.upsell.text') }}
        </p>
        <div class="flex flex-col items-center justify-center gap-3 sm:flex-row">
          <Button @click="push('/register')">{{ t('freeTrial.upsell.register') }}</Button>
          <Button variant="outline" @click="push('/login')">{{ t('freeTrial.upsell.login') }}</Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { FileText, ArrowRightLeft, Loader2 } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { streamFreeCompare, checkFreeAnalysisStatus } from '@/lib/api'
import { useLocale } from '@/i18n/useLocale'
import FreeTrialPDFUpload from './FreeTrialPDFUpload.vue'
import LlmErrorNotice from '@/components/LlmErrorNotice.vue'
import posthog from 'posthog-js'

const { t } = useI18n()
const { push, formatPercent } = useLocale()

const offerText = ref('')
const cvText = ref('')
const loading = ref(false)
const status = ref('')
const progress = ref(0)
const error = ref('')
const errorCode = ref<string | null>(null)
const comparisonResult = ref<any>(null)
const canAnalyze = ref(true)
const activeTab = ref('upload')

const hasData = computed(() => offerText.value.trim() && cvText.value.trim())

onMounted(async () => {
  try {
    const statusData = await checkFreeAnalysisStatus()
    canAnalyze.value = statusData.can_use_free_analysis
  } catch (err) {
    console.error('Erreur de statut:', err)
  }
})

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

const compareCVWithOffer = async () => {
  if (!hasData.value || loading.value || !canAnalyze.value) return

  loading.value = true
  error.value = ''
  errorCode.value = null
  status.value = t('freeTrial.running')
  progress.value = 0
  comparisonResult.value = null

  try {
    const items: any[] = []
    let summary: any = null

    await streamFreeCompare(
      offerText.value,
      cvText.value,
      (m: string) => { status.value = m },
      (p: number) => { progress.value = p },
      (item: any) => { items.push(item) },
      (sData: any) => { summary = sData },
      () => {
        loading.value = false
        comparisonResult.value = { items, summary }
        canAnalyze.value = false
        posthog.capture('free_trial_comparison_completed', { comparison_mode: 'free_trial' })
      },
      (eMsg: string, code?: string) => {
        loading.value = false
        error.value = eMsg
        errorCode.value = code || null
      },
    )
  } catch (err: any) {
    loading.value = false
    error.value = err.message || t('comparison.errors.generic')
  }
}
</script>
