<template>
  <div class="page-shell">
    <AppPageHeader
      :label="t('dashboard.label')"
      :title="t('dashboard.title')"
      :description="t('dashboard.description')"
    />

    <div class="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-3">
      <article
        v-for="module in modules"
        :key="module.path"
        class="panel group relative flex cursor-pointer flex-col p-6 transition-colors focus-within:ring-2 focus-within:ring-ink/60 hover:border-ink/30 sm:p-8"
      >
        <div class="mb-6 font-mono text-micro uppercase text-ink-soft">{{ module.id }}</div>
        <h2 class="mb-3 font-medium text-title transition-colors group-hover:text-ink-soft">
          <!-- Lien étiré : toute la carte est cliquable, un seul arrêt clavier -->
          <RouterLink :to="localePath(module.path)" class="after:absolute after:inset-0 after:content-[''] focus:outline-none">
            {{ module.title }}
          </RouterLink>
        </h2>
        <p class="mb-6 max-w-[42ch] text-lead text-ink-soft">{{ module.description }}</p>
        <ul class="mb-8 space-y-2 font-mono text-micro uppercase text-ink-soft">
          <li v-for="feature in module.features" :key="feature" class="flex gap-2">
            <span class="text-ink/30" aria-hidden="true">—</span>
            <span>{{ feature }}</span>
          </li>
        </ul>
        <div class="mt-auto flex items-center justify-between border-t border-ink/10 pt-5 font-mono text-micro uppercase">
          <span class="text-ink transition-opacity group-hover:opacity-70">{{ module.cta }}</span>
          <ArrowRight class="h-4 w-4 text-ink-soft transition-transform group-hover:translate-x-1" aria-hidden="true" />
        </div>
      </article>
    </div>

    <section class="mt-12">
      <div class="mb-5 flex items-end justify-between gap-4">
        <div>
          <p class="font-mono text-micro uppercase text-ink-soft">{{ t('dashboard.history') }}</p>
          <h2 class="mt-1 font-medium text-title">{{ t('dashboard.comparisons.title') }}</h2>
        </div>
        <button
          v-if="history.length"
          type="button"
          class="btn-secondary h-9 px-4 text-micro"
          :disabled="historyLoading"
          @click="loadHistory"
        >
          {{ t('common.refresh') }}
        </button>
      </div>

      <AppStatus v-if="historyLoading" kind="loading" :message="t('dashboard.comparisons.loading')" />
      <AppStatus
        v-else-if="historyError"
        kind="error"
        :message="historyError"
        :action-label="t('common.retry')"
        @action="loadHistory"
      />
      <AppStatus
        v-else-if="!history.length"
        kind="empty"
        :message="t('dashboard.comparisons.empty')"
        :action-label="t('dashboard.comparisons.cta')"
        @action="push('/compare')"
      />

      <ul v-else class="space-y-3">
        <li
          v-for="item in history"
          :key="item.id"
          class="panel flex flex-col gap-4 p-5 sm:flex-row sm:items-center sm:justify-between"
        >
          <div class="min-w-0 flex-1">
            <div class="mb-2 flex flex-wrap items-center gap-3 font-mono text-micro uppercase text-ink-soft">
              <span>{{ formatDate(item.created_at) }}</span>
              <span>{{ t('dashboard.comparisons.match', { value: formatPercent(item.match_percentage) }) }}</span>
              <span>{{ t('dashboard.comparisons.criteria', { matches: item.matches, total: item.total_items }) }}</span>
            </div>
            <p class="truncate text-sm text-ink">{{ item.offer_excerpt || t('dashboard.noOfferExcerpt') }}</p>
            <p class="mt-1 truncate text-sm text-ink-soft">{{ item.cv_excerpt || t('dashboard.noCvExcerpt') }}</p>
          </div>
          <div class="flex shrink-0 gap-2">
            <button
              type="button"
              class="btn-secondary h-9 px-4 text-micro"
              :aria-label="t('dashboard.comparisons.view', { date: formatDate(item.created_at) })"
              @click="openHistory(item.id)"
            >
              {{ t('dashboard.view') }}
            </button>
            <button
              type="button"
              class="h-9 rounded-lg px-3 font-mono text-micro uppercase text-rose-700 transition-colors hover:bg-rose-500/10"
              :disabled="deletingId === item.id"
              :aria-label="t('dashboard.comparisons.delete', { date: formatDate(item.created_at) })"
              @click="removeHistory(item.id)"
            >
              {{ t('dashboard.delete') }}
            </button>
          </div>
        </li>
      </ul>
    </section>

    <section class="mt-12">
      <div class="mb-5 flex items-end justify-between gap-4">
        <div>
          <p class="font-mono text-micro uppercase text-ink-soft">{{ t('dashboard.history') }}</p>
          <h2 class="mt-1 font-medium text-title">{{ t('dashboard.interviews.title') }}</h2>
        </div>
        <button
          v-if="interviewHistory.length"
          type="button"
          class="btn-secondary h-9 px-4 text-micro"
          :disabled="interviewLoading"
          @click="loadInterviewHistory"
        >
          {{ t('common.refresh') }}
        </button>
      </div>

      <AppStatus v-if="interviewLoading" kind="loading" :message="t('dashboard.interviews.loading')" />
      <AppStatus
        v-else-if="interviewError"
        kind="error"
        :message="interviewError"
        :action-label="t('common.retry')"
        @action="loadInterviewHistory"
      />
      <AppStatus
        v-else-if="!interviewHistory.length"
        kind="empty"
        :message="t('dashboard.interviews.empty')"
        :action-label="t('dashboard.interviews.cta')"
        @action="push('/interview-simulator')"
      />

      <ul v-else class="space-y-3">
        <li
          v-for="item in interviewHistory"
          :key="item.id"
          class="panel flex flex-col gap-4 p-5 sm:flex-row sm:items-center sm:justify-between"
        >
          <div class="min-w-0 flex-1">
            <div class="mb-2 flex flex-wrap items-center gap-3 font-mono text-micro uppercase text-ink-soft">
              <span>{{ formatDate(item.created_at) }}</span>
              <span>{{ formatScore(item.score_global) }}/10</span>
              <span>{{ t('dashboard.interviews.questions', { count: item.num_questions }) }}</span>
              <span>{{ formatDuration(item.duration_seconds) }}</span>
            </div>
            <p class="truncate text-sm text-ink">{{ item.job_excerpt || t('dashboard.noOfferExcerpt') }}</p>
            <p class="mt-1 truncate text-sm text-ink-soft">{{ item.cv_excerpt || t('dashboard.noCvExcerpt') }}</p>
          </div>
          <div class="flex shrink-0 gap-2">
            <button
              type="button"
              class="btn-secondary h-9 px-4 text-micro"
              :aria-label="t('dashboard.interviews.view', { date: formatDate(item.created_at) })"
              @click="openInterviewHistory(item.id)"
            >
              {{ t('dashboard.view') }}
            </button>
            <button
              type="button"
              class="h-9 rounded-lg px-3 font-mono text-micro uppercase text-rose-700 transition-colors hover:bg-rose-500/10"
              :disabled="deletingInterviewId === item.id"
              :aria-label="t('dashboard.interviews.delete', { date: formatDate(item.created_at) })"
              @click="removeInterviewHistory(item.id)"
            >
              {{ t('dashboard.delete') }}
            </button>
          </div>
        </li>
      </ul>
    </section>

    <section class="mt-12">
      <div class="mb-5 flex items-end justify-between gap-4">
        <div>
          <p class="font-mono text-micro uppercase text-ink-soft">{{ t('dashboard.history') }}</p>
          <h2 class="mt-1 font-medium text-title">{{ t('dashboard.coverLetters.title') }}</h2>
        </div>
        <button
          v-if="letterHistory.length"
          type="button"
          class="btn-secondary h-9 px-4 text-micro"
          :disabled="letterLoading"
          @click="loadLetterHistory"
        >
          {{ t('common.refresh') }}
        </button>
      </div>

      <AppStatus v-if="letterLoading" kind="loading" :message="t('dashboard.coverLetters.loading')" />
      <AppStatus
        v-else-if="letterError"
        kind="error"
        :message="letterError"
        :action-label="t('common.retry')"
        @action="loadLetterHistory"
      />
      <AppStatus
        v-else-if="!letterHistory.length"
        kind="empty"
        :message="t('dashboard.coverLetters.empty')"
        :action-label="t('dashboard.coverLetters.cta')"
        @action="push('/cover-letter')"
      />

      <ul v-else class="space-y-3">
        <li
          v-for="item in letterHistory"
          :key="item.id"
          class="panel flex flex-col gap-4 p-5 sm:flex-row sm:items-center sm:justify-between"
        >
          <div class="min-w-0 flex-1">
            <div class="mb-2 flex flex-wrap items-center gap-3 font-mono text-micro uppercase text-ink-soft">
              <span>{{ formatDate(item.created_at) }}</span>
              <span>{{ t(`coverLetter.tones.${item.tone}`) }}</span>
              <span>{{ t('dashboard.coverLetters.words', { count: item.word_count }) }}</span>
            </div>
            <p class="truncate text-sm text-ink">{{ item.subject || item.job_excerpt || t('dashboard.noOfferExcerpt') }}</p>
            <p class="mt-1 truncate text-sm text-ink-soft">{{ item.job_excerpt || t('dashboard.noOfferExcerpt') }}</p>
          </div>
          <div class="flex shrink-0 gap-2">
            <button
              type="button"
              class="btn-secondary h-9 px-4 text-micro"
              :aria-label="t('dashboard.coverLetters.view', { date: formatDate(item.created_at) })"
              @click="openLetterHistory(item.id)"
            >
              {{ t('dashboard.view') }}
            </button>
            <button
              type="button"
              class="h-9 rounded-lg px-3 font-mono text-micro uppercase text-rose-700 transition-colors hover:bg-rose-500/10"
              :disabled="deletingLetterId === item.id"
              :aria-label="t('dashboard.coverLetters.delete', { date: formatDate(item.created_at) })"
              @click="removeLetterHistory(item.id)"
            >
              {{ t('dashboard.delete') }}
            </button>
          </div>
        </li>
      </ul>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ArrowRight } from 'lucide-vue-next'
