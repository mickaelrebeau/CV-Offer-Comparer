<template>
  <div class="page-shell">
    <AppPageHeader
      label="Simulateur"
      title="Studio d'entraînement"
      description="Préparez-vous aux questions ciblées générées d'après les zones d'attention de votre candidature."
    />

    <!-- Étape 1 : saisie -->
    <div v-if="currentStep === 1" class="space-y-8">
      <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div class="panel overflow-hidden">
          <div class="panel-header">01 · Offre d'emploi</div>
          <div class="p-4 sm:p-5">
            <Textarea :model-value="jobText" placeholder="Collez l'offre d'emploi..." class="min-h-[200px]" @input="handleJobInput" />
          </div>
        </div>

        <div class="panel overflow-hidden">
          <div class="panel-header justify-between">
            <span>02 · Mon CV</span>
            <div class="flex gap-1">
              <button
                @click="cvActiveTab = 'upload'"
                class="rounded px-2 py-0.5 transition-colors"
                :class="cvActiveTab === 'upload' ? 'bg-ink text-paper' : 'text-ink-soft hover:text-ink'"
              >
                PDF
              </button>
              <button
                @click="cvActiveTab = 'manual'"
                class="rounded px-2 py-0.5 transition-colors"
                :class="cvActiveTab === 'manual' ? 'bg-ink text-paper' : 'text-ink-soft hover:text-ink'"
              >
                Texte
              </button>
            </div>
          </div>
          <div class="p-4 sm:p-5">
            <PDFUpload v-if="cvActiveTab === 'upload'" :model-value="cvText" @update:model-value="handleCVTextUpdate" />
            <Textarea v-else :model-value="cvText" placeholder="Collez le texte de votre CV..." class="min-h-[200px]" @input="handleCVInput" />
          </div>
        </div>
      </div>

      <div v-if="error" class="rounded-lg border border-rose-500/25 bg-rose-500/5 p-4 font-mono text-micro text-rose-700">
        {{ error }}
      </div>

      <div class="flex justify-center">
        <Button :disabled="!cvText || !jobText || isLoading" size="lg" @click="generateQuestions">
          <Loader2 v-if="isLoading" class="mr-2 h-4 w-4 animate-spin" />
          <MessageSquare v-else class="mr-2 h-4 w-4" />
          Générer les questions
        </Button>
      </div>
    </div>

    <!-- Étape 2 : entretien -->
    <div v-if="currentStep === 2" class="space-y-8">
      <div class="panel flex flex-col gap-4 p-5 sm:flex-row sm:items-center sm:justify-between">
        <div class="flex flex-wrap items-center gap-3">
          <Button variant="outline" size="sm" @click="resetSimulator">
            <ArrowLeft class="mr-1.5 h-4 w-4" />
            Changer de sujet
          </Button>
          <Button v-if="!isInterviewStarted" size="sm" @click="startInterview">
            <Play class="mr-1.5 h-4 w-4" />
            Lancer la simulation
          </Button>
        </div>
        <div class="font-mono text-micro uppercase text-ink-soft">
          ~{{ estimatedTime }} min · {{ questions.length }} questions
        </div>
      </div>

      <div v-if="isInterviewStarted" class="space-y-6">
        <div class="panel-dark">
          <div class="panel-dark-inner">
            <div class="panel-dark-header justify-between">
              <span>Question {{ currentQuestionIndex + 1 }} / {{ questions.length }} · {{ currentQuestionCategory }}</span>
              <span>⏱ {{ formatTime(interviewTimer) }}</span>
            </div>
            <div class="space-y-5 p-5 sm:p-6">
              <p class="font-sans text-lg font-medium leading-snug text-paper">{{ currentQuestion }}</p>
              <div class="space-y-2">
                <label for="answer" class="field-label !text-paper/40">Votre réponse</label>
                <Textarea
                  id="answer"
                  v-model="currentAnswer"
                  placeholder="Rédigez les éléments clés de votre réponse..."
                  class="min-h-[160px] !border-white/10 !bg-ink-deep !text-paper placeholder:!text-paper/30"
                />
              </div>
              <div class="flex items-center justify-between pt-2">
                <Button variant="outline" size="sm" :disabled="currentQuestionIndex === 0" @click="previousQuestion">
                  <ChevronLeft class="mr-1 h-4 w-4" />
                  Précédente
                </Button>
                <div class="flex gap-2">
                  <Button v-if="!isPaused" variant="outline" size="sm" @click="pauseInterview">
                    <Pause class="mr-1 h-4 w-4" />
                    Pause
                  </Button>
                  <Button v-else variant="outline" size="sm" @click="resumeInterview">
                    <Play class="mr-1 h-4 w-4" />
                    Reprendre
                  </Button>
                </div>
                <Button size="sm" :disabled="currentQuestionIndex === questions.length - 1" @click="nextQuestion">
                  Suivante
                  <ChevronRight class="ml-1 h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
        </div>

        <div class="space-y-2">
          <div class="flex justify-between font-mono text-micro uppercase text-ink-soft">
            <span>Progression</span>
            <span>{{ Math.round(((currentQuestionIndex + 1) / questions.length) * 100) }}%</span>
          </div>
          <div class="progress-track">
            <div class="progress-fill" :style="{ width: `${((currentQuestionIndex + 1) / questions.length) * 100}%` }"></div>
          </div>
        </div>

        <div v-if="currentQuestionIndex === questions.length - 1" class="panel p-8 text-center">
          <CheckCircle class="mx-auto mb-4 h-10 w-10 text-emerald-500" />
          <h3 class="mb-2 font-medium text-title">Toutes les questions sont complétées</h3>
          <p class="mb-6 text-lead text-ink-soft">Obtenez une évaluation détaillée de vos réponses.</p>
          <div v-if="error" class="mb-4 rounded-lg border border-rose-500/25 bg-rose-500/5 p-3 font-mono text-micro text-rose-700">
            {{ error }}
          </div>
          <Button size="lg" :disabled="isLoading" @click="finishInterview">
            <Loader2 v-if="isLoading" class="mr-2 h-4 w-4 animate-spin" />
            {{ isLoading ? 'Analyse en cours...' : 'Obtenir le rapport' }}
          </Button>
        </div>
      </div>

      <div v-else class="space-y-3">
        <div v-for="(q, idx) in questions" :key="idx" class="panel p-5">
          <div class="mb-2 flex items-center gap-2 font-mono text-micro uppercase">
            <span class="text-ink-soft">Question {{ idx + 1 }}</span>
            <span class="text-ink/30">{{ q.category }}</span>
          </div>
          <p class="text-sm font-medium text-ink">{{ q.text }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import AppPageHeader from '@/components/AppPageHeader.vue'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import {
  CheckCircle, Loader2, Play, Pause, ChevronLeft, ChevronRight, MessageSquare, ArrowLeft,
} from 'lucide-vue-next'
import { generateInterviewQuestions, analyzeInterviewResponses } from '@/lib/api'
import PDFUpload from '@/components/PDFUpload.vue'
import posthog from 'posthog-js'

const router = useRouter()

const currentStep = ref(1)
const cvText = ref('')
const jobText = ref('')
const cvActiveTab = ref('upload')
const isLoading = ref(false)
const error = ref('')
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
const currentQuestionCategory = computed(() => questions.value[currentQuestionIndex.value]?.category || '')
const estimatedTime = computed(() => Math.round(questions.value.length * 2))

const handleCVInput = (event: Event) => {
  cvText.value = (event.target as HTMLTextAreaElement).value
  error.value = ''
}

const handleJobInput = (event: Event) => {
  jobText.value = (event.target as HTMLTextAreaElement).value
  error.value = ''
}

const handleCVTextUpdate = (text: string) => {
  cvText.value = text
  error.value = ''
}

const generateQuestions = async () => {
  if (!cvText.value || !jobText.value) {
    error.value = 'Veuillez renseigner le CV et l\'offre d\'emploi'
    return
  }

  isLoading.value = true
  error.value = ''

  try {
    const cvBlob = new Blob([cvText.value], { type: 'text/plain' })
    const cvFile = new File([cvBlob], 'cv.txt', { type: 'text/plain' })
    const result = await generateInterviewQuestions(cvFile, jobText.value, 5)

    if (result.success && result.interview_session) {
      questions.value = result.interview_session.questions
      interviewSession.value = result.interview_session
      currentStep.value = 2
      posthog.capture('interview_questions_generated', {
        question_count: result.interview_session.questions.length,
      })
    } else {
      throw new Error(result.message)
    }
  } catch (err: any) {
    error.value = err.message || 'Erreur lors de la génération des questions.'
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

const finishInterview = async () => {
  saveCurrentAnswer()

  if (questions.value.length > 0 && answers.value.length > 0) {
    try {
      isLoading.value = true
      error.value = ''
      const result = await analyzeInterviewResponses(
        questions.value,
        answers.value,
        cvText.value,
        jobText.value,
        interviewTimer.value,
      )

      if (result.success && result.analysis) {
        // Fallback local si l’historique serveur n’est pas encore disponible
        localStorage.setItem('interviewAnalysis', JSON.stringify({
          questions: questions.value,
          answers: answers.value,
          analysis: result.analysis,
          duration: interviewTimer.value,
          cv_text: cvText.value,
          job_text: jobText.value,
        }))
        posthog.capture('interview_completed', {
          answered_question_count: answers.value.length,
          duration_seconds: interviewTimer.value,
        })
        if (result.interview_id) {
          router.push({ path: '/interview-results', query: { history: result.interview_id } })
        } else {
          router.push('/interview-results')
        }
      } else {
        throw new Error(result.message || 'Erreur lors de l\'analyse')
      }
    } catch (err: any) {
      error.value = err.message || 'Erreur lors de l\'analyse'
    } finally {
      isLoading.value = false
    }
  } else {
    router.push('/interview-results')
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

const resetSimulator = () => {
  currentStep.value = 1
  cvText.value = ''
  jobText.value = ''
  questions.value = []
  isInterviewStarted.value = false
  currentQuestionIndex.value = 0
  currentAnswer.value = ''
  interviewTimer.value = 0
  answers.value = []
  error.value = ''
}

onUnmounted(() => {
  if (timerInterval) clearInterval(timerInterval)
})
</script>
