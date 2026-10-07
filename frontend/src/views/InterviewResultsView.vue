<template>
  <div class="page-shell">
    <AppPageHeader
      :label="t('results.label')"
      :title="t('results.title')"
      :description="t('results.description')"
    />

    <ApplicationContextBanner
      v-if="historyContext"
      :proposal="historyContext"
      @adopt="adoptHistoryContext"
      @dismiss="historyContext = null"
    />

    <AppStatus v-if="isLoading" kind="loading" centered :message="t('results.loading')" />

    <div v-else-if="error" class="space-y-4">
      <AppStatus
        kind="error"
        centered
        :message="error"
        :action-label="canRetry ? t('common.retry') : undefined"
        @action="loadInterviewData"
      />
      <div class="flex justify-center">
        <Button variant="outline" @click="startNewInterview">
          <MessageSquare class="mr-2 h-4 w-4" aria-hidden="true" />
          {{ t('results.newSimulator') }}
        </Button>
      </div>
    </div>

    <div v-else-if="interviewData" class="space-y-8">
      <div class="grid grid-cols-1 gap-4 md:grid-cols-4">
        <div class="panel p-6 text-center md:col-span-2">
          <div class="mb-1 font-mono text-micro uppercase text-ink-soft">{{ t('results.globalScore') }}</div>
          <div class="text-4xl font-medium tabular-nums">{{ analysisResult?.score_global || t('common.notAvailable') }}/10</div>
          <p class="mt-1 font-mono text-micro uppercase text-emerald-600">{{ getScoreMessage(analysisResult?.score_global) }}</p>
        </div>
        <div class="panel p-6 text-center">
          <div class="mb-1 font-mono text-micro uppercase text-ink-soft">{{ t('results.questions') }}</div>
          <div class="text-3xl font-medium tabular-nums">{{ interviewData.num_questions }}</div>
        </div>
        <div class="panel p-6 text-center">
          <div class="mb-1 font-mono text-micro uppercase text-ink-soft">{{ t('results.duration') }}</div>
          <div class="text-3xl font-medium tabular-nums">{{ formatTime(interviewData.duration) }}</div>
        </div>
      </div>

      <div v-if="analysisResult?.points_forts?.length" class="panel p-6 space-y-4">
        <h3 class="flex items-center gap-2 font-mono text-caption uppercase">
          <CheckCircle class="h-4 w-4 text-emerald-500" aria-hidden="true" />
          {{ t('results.strengths') }}
        </h3>
        <div class="space-y-2">
          <div v-for="(pf, idx) in analysisResult.points_forts" :key="idx" class="rounded-lg border border-emerald-500/20 bg-emerald-500/5 p-3 text-sm text-emerald-800">
            {{ pf }}
          </div>
        </div>
      </div>

      <div v-if="analysisResult?.points_amelioration?.length" class="panel p-6 space-y-4">
        <h3 class="flex items-center gap-2 font-mono text-caption uppercase">
          <MessageSquare class="h-4 w-4 text-amber-600" aria-hidden="true" />
          {{ t('results.improvements') }}
        </h3>
        <div class="space-y-2">
          <div v-for="(pa, idx) in analysisResult.points_amelioration" :key="idx" class="rounded-lg border border-amber-500/20 bg-amber-500/5 p-3 text-sm text-amber-800">
            {{ pa }}
          </div>
        </div>
      </div>

      <div class="panel-dark">
        <div class="panel-dark-inner">
          <div class="panel-dark-header">{{ t('results.answersDetail') }}</div>
          <div class="space-y-0 p-4 sm:p-6">
            <div v-for="(ans, idx) in interviewData.answers" :key="idx" class="border-b border-white/5 py-4 last:border-0">
              <div class="mb-2 font-mono text-micro uppercase text-paper/60">
                {{ t('results.questionN', { n: idx + 1, category: ans.category }) }}
              </div>
              <p class="mb-3 text-sm font-medium text-paper/90">{{ ans.question }}</p>
              <div class="rounded-lg border border-white/10 p-3 text-xs text-paper/60">
                {{ ans.answer || t('results.noAnswer') }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="flex flex-col items-center justify-center gap-3 sm:flex-row">
        <ExportPdfButton
          v-if="reportMeta"
          type="interview"
          :file-title="reportFileTitle(t('report.interview.title'), reportMeta.date)"
        />
        <Button variant="outline" @click="goToDashboard">
          <ArrowLeft class="mr-2 h-4 w-4" aria-hidden="true" />
          {{ t('results.backToDashboard') }}
        </Button>
        <Button @click="startNewInterview">
          <RotateCcw class="mr-2 h-4 w-4" aria-hidden="true" />
          {{ t('results.newSimulation') }}
        </Button>
      </div>

      <InterviewReport
        v-if="reportMeta"
        :analysis="analysisResult"
        :answers="interviewData.answers"
        :num-questions="interviewData.num_questions"
        :duration="formatTime(interviewData.duration)"
        :score-message="getScoreMessage(analysisResult?.score_global)"
        :meta="reportMeta"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import AppPageHeader from '@/components/AppPageHeader.vue'
import AppStatus from '@/components/AppStatus.vue'
import ApplicationContextBanner from '@/components/ApplicationContextBanner.vue'
import ExportPdfButton from '@/components/report/ExportPdfButton.vue'
import InterviewReport from '@/components/report/InterviewReport.vue'
import { Button } from '@/components/ui/button'
import { useLocale } from '@/i18n/useLocale'
import { getInterview } from '@/lib/api'
import { isOnline } from '@/lib/pwa'
import { reportFileTitle, type ReportMeta } from '@/lib/report'
import { useApplicationContextStore } from '@/stores/applicationContext'
import type { HistoryContext } from '@/stores/compare'
import { ArrowLeft, RotateCcw, CheckCircle, MessageSquare } from 'lucide-vue-next'

const { t } = useI18n()
const { push } = useLocale()
const route = useRoute()
const context = useApplicationContextStore()
// CV + offre de l'entretien rouvert depuis l'historique, proposés comme contexte courant
const historyContext = ref<HistoryContext | null>(null)

function proposeHistoryContext(cvText: string, offerText: string, offerUrl: string | null) {
  if (!cvText.trim() && !offerText.trim()) return
  // Contexte vide ou identique : repris directement, sinon proposé à l'utilisateur
  if (!context.hasContext) context.setContext({ cvText, offerText, offerUrl }, 'interview')
  historyContext.value = context.matches(cvText, offerText) ? null : { cvText, offerText, offerUrl }
}

function adoptHistoryContext() {
  if (!historyContext.value) return
  context.setContext(historyContext.value, 'interview')
  historyContext.value = null
}

const isLoading = ref(true)
const error = ref('')
const interviewData = ref<any>(null)
const analysisResult = ref<any>(null)
// Offre et date de la session, pour l'export PDF
const reportMeta = ref<ReportMeta | null>(null)

const formatTime = (seconds: number) => {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${m}:${s.toString().padStart(2, '0')}`
}

const getScoreMessage = (score: number | undefined) => {
  if (!score) return t('results.score.none')
  if (score >= 8) return t('results.score.excellent')
  if (score >= 6) return t('results.score.good')
  return t('results.score.work')
}

function applySession(payload: {
  questions: any[]
  answers: any[]
  analysis: any
  duration: number
  offerText: string
  offerUrl: string | null
  date: string
}) {
  interviewData.value = {
    id: 'session',
    num_questions: payload.questions?.length || payload.answers?.length || 0,
    duration: payload.duration || 0,
    answers: (payload.answers || []).map((answer: any) => ({
      question: answer.question,
      answer: answer.answer,
      category: answer.category,
      time: answer.time || 0,
    })),
  }
  analysisResult.value = payload.analysis
  reportMeta.value = { offerText: payload.offerText, offerUrl: payload.offerUrl, date: payload.date }
}

const loadInterviewData = async () => {
  isLoading.value = true
  error.value = ''

  try {
    const historyId = typeof route.query.history === 'string' ? route.query.history : null
    if (historyId) {
      const detail = await getInterview(historyId)
      applySession({
        questions: detail.questions as any[],
        answers: detail.answers as any[],
        analysis: detail.analysis,
        duration: detail.duration_seconds,
        offerText: detail.job_text || '',
        offerUrl: detail.offer_url || null,
        date: detail.created_at || new Date().toISOString(),
      })
      proposeHistoryContext(detail.cv_text || '', detail.job_text || '', detail.offer_url || null)
      localStorage.removeItem('interviewAnalysis')
      return
    }

    const storedAnalysis = localStorage.getItem('interviewAnalysis')
    if (storedAnalysis) {
      const analysisData = JSON.parse(storedAnalysis)
      applySession({
        questions: analysisData.questions,
        answers: analysisData.answers,
        analysis: analysisData.analysis,
        duration: analysisData.duration,
        offerText: analysisData.job_text || '',
        offerUrl: analysisData.offer_url || null,
        date: analysisData.created_at || new Date().toISOString(),
      })
      localStorage.removeItem('interviewAnalysis')
      return
    }

    error.value = t('results.noSession')
  } catch (err: any) {
    error.value = err.response?.data?.detail || err.message || t('results.loadError')
  } finally {
    isLoading.value = false
  }
}

const goToDashboard = () => push('/dashboard')
const startNewInterview = () => push('/interview-simulator')

// Deep link /interview-results?history=… : relance possible (bouton, retour du réseau)
const canRetry = computed(() => typeof route.query.history === 'string')

onMounted(() => {
  loadInterviewData()
})

watch(isOnline, (online) => {
  if (online && error.value && canRetry.value) loadInterviewData()
})
</script>
