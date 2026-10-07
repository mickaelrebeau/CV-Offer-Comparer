<template>
  <div class="page-shell">
    <AppPageHeader
      :label="t('interview.label')"
      :title="t('interview.title')"
      :description="t('interview.description')"
    />

    <ApplicationContextBanner edit-target="job-text" @edit="editContext" />

    <!-- Annonce le changement d'étape et de question aux lecteurs d'écran -->
    <p class="sr-only" aria-live="polite">{{ stepAnnouncement }}</p>

    <!-- Étape 1 : saisie -->
    <div v-if="currentStep === 1" class="space-y-8">
      <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <OfferInput
          module="interview"
          textarea-id="job-text"
          :placeholder="t('interview.jobPlaceholder')"
          min-height-class="min-h-[200px]"
        />

        <div class="panel overflow-hidden">
          <div class="panel-header justify-between">
            <span id="cv-label">{{ t('cvInput.cvHeader') }}</span>
            <div class="flex gap-1" role="group" :aria-label="t('cvInput.cvFormat')">
              <button
                type="button"
                :aria-pressed="cvActiveTab === 'upload'"
                @click="cvActiveTab = 'upload'"
                class="rounded px-2 py-0.5 transition-colors"
                :class="cvActiveTab === 'upload' ? 'bg-ink text-paper' : 'text-ink-soft hover:text-ink'"
              >
                {{ t('common.file') }}
              </button>
              <button
                type="button"
                :aria-pressed="cvActiveTab === 'manual'"
                @click="cvActiveTab = 'manual'"
                class="rounded px-2 py-0.5 transition-colors"
                :class="cvActiveTab === 'manual' ? 'bg-ink text-paper' : 'text-ink-soft hover:text-ink'"
              >
                {{ t('common.text') }}
              </button>
            </div>
          </div>
          <div class="p-4 sm:p-5">
            <SavedCvPicker module="interview" class="mb-4" />
            <PDFUpload
              v-if="cvActiveTab === 'upload'"
              :model-value="context.cvText"
              :file-name="context.cvFileName"
              @update:model-value="handleCVTextUpdate"
              @update:file-name="(name) => (context.cvFileName = name)"
            />
            <Textarea v-else aria-labelledby="cv-label" :model-value="context.cvText" :placeholder="t('interview.cvPlaceholder')" class="min-h-[200px]" @input="handleCVInput" />
          </div>
        </div>
      </div>

      <LlmErrorNotice v-if="error" :message="error" :code="errorCode" />

      <div class="flex justify-center">
        <Button :disabled="!context.isComplete || isLoading" size="lg" @click="generateQuestions">
          <Loader2 v-if="isLoading" class="mr-2 h-4 w-4 animate-spin" aria-hidden="true" />
          <MessageSquare v-else class="mr-2 h-4 w-4" aria-hidden="true" />
          {{ t('interview.generate') }}
        </Button>
      </div>
    </div>

    <!-- Étape 2 : entretien -->
    <div v-if="currentStep === 2" class="space-y-8">
      <div class="panel flex flex-col gap-4 p-5 sm:flex-row sm:items-center sm:justify-between">
        <div class="flex flex-wrap items-center gap-3">
          <Button variant="outline" size="sm" @click="resetSimulator">
            <ArrowLeft class="mr-1.5 h-4 w-4" aria-hidden="true" />
            {{ t('interview.changeTopic') }}
          </Button>
          <Button v-if="!isInterviewStarted" size="sm" @click="startInterview">
            <Play class="mr-1.5 h-4 w-4" aria-hidden="true" />
            {{ t('interview.start') }}
          </Button>
        </div>
        <div class="font-mono text-micro uppercase text-ink-soft">
          {{ t('interview.estimate', { minutes: estimatedTime, count: questions.length }) }}
        </div>
      </div>

      <div v-if="isInterviewStarted" class="space-y-6">
        <div class="panel-dark">
          <div class="panel-dark-inner">
            <div class="panel-dark-header justify-between">
              <span>{{ t('interview.questionOf', { current: currentQuestionIndex + 1, total: questions.length, category: currentQuestionCategory }) }}</span>
              <span role="timer">
                <span aria-hidden="true">⏱</span>
                <span class="sr-only">{{ t('interview.elapsed') }}</span>
                {{ formatTime(interviewTimer) }}
              </span>
            </div>
            <div class="space-y-5 p-5 sm:p-6">
              <p class="font-sans text-lg font-medium leading-snug text-paper">{{ currentQuestion }}</p>
              <div class="space-y-2">
                <label for="answer" class="field-label !text-paper/60">{{ t('interview.answerLabel') }}</label>
                <Textarea
                  id="answer"
                  v-model="currentAnswer"
                  :placeholder="t('interview.answerPlaceholder')"
                  class="min-h-[160px] !border-white/10 !bg-ink-deep !text-paper placeholder:!text-paper/60"
                />
              </div>
              <div class="flex items-center justify-between pt-2">
                <Button variant="outline" size="sm" :disabled="currentQuestionIndex === 0" @click="previousQuestion">
                  <ChevronLeft class="mr-1 h-4 w-4" aria-hidden="true" />
                  {{ t('interview.previous') }}
                </Button>
                <div class="flex gap-2">
                  <Button v-if="!isPaused" variant="outline" size="sm" @click="pauseInterview">
                    <Pause class="mr-1 h-4 w-4" aria-hidden="true" />
                    {{ t('interview.pause') }}
                  </Button>
                  <Button v-else variant="outline" size="sm" @click="resumeInterview">
                    <Play class="mr-1 h-4 w-4" aria-hidden="true" />
                    {{ t('interview.resume') }}
                  </Button>
                </div>
                <Button size="sm" :disabled="currentQuestionIndex === questions.length - 1" @click="nextQuestion">
                  {{ t('interview.next') }}
                  <ChevronRight class="ml-1 h-4 w-4" aria-hidden="true" />
                </Button>
              </div>
            </div>
          </div>
        </div>

        <div class="space-y-2">
          <div class="flex justify-between font-mono text-micro uppercase text-ink-soft">
            <span>{{ t('interview.progress') }}</span>
            <span>{{ formatPercent((currentQuestionIndex + 1) / questions.length) }}</span>
          </div>
          <div
            class="progress-track"
            role="progressbar"
            :aria-label="t('interview.progressAria')"
            :aria-valuenow="currentQuestionIndex + 1"
            aria-valuemin="1"
            :aria-valuemax="questions.length"
            :aria-valuetext="t('interview.progressValue', { current: currentQuestionIndex + 1, total: questions.length })"
          >
            <div class="progress-fill" :style="{ width: `${((currentQuestionIndex + 1) / questions.length) * 100}%` }"></div>
          </div>
        </div>

        <div v-if="currentQuestionIndex === questions.length - 1" class="panel p-8 text-center">
          <CheckCircle class="mx-auto mb-4 h-10 w-10 text-emerald-500" aria-hidden="true" />
          <h3 class="mb-2 font-medium text-title">{{ t('interview.completeTitle') }}</h3>
          <p class="mb-6 text-lead text-ink-soft">{{ t('interview.completeText') }}</p>
          <LlmErrorNotice v-if="error" class="mb-4 text-left" :message="error" :code="errorCode" />
          <Button size="lg" :disabled="isLoading" @click="finishInterview">
            <Loader2 v-if="isLoading" class="mr-2 h-4 w-4 animate-spin" aria-hidden="true" />
            {{ isLoading ? t('interview.analyzing') : t('interview.getReport') }}
          </Button>
        </div>
      </div>

      <div v-else class="space-y-3">
        <div v-for="(q, idx) in questions" :key="idx" class="panel p-5">
          <div class="mb-2 flex items-center gap-2 font-mono text-micro uppercase">
            <span class="text-ink-soft">{{ t('interview.questionN', { n: idx + 1 }) }}</span>
            <span class="text-ink-soft">· {{ q.category }}</span>
          </div>
          <p class="text-sm font-medium text-ink">{{ q.text }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { onBeforeRouteLeave } from 'vue-router'
import AppPageHeader from '@/components/AppPageHeader.vue'
import ApplicationContextBanner from '@/components/ApplicationContextBanner.vue'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import {
  CheckCircle, Loader2, Play, Pause, ChevronLeft, ChevronRight, MessageSquare, ArrowLeft,
} from 'lucide-vue-next'
import { generateInterviewQuestions, analyzeInterviewResponses } from '@/lib/api'
import OfferInput from '@/components/OfferInput.vue'
import PDFUpload from '@/components/PDFUpload.vue'
import SavedCvPicker from '@/components/SavedCvPicker.vue'
import LlmErrorNotice from '@/components/LlmErrorNotice.vue'
import { useCvInputTab } from '@/composables/useCvInputTab'
import { useLocale } from '@/i18n/useLocale'
import { useApplicationContextStore } from '@/stores/applicationContext'
import posthog from 'posthog-js'

const { t } = useI18n()
const { push, formatPercent } = useLocale()

const context = useApplicationContextStore()
const currentStep = ref(1)
// CV et offre figés à la génération des questions : l'analyse finale reste cohérente
// même si le contexte partagé est modifié ou effacé pendant l'entretien
const sessionCvText = ref('')
const sessionJobText = ref('')
const sessionOfferUrl = ref<string | null>(null)
const cvActiveTab = useCvInputTab()
const isLoading = ref(false)
const error = ref('')
const errorCode = ref<string | null>(null)
const questions = ref<any[]>([])
const isInterviewStarted = ref(false)
const currentQuestionIndex = ref(0)
const currentAnswer = ref('')
const interviewTimer = ref(0)
const isPaused = ref(false)
const interviewSession = ref<any>(null)
const answers = ref<any[]>([])
let timerInterval: ReturnType<typeof setInterval> | null = null

const currentQuestion = computed(() => questions.value[currentQuestionIndex.value]?.text || '')

const stepAnnouncement = computed(() => {
  if (currentStep.value === 1) return ''
  if (!isInterviewStarted.value) return t('interview.announce.generated', { count: questions.value.length })
  return t('interview.announce.question', {
    current: currentQuestionIndex.value + 1,
    total: questions.value.length,
    text: currentQuestion.value,
  })
})
const currentQuestionCategory = computed(() => questions.value[currentQuestionIndex.value]?.category || '')
const estimatedTime = computed(() => Math.round(questions.value.length * 2))

const handleCVInput = (event: Event) => {
  context.setCv((event.target as HTMLTextAreaElement).value, { from: 'interview' })
  error.value = ''
}

// Offre modifiée (texte ou import) : l'erreur précédente n'est plus d'actualité
watch(() => context.offerText, () => (error.value = ''))

const handleCVTextUpdate = (text: string) => {
  context.setCv(text, { from: 'interview' })
  error.value = ''
}

const generateQuestions = async () => {
  const cvText = context.cvText
  const jobText = context.offerText
  if (!cvText.trim() || !jobText.trim()) {
    error.value = t('interview.errors.missingInput')
    return
  }

  isLoading.value = true
  error.value = ''
  errorCode.value = null

  try {
    const cvBlob = new Blob([cvText], { type: 'text/plain' })
    const cvFile = new File([cvBlob], 'cv.txt', { type: 'text/plain' })
    const result = await generateInterviewQuestions(cvFile, jobText, 5)

    if (result.success && result.interview_session) {
      sessionCvText.value = cvText
      sessionJobText.value = jobText
      sessionOfferUrl.value = context.offerUrl
      questions.value = result.interview_session.questions
      interviewSession.value = result.interview_session
      currentStep.value = 2
      posthog.capture('interview_questions_generated', {
        question_count: result.interview_session.questions.length,
      })
    } else {
      errorCode.value = result.code || null
      throw new Error(result.message)
    }
  } catch (err: any) {
    error.value = err.message || t('interview.errors.generate')
  } finally {
    isLoading.value = false
  }
}

const startInterview = () => {
  isInterviewStarted.value = true
  posthog.capture('interview_started', { question_count: questions.value.length })
  startTimer()
}

const nextQuestion = () => {
  saveCurrentAnswer()
  if (currentQuestionIndex.value < questions.value.length - 1) {
    currentQuestionIndex.value++
    currentAnswer.value = ''
  }
}

const previousQuestion = () => {
  saveCurrentAnswer()
  if (currentQuestionIndex.value > 0) {
    currentQuestionIndex.value--
    currentAnswer.value = ''
  }
}

const saveCurrentAnswer = () => {
  if (currentAnswer.value.trim()) {
    const answerData = {
      questionIndex: currentQuestionIndex.value,
      question: questions.value[currentQuestionIndex.value]?.text || '',
      category: questions.value[currentQuestionIndex.value]?.category || '',
      answer: currentAnswer.value,
      time: 0,
    }
    const existingIndex = answers.value.findIndex((a) => a.questionIndex === currentQuestionIndex.value)
    if (existingIndex >= 0) answers.value[existingIndex] = answerData
    else answers.value.push(answerData)
  }
}

// Simulation en cours : réponses uniquement en mémoire → confirmer avant de quitter
// (liens, retour navigateur, geste retour mobile, fermeture de l'onglet)
const leavingToResults = ref(false)
const hasUnsavedSession = computed(
  () => currentStep.value === 2 && isInterviewStarted.value && !leavingToResults.value,
)

onBeforeRouteLeave(() => {
  if (!hasUnsavedSession.value) return true
  return window.confirm(t('interview.leaveConfirm'))
})

const warnBeforeUnload = (event: BeforeUnloadEvent) => {
  if (!hasUnsavedSession.value) return
  event.preventDefault()
  event.returnValue = ''
}

onMounted(() => window.addEventListener('beforeunload', warnBeforeUnload))

const finishInterview = async () => {
  saveCurrentAnswer()

  if (questions.value.length > 0 && answers.value.length > 0) {
    try {
      isLoading.value = true
      error.value = ''
      errorCode.value = null
      const result = await analyzeInterviewResponses(
        questions.value,
        answers.value,
        sessionCvText.value,
        sessionJobText.value,
        interviewTimer.value,
        sessionOfferUrl.value,
      )

      if (result.success && result.analysis) {
        // Fallback local si l’historique serveur n’est pas encore disponible
        localStorage.setItem('interviewAnalysis', JSON.stringify({
          questions: questions.value,
          answers: answers.value,
          analysis: result.analysis,
          duration: interviewTimer.value,
          cv_text: sessionCvText.value,
          job_text: sessionJobText.value,
          offer_url: sessionOfferUrl.value,
          created_at: new Date().toISOString(),
        }))
        posthog.capture('interview_completed', {
          answered_question_count: answers.value.length,
          duration_seconds: interviewTimer.value,
        })
        leavingToResults.value = true
        if (result.interview_id) {
          push({ path: '/interview-results', query: { history: result.interview_id } })
        } else {
          push('/interview-results')
        }
      } else {
        errorCode.value = result.code || null
        throw new Error(result.message || t('interview.errors.analyze'))
      }
    } catch (err: any) {
      error.value = err.message || t('interview.errors.analyze')
    } finally {
      isLoading.value = false
    }
  } else {
    leavingToResults.value = true
    push('/interview-results')
  }
}

const startTimer = () => {
  timerInterval = setInterval(() => {
    if (!isPaused.value) interviewTimer.value++
  }, 1000)
}

const pauseInterview = () => { isPaused.value = true }
const resumeInterview = () => { isPaused.value = false }

const formatTime = (seconds: number) => {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${m}:${s.toString().padStart(2, '0')}`
}

// Le contexte partagé (CV + offre) est conservé : seul l'entretien en cours est abandonné
const resetSimulator = () => {
  if (timerInterval) clearInterval(timerInterval)
  timerInterval = null
  currentStep.value = 1
  sessionCvText.value = ''
  sessionJobText.value = ''
  sessionOfferUrl.value = null
  questions.value = []
  isInterviewStarted.value = false
  currentQuestionIndex.value = 0
  currentAnswer.value = ''
  interviewTimer.value = 0
  answers.value = []
  error.value = ''
}

// « Modifier » depuis l'encart de contexte : retour à la saisie (confirmation si l'entretien a commencé)
const editContext = () => {
  if (currentStep.value === 1) return
  if (hasUnsavedSession.value && !window.confirm(t('interview.leaveConfirm'))) return
  resetSimulator()
}

onMounted(() => context.trackReuse('interview'))

onUnmounted(() => {
  if (timerInterval) clearInterval(timerInterval)
  window.removeEventListener('beforeunload', warnBeforeUnload)
})
</script>
