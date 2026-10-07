<template>
  <div class="page-shell">
    <AppPageHeader
      :label="t('cvOptimizer.label')"
      :title="t('cvOptimizer.title')"
      :description="t('cvOptimizer.description')"
    />
    <AppStatus v-if="historyLoading" class="mb-6" kind="loading" :message="t('cvOptimizer.historyLoading')" />
    <AppStatus
      v-else-if="historyError"
      class="mb-6"
      kind="error"
      :message="historyError"
      :action-label="t('common.retry')"
      @action="pendingHistoryId && loadHistory(pendingHistoryId)"
    />

    <div class="space-y-10">
      <!-- Garde-fou : reformuler, jamais inventer -->
      <div class="panel flex items-start gap-3 p-5">
        <ShieldCheck class="mt-0.5 h-5 w-5 shrink-0 text-emerald-600" aria-hidden="true" />
        <div>
          <p class="text-sm font-medium text-ink">{{ t('cvOptimizer.guardrail.title') }}</p>
          <p class="mt-1 text-sm text-ink-soft">{{ t('cvOptimizer.guardrail.text') }}</p>
        </div>
      </div>

      <!-- À partir d'une analyse : son CV, son offre et ses exigences manquantes ou floues -->
      <div
        v-if="fromComparisonId"
        class="panel flex flex-col gap-3 p-5 sm:flex-row sm:items-center sm:justify-between"
      >
        <div>
          <p class="font-mono text-micro uppercase text-ink-soft">{{ t('cvOptimizer.fromAnalysis.label') }}</p>
          <p class="mt-1 text-sm text-ink">{{ t('cvOptimizer.fromAnalysis.text') }}</p>
        </div>
        <Button size="sm" variant="outline" class="shrink-0" :disabled="store.loading" @click="fromComparisonId = null">
          {{ t('cvOptimizer.fromAnalysis.useContext') }}
        </Button>
      </div>

      <div v-else class="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <OfferInput module="cvOptimizer" textarea-id="cv-optimizer-offer" :placeholder="t('cvOptimizer.offerPlaceholder')" />

        <div class="panel overflow-hidden">
          <div class="panel-header justify-between">
            <span id="cv-optimizer-cv-label">{{ t('cvInput.cvHeader') }}</span>
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
            <SavedCvPicker module="cvOptimizer" class="mb-4" />
            <PDFUpload
              v-if="cvTab === 'upload'"
              :model-value="context.cvText"
              :file-name="context.cvFileName"
              @update:model-value="(value) => context.setCv(value, { from: 'cvOptimizer' })"
              @update:file-name="(name) => (context.cvFileName = name)"
            />
            <Textarea
              v-else
              :model-value="context.cvText"
              @update:model-value="(value) => context.setCv(String(value), { from: 'cvOptimizer' })"
              aria-labelledby="cv-optimizer-cv-label"
              :placeholder="t('cvOptimizer.cvPlaceholder')"
              class="min-h-[220px]"
            />
          </div>
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
            :aria-label="t('cvOptimizer.progressAria')"
            :aria-valuenow="Math.round(store.progress)"
            aria-valuemin="0"
            aria-valuemax="100"
          >
            <div class="progress-fill" :style="{ width: store.progress + '%' }"></div>
          </div>
        </div>

        <Button :disabled="(!fromComparisonId && !store.hasData) || store.loading" size="lg" @click="run">
          <Loader2 v-if="store.loading" class="mr-2 h-4 w-4 animate-spin" aria-hidden="true" />
          <Sparkles v-else class="mr-2 h-4 w-4" aria-hidden="true" />
          {{ store.suggestions.length && !store.loading ? t('cvOptimizer.rerun') : t('cvOptimizer.run') }}
        </Button>
      </div>

      <LlmErrorNotice v-if="store.error" :message="store.error" :code="store.errorCode" />

      <!-- Propositions -->
      <section v-if="store.suggestions.length" :aria-busy="store.loading" aria-labelledby="cv-optimizer-suggestions" class="space-y-4">
        <div class="flex flex-wrap items-end justify-between gap-3">
          <div>
            <h2 id="cv-optimizer-suggestions" class="font-medium text-title">{{ t('cvOptimizer.suggestions.title') }}</h2>
            <p v-if="store.summary" class="mt-1 text-sm text-ink-soft">{{ store.summary }}</p>
          </div>
          <div v-if="!store.loading" class="flex flex-wrap items-center gap-3">
            <span class="font-mono text-micro uppercase text-ink-soft">
              {{ t('cvOptimizer.suggestions.counts', store.counts) }}
            </span>
            <Button v-if="store.counts.pending" size="sm" variant="outline" @click="store.acceptAll">
              {{ t('cvOptimizer.suggestions.acceptAll') }}
            </Button>
          </div>
        </div>

        <ul class="space-y-3">
          <li
            v-for="suggestion in store.suggestions"
            :key="suggestion.id"
            class="panel overflow-hidden"
            :class="{
              'border-emerald-500/40': decisionOf(suggestion.id).status === 'accepted',
              'opacity-60': decisionOf(suggestion.id).status === 'rejected',
            }"
          >
            <div class="panel-header !h-auto min-h-10 flex-wrap justify-between gap-2 py-2">
              <span>
                {{ suggestion.section || t('cvOptimizer.suggestions.noSection') }}
                <template v-if="suggestion.requirement"> · {{ t('cvOptimizer.suggestions.targets', { requirement: suggestion.requirement }) }}</template>
              </span>
              <span :class="statusTone(decisionOf(suggestion.id).status)">
                {{ t(`cvOptimizer.status.${decisionOf(suggestion.id).status}`) }}
              </span>
            </div>
            <div class="grid gap-4 p-4 sm:p-5 md:grid-cols-2">
              <div>
                <p class="field-label mb-1.5">{{ t('cvOptimizer.suggestions.original') }}</p>
                <p class="whitespace-pre-line text-sm text-ink-soft">{{ suggestion.original }}</p>
              </div>
              <div>
                <label :for="`suggestion-${suggestion.id}`" class="field-label mb-1.5 block">
                  {{ t('cvOptimizer.suggestions.proposed') }}
                </label>
                <Textarea
                  v-if="editingId === suggestion.id"
                  :id="`suggestion-${suggestion.id}`"
                  v-model="draft"
                  class="min-h-[96px] text-sm"
                />
                <p v-else :id="`suggestion-${suggestion.id}`" class="whitespace-pre-line text-sm text-ink">
                  {{ decisionOf(suggestion.id).text }}
                </p>
              </div>
            </div>
            <div class="flex flex-col gap-3 border-t border-ink/10 px-4 py-3 sm:flex-row sm:items-center sm:justify-between sm:px-5">
              <p v-if="suggestion.rationale" class="text-xs text-ink-soft">{{ suggestion.rationale }}</p>
              <div v-if="!store.loading" class="flex shrink-0 flex-wrap gap-2 sm:ml-auto">
                <template v-if="editingId === suggestion.id">
                  <Button size="sm" :disabled="!draft.trim()" @click="saveEdit(suggestion.id)">
                    {{ t('cvOptimizer.actions.saveAndAccept') }}
                  </Button>
                  <Button size="sm" variant="outline" @click="editingId = null">{{ t('common.cancel') }}</Button>
                </template>
                <template v-else-if="decisionOf(suggestion.id).status === 'pending'">
                  <Button size="sm" @click="store.accept(suggestion.id)">
                    <Check class="h-3.5 w-3.5" aria-hidden="true" />
                    {{ t('cvOptimizer.actions.accept') }}
                  </Button>
                  <Button size="sm" variant="outline" @click="startEdit(suggestion.id)">
                    <Pencil class="h-3.5 w-3.5" aria-hidden="true" />
                    {{ t('cvOptimizer.actions.edit') }}
                  </Button>
                  <Button size="sm" variant="outline" @click="store.reject(suggestion.id)">
                    <X class="h-3.5 w-3.5" aria-hidden="true" />
                    {{ t('cvOptimizer.actions.reject') }}
                  </Button>
                </template>
                <Button v-else size="sm" variant="outline" @click="store.reset(suggestion.id)">
                  <Undo2 class="h-3.5 w-3.5" aria-hidden="true" />
                  {{ t('cvOptimizer.actions.undo') }}
                </Button>
              </div>
            </div>
          </li>
        </ul>
      </section>

      <!-- CV optimisé -->
      <section v-if="store.suggestions.length && !store.loading && store.sourceCv" aria-labelledby="cv-optimizer-result">
        <div class="panel overflow-hidden">
          <div class="panel-header !h-auto min-h-10 flex-wrap justify-between gap-2 py-2">
            <h2 id="cv-optimizer-result">{{ t('cvOptimizer.result.title', { count: store.optimized.applied }) }}</h2>
            <div class="flex flex-wrap gap-2">
              <Button
                v-for="format in formats"
                :key="format"
                variant="outline"
                size="sm"
                :aria-label="t('cvOptimizer.result.downloadAria', { format })"
                @click="download(format)"
              >
                <Download class="h-3.5 w-3.5" aria-hidden="true" />
                .{{ format }}
              </Button>
              <Button variant="outline" size="sm" :disabled="saving || savedCvs.limitReached || saved" @click="saveAsNewCv">
                <Loader2 v-if="saving" class="h-3.5 w-3.5 animate-spin" aria-hidden="true" />
                <Check v-else-if="saved" class="h-3.5 w-3.5" aria-hidden="true" />
                <Save v-else class="h-3.5 w-3.5" aria-hidden="true" />
                {{ saved ? t('cvOptimizer.result.saved') : t('cvOptimizer.result.save') }}
              </Button>
              <Button size="sm" :disabled="!store.optimized.applied" @click="rescore">
                <RefreshCw class="h-3.5 w-3.5" aria-hidden="true" />
                {{ t('cvOptimizer.result.rescore') }}
              </Button>
            </div>
          </div>
          <p v-if="savedCvs.limitReached && !saved" class="border-b border-ink/10 px-4 py-2 text-xs text-ink-soft sm:px-5">
            {{ t('cvOptimizer.result.limitReached', { max: savedCvs.limit }) }}
          </p>
          <p v-if="saveError" class="border-b border-ink/10 px-4 py-2 text-xs text-rose-700 sm:px-5" role="alert">{{ saveError }}</p>
          <p v-if="store.optimized.skipped.length" class="border-b border-ink/10 px-4 py-2 text-xs text-amber-700 sm:px-5">
            {{ t('cvOptimizer.result.skipped', { count: store.optimized.skipped.length }) }}
          </p>
          <pre class="max-h-[32rem] overflow-y-auto whitespace-pre-wrap p-6 font-sans text-sm leading-relaxed text-ink sm:p-8">{{ store.optimized.text }}</pre>
          <p class="border-t border-ink/10 px-6 py-4 font-mono text-micro uppercase text-ink-soft sm:px-8">
            {{ t('cvOptimizer.result.reviewHint') }}
          </p>
        </div>
      </section>

      <p class="sr-only" aria-live="polite">{{ liveMessage }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { Check, Download, Loader2, Pencil, RefreshCw, Save, ShieldCheck, Sparkles, Undo2, X } from 'lucide-vue-next'
import posthog from 'posthog-js'
import AppPageHeader from '@/components/AppPageHeader.vue'
import AppStatus from '@/components/AppStatus.vue'
import LlmErrorNotice from '@/components/LlmErrorNotice.vue'
import OfferInput from '@/components/OfferInput.vue'
import PDFUpload from '@/components/PDFUpload.vue'
import SavedCvPicker from '@/components/SavedCvPicker.vue'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { useCvInputTab } from '@/composables/useCvInputTab'
import { useLocale } from '@/i18n/useLocale'
import { downloadOptimizedCv, type CvExportFormat, type SuggestionDecision, type SuggestionStatus } from '@/lib/cvOptimizer'
import { isOnline } from '@/lib/pwa'
import { useApplicationContextStore } from '@/stores/applicationContext'
import { useCvOptimizerStore } from '@/stores/cvOptimizer'
import { useSavedCvsStore } from '@/stores/savedCvs'

const { t } = useI18n()
const { push, replace, formatDate } = useLocale()
const route = useRoute()
const store = useCvOptimizerStore()
const context = useApplicationContextStore()
const savedCvs = useSavedCvsStore()
const cvTab = useCvInputTab()
const cvTabs = computed(() => [
  { value: 'upload' as const, label: t('common.file') },
  { value: 'manual' as const, label: t('common.text') },
])

// Analyse d'origine (/cv-optimizer?comparison=…) : optimisation ciblée sur ses exigences manquantes ou floues
const fromComparisonId = ref<string | null>(null)
const liveMessage = ref('')

const decisionOf = (id: string): SuggestionDecision => store.decisions[id] ?? { status: 'pending', text: '' }

const statusTone = (status: SuggestionStatus) =>
  status === 'accepted' ? 'text-emerald-700' : status === 'rejected' ? 'text-rose-700' : 'text-ink-soft'

function run() {
  editingId.value = null
  saved.value = false
  store.optimize(fromComparisonId.value)
}

// --- Édition d'une proposition -------------------------------------------------
const editingId = ref<string | null>(null)
const draft = ref('')

function startEdit(id: string) {
  editingId.value = id
  draft.value = decisionOf(id).text
}

function saveEdit(id: string) {
  store.accept(id, draft.value)
  editingId.value = null
}

// --- CV optimisé : export, enregistrement, réanalyse ----------------------------
const formats: CvExportFormat[] = ['txt', 'md']
const saving = ref(false)
const saved = ref(false)
const saveError = ref('')

function download(format: CvExportFormat) {
  downloadOptimizedCv(store.optimized.text, format, t('cvOptimizer.result.filename'))
  posthog.capture('cv_optimized_downloaded', { format, accepted_count: store.optimized.applied })
}

async function saveAsNewCv() {
  saving.value = true
  saveError.value = ''
  try {
    const label = t('cvOptimizer.result.savedLabel', { date: formatDate(new Date().toISOString(), { dateStyle: 'short' }) })
    await savedCvs.create({ label, text: store.optimized.text }, 'cvOptimizer')
    saved.value = true
    liveMessage.value = t('cvOptimizer.result.saved')
  } catch (err: any) {
    saveError.value = err?.response?.data?.detail || t('cvOptimizer.errors.save')
  } finally {
    saving.value = false
  }
}

// Le CV optimisé devient le CV courant, puis réanalyse de la même offre (#48)
function rescore() {
  store.useOptimizedCv()
  if (store.comparisonId) push({ path: '/compare', query: { history: store.comparisonId, rescore: '1' } })
  else push('/compare')
}

// Un nouveau choix invalide l'enregistrement précédent du CV optimisé
watch(
  () => store.optimized.text,
  () => (saved.value = false),
)

watch(
  () => store.loading,
  (loading, wasLoading) => {
    if (wasLoading && !loading) {
      liveMessage.value = store.error || t('cvOptimizer.statusReady', { count: store.suggestions.length })
    }
  },
)

// --- Relecture depuis l'historique (?history=…) ----------------------------------
const historyLoading = ref(false)
const historyError = ref('')
const pendingHistoryId = ref<string | null>(null)

async function loadHistory(historyId: string) {
  historyLoading.value = true
  historyError.value = ''
  try {
    await store.loadFromHistory(historyId)
    fromComparisonId.value = store.comparisonId
    pendingHistoryId.value = null
    replace({ path: '/cv-optimizer', query: {} })
  } catch {
    historyError.value = store.error || t('cvOptimizer.errors.loadHistory')
    store.error = null
    pendingHistoryId.value = historyId
  } finally {
    historyLoading.value = false
  }
}

onMounted(() => {
  context.trackReuse('cvOptimizer')
  savedCvs.fetch().catch(() => undefined)
  const historyId = typeof route.query.history === 'string' ? route.query.history : null
  const comparisonId = typeof route.query.comparison === 'string' ? route.query.comparison : null
  if (historyId) loadHistory(historyId)
  else if (comparisonId) {
    fromComparisonId.value = comparisonId
    if (store.comparisonId !== comparisonId) store.clearResult()
  }
})

watch(isOnline, (online) => {
  if (online && pendingHistoryId.value) loadHistory(pendingHistoryId.value)
})
</script>