import AppPageHeader from '@/components/AppPageHeader.vue'
import AppStatus from '@/components/AppStatus.vue'
import { useLocale } from '@/i18n/useLocale'
import { isOnline } from '@/lib/pwa'
import {
  deleteComparison,
  deleteCoverLetter,
  deleteInterview,
  listComparisons,
  listCoverLetters,
  listInterviews,
  type ComparisonHistoryItem,
  type CoverLetterHistoryItem,
  type InterviewHistoryItem,
} from '@/lib/api'

const { t, tm, rt } = useI18n()
const { localePath, push, formatDate, formatNumber, formatPercent } = useLocale()
const history = ref<ComparisonHistoryItem[]>([])
const historyLoading = ref(true)
const historyError = ref('')
const deletingId = ref<string | null>(null)

const interviewHistory = ref<InterviewHistoryItem[]>([])
const interviewLoading = ref(true)
const interviewError = ref('')
const deletingInterviewId = ref<string | null>(null)

const letterHistory = ref<CoverLetterHistoryItem[]>([])
const letterLoading = ref(true)
const letterError = ref('')
const deletingLetterId = ref<string | null>(null)

const MODULE_PATHS = {
  compare: '/compare',
  interview: '/interview-simulator',
  coverLetter: '/cover-letter',
} as const

