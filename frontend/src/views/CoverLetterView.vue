<template>
  <div class="page-shell">
    <AppPageHeader
      :label="t('coverLetter.label')"
      :title="t('coverLetter.title')"
      :description="t('coverLetter.description')"
    />
    <AppStatus v-if="historyLoading" class="mb-6" kind="loading" :message="t('coverLetter.historyLoading')" />
    <AppStatus
      v-else-if="historyError"
      class="mb-6"
      kind="error"
      :message="historyError"
      :action-label="t('common.retry')"
      @action="pendingHistoryId && loadHistory(pendingHistoryId)"
    />
    <ApplicationContextBanner
      edit-target="cover-letter-offer"
      :proposal="store.historyContext"
      @adopt="store.adoptHistoryContext"
      @dismiss="store.dismissHistoryContext"
    />

    <div class="space-y-10">
      <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <!-- Offre -->
        <div class="panel overflow-hidden">
          <label for="cover-letter-offer" class="panel-header">{{ t('cvInput.offerHeader') }}</label>
          <div class="p-4 sm:p-5">
            <Textarea
              id="cover-letter-offer"
              :model-value="context.offerText"
              :placeholder="t('coverLetter.offerPlaceholder')"
              class="min-h-[220px]"
              @update:model-value="(value) => context.setOffer(String(value), { from: 'coverLetter' })"
            />
          </div>
        </div>

        <!-- CV -->
        <div class="panel overflow-hidden">
          <div class="panel-header justify-between">
            <span id="cover-letter-cv-label">{{ t('cvInput.cvHeader') }}</span>
            <div class="flex gap-1" role="group" :aria-label="t('cvInput.cvFormat')">
              <button
                v-for="tab in cvTabs"
                :key="tab.value"
                type="button"
                :aria-pressed="cvTab === tab.value"
                class="rounded px-2 py-0.5 transition-colors"
                :class="cvTab === tab.value ? 'bg-ink text-paper' : 'text-ink-soft hover:text-ink'"
                @click="cvTab = tab.value"
              >
                {{ tab.label }}
              </button>
            </div>
          </div>
          <div class="p-4 sm:p-5">
            <SavedCvPicker module="coverLetter" class="mb-4" />
            <PDFUpload
              v-if="cvTab === 'upload'"
              :model-value="context.cvText"
              :file-name="context.cvFileName"
              allow-txt
              @update:model-value="(value) => context.setCv(value, { from: 'coverLetter' })"
              @update:file-name="(name) => (context.cvFileName = name)"
            />
            <Textarea
              v-else
              :model-value="context.cvText"
              @update:model-value="(value) => context.setCv(String(value), { from: 'coverLetter' })"
              aria-labelledby="cover-letter-cv-label"
              :placeholder="t('coverLetter.cvPlaceholder')"
              class="min-h-[220px]"
            />
          </div>
        </div>
      </div>

      <!-- Options -->
      <div class="panel overflow-hidden">
        <div class="panel-header">{{ t('coverLetter.options.header') }}</div>
        <div class="grid grid-cols-1 gap-6 p-4 sm:p-5 lg:grid-cols-3">
          <fieldset v-for="group in optionGroups" :key="group.name" class="min-w-0">
            <legend class="field-label mb-3">{{ group.legend }}</legend>
            <div class="flex flex-wrap gap-2">
              <label
                v-for="option in group.options"
                :key="option.value"
                class="cursor-pointer rounded-lg border px-3 py-2 font-mono text-micro uppercase transition-colors focus-within:ring-2 focus-within:ring-ink/60"
                :class="group.model.value === option.value ? 'border-ink bg-ink text-paper' : 'border-ink/20 text-ink-soft hover:border-ink/50 hover:text-ink'"
              >
                <input
                  v-model="group.model.value"
                  type="radio"
                  class="sr-only"
                  :name="`cover-letter-${group.name}`"
                  :value="option.value"
                  :disabled="store.loading"
                />
                {{ option.label }}
              </label>
            </div>
          </fieldset>
        </div>
      </div>

      <div class="mx-auto flex max-w-xl flex-col items-center gap-4">
        <div v-if="store.loading" class="w-full space-y-2">
          <div class="flex items-center justify-between font-mono text-micro uppercase text-ink-soft">
            <span>{{ store.status }}</span>
            <span>{{ Math.round(store.progress) }}%</span>
          </div>
          <div
            class="progress-track"
            role="progressbar"
            :aria-label="t('coverLetter.progressAria')"
            :aria-valuenow="Math.round(store.progress)"
            aria-valuemin="0"
            aria-valuemax="100"
          >
            <div class="progress-fill" :style="{ width: store.progress + '%' }"></div>
          </div>
        </div>

        <Button :disabled="!store.hasData || store.loading" size="lg" @click="store.generate">
          <Loader2 v-if="store.loading" class="mr-2 h-4 w-4 animate-spin" aria-hidden="true" />
          <PenLine v-else class="mr-2 h-4 w-4" aria-hidden="true" />
          {{ store.letter && !store.loading ? t('coverLetter.regenerate') : t('coverLetter.run') }}
        </Button>
      </div>

      <LlmErrorNotice v-if="store.error" :message="store.error" :code="store.errorCode" />

      <section v-if="store.letter" :aria-busy="store.loading" aria-labelledby="cover-letter-result">
        <div class="panel overflow-hidden">
          <div class="panel-header flex-wrap justify-between gap-2 !h-auto min-h-10 py-2">
            <h2 id="cover-letter-result">{{ t('coverLetter.result') }}</h2>
            <div v-if="!store.loading" class="flex flex-wrap gap-2">
              <Button variant="outline" size="sm" @click="copyLetter">
                <Check v-if="copied" class="h-3.5 w-3.5" aria-hidden="true" />
                <Copy v-else class="h-3.5 w-3.5" aria-hidden="true" />
                {{ copied ? t('coverLetter.copied') : t('common.copy') }}
              </Button>
              <Button
                v-for="format in formats"
                :key="format"
                variant="outline"
                size="sm"
                :aria-label="t('coverLetter.downloadAria', { format })"
                @click="download(format)"
              >
                <Download class="h-3.5 w-3.5" aria-hidden="true" />
                .{{ format }}
              </Button>
            </div>
          </div>
          <article class="mx-auto max-w-[68ch] space-y-5 p-6 text-[15px] leading-relaxed text-ink sm:p-10" :lang="store.letter.language || undefined">
            <p v-if="store.letter.subject" class="font-medium">{{ store.letter.subject }}</p>
            <p v-if="store.letter.greeting">{{ store.letter.greeting }}</p>
            <p v-if="store.letter.opening">{{ store.letter.opening }}</p>
            <p v-for="(paragraph, index) in store.letter.body" :key="index">{{ paragraph }}</p>
            <p v-if="store.letter.closing">{{ store.letter.closing }}</p>
            <p v-if="store.letter.signoff">{{ store.letter.signoff }}</p>
            <p v-if="store.letter.signature" class="pt-2">{{ store.letter.signature }}</p>
          </article>
          <div v-if="!store.loading" class="border-t border-ink/10">
            <p class="mx-auto max-w-[68ch] px-6 py-4 font-mono text-micro uppercase text-ink-soft sm:px-10">
              {{ t('coverLetter.reviewHint') }}
            </p>
          </div>
        </div>
      </section>
      <p class="sr-only" aria-live="polite">{{ liveMessage }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { Check, Copy, Download, Loader2, PenLine } from 'lucide-vue-next'
import posthog from 'posthog-js'
import AppPageHeader from '@/components/AppPageHeader.vue'
import AppStatus from '@/components/AppStatus.vue'
import ApplicationContextBanner from '@/components/ApplicationContextBanner.vue'
import PDFUpload from '@/components/PDFUpload.vue'
import SavedCvPicker from '@/components/SavedCvPicker.vue'
import LlmErrorNotice from '@/components/LlmErrorNotice.vue'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { useCvInputTab } from '@/composables/useCvInputTab'
import { useLocale } from '@/i18n/useLocale'
import { downloadCoverLetter, formatCoverLetter, type CoverLetterFormat } from '@/lib/coverLetter'
import { isOnline } from '@/lib/pwa'
import { useApplicationContextStore } from '@/stores/applicationContext'
import { useCoverLetterStore } from '@/stores/coverLetter'

const { t } = useI18n()
const { replace } = useLocale()
const route = useRoute()
const store = useCoverLetterStore()
const context = useApplicationContextStore()

const cvTab = useCvInputTab()
const cvTabs = computed(() => [
  { value: 'upload' as const, label: t('coverLetter.cvFile') },
  { value: 'manual' as const, label: t('common.text') },
])

const tone = computed({ get: () => store.tone, set: (value) => (store.tone = value) })
const length = computed({ get: () => store.length, set: (value) => (store.length = value) })
const language = computed({ get: () => store.language, set: (value) => (store.language = value) })

const optionGroups = computed(() => [
  {
    name: 'tone',
    legend: t('coverLetter.options.tone'),
    model: tone,
    options: (['professional', 'warm', 'confident', 'formal'] as const).map((value) => ({
      value,
      label: t(`coverLetter.tones.${value}`),
    })),
  },
  {
    name: 'length',
    legend: t('coverLetter.options.length'),
    model: length,
    options: (['short', 'standard', 'detailed'] as const).map((value) => ({
      value,
      label: t(`coverLetter.lengths.${value}`),
    })),
  },
  {
    name: 'language',
    legend: t('coverLetter.options.language'),
    model: language,
    options: (['auto', 'fr', 'en'] as const).map((value) => ({
      value,
      label: t(`coverLetter.languages.${value}`),
    })),
  },
])

// --- Copier / télécharger ----------------------------------------------------

const formats: CoverLetterFormat[] = ['txt', 'md']
const copied = ref(false)
const liveMessage = ref('')
let copiedTimer: ReturnType<typeof setTimeout> | undefined

function analyticsProps() {
  return { tone: store.tone, length: store.length, letter_language: store.letter?.language || null }
}

async function copyLetter() {
  if (!store.letter) return
  try {
    await navigator.clipboard.writeText(formatCoverLetter(store.letter, 'txt'))
    copied.value = true
    liveMessage.value = t('coverLetter.copied')
    posthog.capture('cover_letter_copied', analyticsProps())
    clearTimeout(copiedTimer)
    copiedTimer = setTimeout(() => (copied.value = false), 2000)
  } catch {
    liveMessage.value = t('coverLetter.errors.copy')
  }
}

function download(format: CoverLetterFormat) {
  if (!store.letter) return
  downloadCoverLetter(store.letter, format, t('coverLetter.filename'))
  posthog.capture('cover_letter_downloaded', { ...analyticsProps(), format })
}

// --- Relecture depuis l'historique (?history=…) -------------------------------

const historyLoading = ref(false)
const historyError = ref('')
const pendingHistoryId = ref<string | null>(null)

// L'id est gardé tant que le chargement échoue (hors ligne) : nouvel essai au retour du réseau
async function loadHistory(historyId: string) {
  historyLoading.value = true
  historyError.value = ''
  try {
    await store.loadFromHistory(historyId)
    pendingHistoryId.value = null
    replace({ path: '/cover-letter', query: {} })
  } catch {
    historyError.value = store.error || t('coverLetter.errors.loadHistory')
    store.error = null
    pendingHistoryId.value = historyId
  } finally {
    historyLoading.value = false
  }
}

watch(
  () => store.loading,
  (loading, wasLoading) => {
    if (wasLoading && !loading) liveMessage.value = store.error || (store.letter ? t('coverLetter.statusDone') : '')
  },
)

onMounted(() => {
  context.trackReuse('coverLetter')
  const historyId = typeof route.query.history === 'string' ? route.query.history : null
  if (historyId) loadHistory(historyId)
})

watch(isOnline, (online) => {
  if (online && pendingHistoryId.value) loadHistory(pendingHistoryId.value)
})

onUnmounted(() => clearTimeout(copiedTimer))
</script>
