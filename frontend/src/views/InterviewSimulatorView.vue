<template>
  <div class="max-w-4xl mx-auto px-6 py-10 sm:py-16 space-y-8">
    <!-- Header -->
    <div class="text-center space-y-3">
      <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/10 text-purple-600 dark:text-purple-400 text-xs font-semibold tracking-wider uppercase">
        <span>SIMULATEUR D'ENTRETIEN</span>
      </div>
      <h1 class="text-3xl sm:text-4xl font-extrabold tracking-tight text-foreground">
        Studio d'Entraînement en Direct
      </h1>
      <p class="text-base text-muted-foreground max-w-xl mx-auto">
        Préparez-vous aux questions ciblées générées d'après les zones d'attention de votre candidature.
      </p>
    </div>

    <!-- Step 1: Upload / Input -->
    <div v-if="currentStep === 1" class="space-y-8">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Job Offer Pane -->
        <Card class="glass-card rounded-2xl overflow-hidden border border-border">
          <CardHeader class="border-b border-border bg-zinc-50/50 dark:bg-zinc-900/50">
            <CardTitle class="text-base font-bold flex items-center gap-2">
              <FileText class="h-4 w-4 text-indigo-500" />
              <span>Offre d'emploi</span>
            </CardTitle>
            <CardDescription class="text-xs">
              Saisissez l'offre d'emploi visée.
            </CardDescription>
          </CardHeader>
          <CardContent class="p-6">
            <Textarea :model-value="jobText" placeholder="Collez l'offre d'emploi..." class="min-h-[200px]" @input="handleJobInput" />
          </CardContent>
        </Card>

        <!-- CV Pane -->
        <Card class="glass-card rounded-2xl overflow-hidden border border-border">
          <CardHeader class="border-b border-border bg-zinc-50/50 dark:bg-zinc-900/50">
            <CardTitle class="text-base font-bold flex items-center justify-between">
              <div class="flex items-center gap-2">
                <User class="h-4 w-4 text-purple-500" />
                <span>Mon CV</span>
              </div>
              <div class="flex items-center gap-1 bg-zinc-200/60 dark:bg-zinc-800/80 p-1 rounded-lg">
                <button @click="cvActiveTab = 'upload'" class="px-3 py-1 text-xs font-semibold rounded-md transition-all" :class="cvActiveTab === 'upload' ? 'bg-background text-foreground shadow-sm' : 'text-muted-foreground'">
                  PDF
                </button>
                <button @click="cvActiveTab = 'manual'" class="px-3 py-1 text-xs font-semibold rounded-md transition-all" :class="cvActiveTab === 'manual' ? 'bg-background text-foreground shadow-sm' : 'text-muted-foreground'">
                  Texte
                </button>
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent class="p-6">
            <div v-if="cvActiveTab === 'upload'">
              <PDFUpload :model-value="cvText" @update:model-value="handleCVTextUpdate" />
            </div>
            <div v-else>
              <Textarea :model-value="cvText" placeholder="Collez le texte de votre CV..." class="min-h-[200px]" @input="handleCVInput" />
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- Error message -->
      <div v-if="error" class="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-600 dark:text-rose-400 text-sm">
        {{ error }}
      </div>

      <!-- Generate Questions Button -->
      <div class="flex justify-center">
        <Button @click="generateQuestions" :disabled="!cvText || !jobText || isLoading" size="lg" class="px-10 py-3.5 rounded-full font-semibold shadow-glow">
          <Loader2 v-if="isLoading" class="mr-2 h-4 w-4 animate-spin" />
          <MessageSquare v-else class="mr-2 h-4 w-4" />
          <span>Générer les questions d'entretien</span>
        </Button>
      </div>
    </div>

    <!-- Step 2: Interactive Interview Room -->
    <div v-if="currentStep === 2" class="space-y-8">
      <!-- Session Header Card -->
      <Card class="glass-card p-6 rounded-2xl border border-border flex flex-col sm:flex-row items-center justify-between gap-4">
        <div class="flex items-center gap-3">
          <Button variant="outline" size="sm" @click="resetSimulator" class="rounded-full">
            <ArrowLeft class="h-4 w-4 mr-1.5" />
            <span>Changer de sujet</span>
          </Button>
          <Button v-if="!isInterviewStarted" variant="default" size="sm" @click="startInterview" class="rounded-full shadow-glow">
            <Play class="h-4 w-4 mr-1.5" />
            <span>Lancer la simulation</span>
          </Button>
        </div>
        <div class="text-xs font-mono text-muted-foreground">
          Temps estimé : ~{{ estimatedTime }} min • {{ questions.length }} Questions
        </div>
      </Card>

      <!-- Live Interview Room -->
      <div v-if="isInterviewStarted" class="space-y-6">
        <!-- Question Card -->
        <Card class="glass-card p-8 rounded-2xl border border-border space-y-6">
          <div class="flex items-center justify-between border-b border-border pb-4">
            <span class="text-xs font-mono font-bold uppercase text-purple-500">
              Question {{ currentQuestionIndex + 1 }} / {{ questions.length }} • {{ currentQuestionCategory }}
            </span>
            <div class="text-xs font-mono px-3 py-1 rounded-full bg-zinc-100 dark:bg-zinc-800 text-foreground font-semibold">
              ⏱ {{ formatTime(interviewTimer) }}
            </div>
          </div>

          <p class="text-lg sm:text-xl font-bold text-foreground leading-snug">
            {{ currentQuestion }}
          </p>

          <!-- Answer Textarea -->
          <div class="space-y-2">
            <label for="answer" class="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Votre réponse orale ou rédigée :
            </label>
            <Textarea id="answer" v-model="currentAnswer" placeholder="Rédigez ou dictez les éléments clés de votre réponse..." class="min-h-[160px]" />
          </div>

          <!-- Controls -->
          <div class="flex items-center justify-between pt-2">
            <Button variant="outline" size="sm" @click="previousQuestion" :disabled="currentQuestionIndex === 0" class="rounded-full">
              <ChevronLeft class="h-4 w-4 mr-1" />
              Précédente
            </Button>

            <div class="flex items-center gap-2">
              <Button variant="outline" size="sm" @click="pauseInterview" v-if="!isPaused" class="rounded-full">
                <Pause class="h-4 w-4 mr-1" />
                Pause
              </Button>
              <Button variant="outline" size="sm" @click="resumeInterview" v-else class="rounded-full">
                <Play class="h-4 w-4 mr-1" />
                Reprendre
              </Button>
            </div>

            <Button size="sm" @click="nextQuestion" :disabled="currentQuestionIndex === questions.length - 1" class="rounded-full">
              Suivante
              <ChevronRight class="h-4 w-4 ml-1" />
            </Button>
          </div>
        </Card>

        <!-- Progress Bar -->
        <div class="space-y-2">
          <div class="flex justify-between text-xs font-mono text-muted-foreground">
            <span>Progression de l'entretien</span>
            <span>{{ Math.round(((currentQuestionIndex + 1) / questions.length) * 100) }}%</span>
          </div>
          <div class="w-full bg-zinc-200 dark:bg-zinc-800 rounded-full h-2 overflow-hidden">
            <div class="bg-purple-500 h-2 rounded-full transition-all duration-300" :style="{ width: `${((currentQuestionIndex + 1) / questions.length) * 100}%` }"></div>
          </div>
        </div>

        <!-- Finish Banner -->
        <div v-if="currentQuestionIndex === questions.length - 1" class="text-center pt-4">
          <Card class="glass-card p-8 rounded-2xl border-purple-500/30 space-y-4">
            <CheckCircle class="h-12 w-12 text-emerald-500 mx-auto" />
            <h3 class="text-xl font-bold text-foreground">Toutes les questions sont complétées !</h3>
            <p class="text-sm text-muted-foreground">
              Obtenez une évaluation détaillée de vos réponses.
            </p>

            <div v-if="error" class="p-3 rounded-lg bg-rose-500/10 text-rose-500 text-xs">
              {{ error }}
            </div>

            <Button size="lg" @click="finishInterview" :disabled="isLoading" class="rounded-full shadow-glow">
              <Loader2 v-if="isLoading" class="mr-2 h-4 w-4 animate-spin" />
              <span>{{ isLoading ? 'Analyse des réponses...' : 'Obtenir le rapport d\'entretien' }}</span>
            </Button>
          </Card>
        </div>
      </div>

      <!-- Preview Mode -->
      <div v-else class="space-y-4">
        <div v-for="(q, idx) in questions" :key="idx" class="p-5 rounded-2xl bg-card border border-border space-y-2">
          <div class="flex items-center gap-2">
            <span class="text-xs font-mono font-bold text-purple-500">Question {{ idx + 1 }}</span>
            <span class="text-[10px] uppercase font-semibold px-2 py-0.5 rounded bg-zinc-100 dark:bg-zinc-800 text-muted-foreground">
              {{ q.category }}
            </span>
          </div>
          <p class="text-sm font-semibold text-foreground">{{ q.text }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import {
  FileText, User, Upload, Edit, CheckCircle, Loader2, Play, Pause, ChevronLeft, ChevronRight, MessageSquare, ArrowLeft
} from 'lucide-vue-next'
import { generateInterviewQuestions, analyzeInterviewResponses } from '@/lib/api'
import PDFUpload from '@/components/PDFUpload.vue'

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
let timerInterval: any = null

const currentQuestion = computed(() => questions.value[currentQuestionIndex.value]?.text || '')
const currentQuestionCategory = computed(() => questions.value[currentQuestionIndex.value]?.category || '')
const estimatedTime = computed(() => Math.round(questions.value.length * 2))

const handleCVInput = (event: Event) => {
  const target = event.target as HTMLTextAreaElement
  cvText.value = target.value
  error.value = ''
}

const handleJobInput = (event: Event) => {
  const target = event.target as HTMLTextAreaElement
  jobText.value = target.value
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
      time: 0
    }

    const existingIndex = answers.value.findIndex(a => a.questionIndex === currentQuestionIndex.value)
    if (existingIndex >= 0) {
      answers.value[existingIndex] = answerData
    } else {
      answers.value.push(answerData)
    }
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
        jobText.value
      )

      if (result.success && result.analysis) {
        const analysisData = {
          questions: questions.value,
          answers: answers.value,
          analysis: result.analysis,
          duration: interviewTimer.value,
          cv_text: cvText.value,
          job_text: jobText.value
        }

        localStorage.setItem('interviewAnalysis', JSON.stringify(analysisData))
        router.push('/interview-results')
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
    if (!isPaused.value) {
      interviewTimer.value++
    }
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