const modules = computed(() =>
  (Object.keys(MODULE_PATHS) as (keyof typeof MODULE_PATHS)[]).map((key) => ({
    path: MODULE_PATHS[key],
    id: t(`dashboard.modules.${key}.id`),
    title: t(`dashboard.modules.${key}.title`),
    description: t(`dashboard.modules.${key}.description`),
    features: (tm(`dashboard.modules.${key}.features`) as unknown[]).map((feature) => rt(feature as string)),
    cta: t(`dashboard.modules.${key}.cta`),
  })),
)

async function loadHistory() {
  historyLoading.value = true
  historyError.value = ''
  try {
    const data = await listComparisons(10)
    history.value = data.items
  } catch (err: any) {
    historyError.value = err.response?.data?.detail || t('dashboard.comparisons.loadError')
  } finally {
    historyLoading.value = false
  }
}

async function loadInterviewHistory() {
  interviewLoading.value = true
  interviewError.value = ''
  try {
    const data = await listInterviews(10)
    interviewHistory.value = data.items
  } catch (err: any) {
    interviewError.value = err.response?.data?.detail || t('dashboard.interviews.loadError')
  } finally {
    interviewLoading.value = false
  }
}

async function loadLetterHistory() {
  letterLoading.value = true
  letterError.value = ''
  try {
    const data = await listCoverLetters(10)
    letterHistory.value = data.items
  } catch (err: any) {
    letterError.value = err.response?.data?.detail || t('dashboard.coverLetters.loadError')
  } finally {
    letterLoading.value = false
  }
}

function formatScore(score: number) {
  return formatNumber(score, { maximumFractionDigits: 1 })
}

function formatDuration(seconds: number) {
  const m = Math.floor((seconds || 0) / 60)
  const s = (seconds || 0) % 60
  return `${m}:${s.toString().padStart(2, '0')}`
}

function openHistory(id: string) {
  push({ path: '/compare', query: { history: id } })
}

function openInterviewHistory(id: string) {
  push({ path: '/interview-results', query: { history: id } })
}

function openLetterHistory(id: string) {
  push({ path: '/cover-letter', query: { history: id } })
}

async function removeHistory(id: string) {
  deletingId.value = id
  try {
    await deleteComparison(id)
    history.value = history.value.filter((item) => item.id !== id)
  } catch (err: any) {
    historyError.value = err.response?.data?.detail || t('dashboard.deleteError')
  } finally {
    deletingId.value = null
  }
}

async function removeInterviewHistory(id: string) {
  deletingInterviewId.value = id
  try {
    await deleteInterview(id)
    interviewHistory.value = interviewHistory.value.filter((item) => item.id !== id)
  } catch (err: any) {
    interviewError.value = err.response?.data?.detail || t('dashboard.deleteError')
  } finally {
    deletingInterviewId.value = null
  }
}

async function removeLetterHistory(id: string) {
  deletingLetterId.value = id
  try {
    await deleteCoverLetter(id)
    letterHistory.value = letterHistory.value.filter((item) => item.id !== id)
  } catch (err: any) {
    letterError.value = err.response?.data?.detail || t('dashboard.deleteError')
  } finally {
    deletingLetterId.value = null
  }
}

onMounted(() => {
  loadHistory()
  loadInterviewHistory()
  loadLetterHistory()
})

// Retour du réseau : relancer les listes en erreur
watch(isOnline, (online) => {
  if (!online) return
  if (historyError.value) loadHistory()
  if (interviewError.value) loadInterviewHistory()
  if (letterError.value) loadLetterHistory()
})
</script>
