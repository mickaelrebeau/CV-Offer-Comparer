<template>
    <div class="max-w-4xl mx-auto">
        <!-- Header -->
        <div class="text-center space-y-4 py-8">
            <h1 class="text-3xl font-bold text-primary">
                Simulateur d'entretien
            </h1>
            <p class="text-lg text-muted-foreground">
                Préparez-vous aux entretiens avec des questions personnalisées basées sur votre CV et l'offre d'emploi
            </p>
        </div>

        <!-- Étape 1: Upload des documents -->
        <div v-if="currentStep === 1" class="space-y-6">
            <!-- Zone de saisie -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <!-- Offre d'emploi -->
                <Card>
                    <CardHeader>
                        <CardTitle class="flex items-center space-x-2">
                            <FileText class="h-5 w-5" />
                            <span>Offre d'emploi</span>
                        </CardTitle>
                        <CardDescription>
                            Uploadez l'offre d'emploi PDF ou saisissez le texte manuellement
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <Textarea :model-value="jobText" placeholder="Collez le texte de l'offre d'emploi..." @input="handleJobInput" />
                    </CardContent>
                </Card>

                <!-- CV avec onglets -->
                <Card>
                    <CardHeader>
                        <CardTitle class="flex items-center space-x-2">
                            <User class="h-5 w-5" />
                            <span>Mon CV</span>
                        </CardTitle>
                        <CardDescription>
                            Uploadez votre CV PDF ou saisissez le texte manuellement
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <!-- Onglets -->
                        <div class="flex border-b border-border mb-4">
                            <button @click="cvActiveTab = 'upload'"
                                class="px-4 py-2 text-sm font-medium transition-colors duration-200 flex items-center space-x-2 border-b-2"
                                :class="cvActiveTab === 'upload'
                                    ? 'border-primary text-primary bg-primary/5'
                                    : 'border-transparent text-muted-foreground hover:text-foreground hover:bg-muted/50'">
                                <Upload class="h-4 w-4" />
                                <span>Upload PDF</span>
                            </button>
                            <button @click="cvActiveTab = 'manual'"
                                class="px-4 py-2 text-sm font-medium transition-colors duration-200 flex items-center space-x-2 border-b-2"
                                :class="cvActiveTab === 'manual'
                                    ? 'border-primary text-primary bg-primary/5'
                                    : 'border-transparent text-muted-foreground hover:text-foreground hover:bg-muted/50'">
                                <Edit class="h-4 w-4" />
                                <span>Saisie manuelle</span>
                            </button>
                        </div>

                        <!-- Contenu des onglets -->
                        <div v-if="cvActiveTab === 'upload'">
                            <PDFUpload :model-value="cvText" @update:model-value="handleCVTextUpdate" />
                        </div>

                        <div v-else-if="cvActiveTab === 'manual'">
                            <div class="mb-4">
                                <p class="text-sm text-muted-foreground">
                                    Vous pouvez également saisir le texte de votre CV manuellement.
                                </p>
                            </div>
                            <Textarea :model-value="cvText" placeholder="Collez le texte de votre CV..."
                                @input="handleCVInput" />
                        </div>
                    </CardContent>
                </Card>
            </div>

            <!-- Message d'erreur -->
            <div v-if="error" class="bg-destructive/10 border border-destructive text-destructive px-4 py-3 rounded-md">
                {{ error }}
            </div>

            <!-- Bouton de génération -->
            <div class="flex justify-center items-center flex-col">
                <Button @click="generateQuestions" :disabled="!cvText || !jobText || isLoading"
                    class="px-8 py-3 p-2 flex items-center justify-center rounded-md border-2 border-primary disabled:opacity-50">
                    <Loader2 v-if="isLoading" class="mr-2 h-4 w-4 animate-spin" />
                    <MessageSquare class="mr-2 h-4 w-4" />
                    Générer les questions d'entretien
                </Button>
            </div>
        </div>

        <!-- Étape 2: Questions générées -->
        <div v-if="currentStep === 2">
            <!-- Informations sur l'entretien -->
            <Card class="mb-6">
                <CardHeader>
                    <CardTitle class="flex items-center gap-2">
                        <span
                            class="w-8 h-8 bg-green-500 text-white rounded-full flex items-center justify-center text-sm font-bold">2</span>
                        Questions d'entretien générées
                    </CardTitle>
                    <CardDescription>
                        {{ questions.length }} questions personnalisées basées sur votre profil et l'offre d'emploi
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <div class="flex items-center justify-between mb-4">
                        <div class="flex items-center gap-4">
                            <Button variant="outline" @click="startInterview" :disabled="isInterviewStarted">
                                <Play class="h-4 w-4 mr-2" />
                                Commencer l'entretien
                            </Button>
                            <Button variant="outline" @click="resetSimulator">
                                <RotateCcw class="h-4 w-4 mr-2" />
                                Recommencer
                            </Button>
                        </div>
                        <div class="text-sm text-muted-foreground">
                            Temps estimé : {{ estimatedTime }} minutes
                        </div>
                    </div>
                </CardContent>
            </Card>

            <!-- Mode entretien -->
            <div v-if="isInterviewStarted" class="space-y-6">
                <!-- Question actuelle -->
                <Card>
                    <CardHeader>
                        <div class="flex items-center justify-between">
                            <CardTitle>Question {{ currentQuestionIndex + 1 }} / {{ questions.length }}</CardTitle>
                            <div class="text-sm text-muted-foreground">
                                {{ formatTime(interviewTimer) }}
                            </div>
                        </div>
                    </CardHeader>
                    <CardContent>
                        <div class="space-y-4">
                            <div class="flex items-center gap-2 mb-4">
                                <span class="text-xs bg-primary/10 text-primary px-2 py-1 rounded-full">
                                    {{ currentQuestionCategory }}
                                </span>
                            </div>
                            <p class="text-lg font-medium">{{ currentQuestion }}</p>

                            <!-- Zone de réponse -->
                            <div class="space-y-2">
                                <Label for="answer">Votre réponse</Label>
                                <Textarea id="answer" v-model="currentAnswer" placeholder="Tapez votre réponse ici..."
                                    class="min-h-[120px]" />
                            </div>

                            <!-- Contrôles -->
                            <div class="flex items-center justify-between">
                                <Button variant="outline" @click="previousQuestion"
                                    :disabled="currentQuestionIndex === 0">
                                    <ChevronLeft class="h-4 w-4 mr-2" />
                                    Précédente
                                </Button>

                                <div class="flex items-center gap-2">
                                    <Button variant="outline" @click="pauseInterview" v-if="!isPaused">
                                        <Pause class="h-4 w-4 mr-2" />
                                        Pause
                                    </Button>
                                    <Button variant="outline" @click="resumeInterview" v-else>
                                        <Play class="h-4 w-4 mr-2" />
                                        Reprendre
                                    </Button>
                                </div>

                                <Button @click="nextQuestion" :disabled="currentQuestionIndex === questions.length - 1">
                                    Suivante
                                    <ChevronRight class="h-4 w-4 ml-2" />
                                </Button>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <!-- Progression -->
                <Card>
                    <CardContent class="p-6">
                        <div class="space-y-2">
                            <div class="flex justify-between text-sm">
                                <span>Progression</span>
                                <span>{{ Math.round(((currentQuestionIndex + 1) / questions.length) * 100) }}%</span>
                            </div>
                            <div class="w-full bg-muted rounded-full h-2">
                                <div class="bg-primary h-2 rounded-full transition-all duration-300"
                                    :style="{ width: `${((currentQuestionIndex + 1) / questions.length) * 100}%` }">
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <!-- Fin de l'entretien -->
                <div v-if="currentQuestionIndex === questions.length - 1" class="text-center">
                    <Card>
                        <CardContent class="p-6">
                            <div class="space-y-4">
                                <CheckCircle class="h-12 w-12 text-green-500 mx-auto" />
                                <h3 class="text-lg font-semibold">Entretien terminé !</h3>
                                <p class="text-muted-foreground">
                                    Vous avez répondu à toutes les questions en {{ formatTime(interviewTimer) }}
                                </p>
                                <Button @click="finishInterview" class="mt-4">
                                    Terminer et sauvegarder
                                </Button>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>

            <!-- Liste des questions (mode aperçu) -->
            <div v-else class="space-y-4">
                <div v-for="(question, index) in questions" :key="index"
                    class="p-4 border rounded-lg hover:bg-muted/50 transition-colors cursor-pointer"
                    @click="goToQuestion(index)">
                    <div class="flex items-start justify-between">
                        <div class="flex-1">
                            <div class="flex items-center gap-2 mb-2">
                                <span class="text-sm font-medium text-primary">Question {{ index + 1 }}</span>
                                <span class="text-xs bg-primary/10 text-primary px-2 py-1 rounded-full">{{ question.category }}</span>
                            </div>
                            <p class="text-sm">{{ question.text }}</p>
                        </div>
                        <ChevronRight class="h-4 w-4 text-muted-foreground" />
                    </div>
                </div>
            </div>
        </div>

        <!-- Étape 3: Résultats de l'analyse IA -->
        <div v-if="currentStep === 3" class="space-y-6">
            <!-- Header des résultats -->
            <Card class="mb-6">
                <CardHeader>
                    <CardTitle class="flex items-center gap-2">
                        <span class="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-bold">3</span>
                        Analyse de vos réponses
                    </CardTitle>
                    <CardDescription>
                        Analyse personnalisée de vos performances par notre IA
                    </CardDescription>
                </CardHeader>
            </Card>

            <!-- Chargement de l'analyse -->
            <div v-if="isAnalyzing" class="text-center py-12">
                <Loader2 class="h-12 w-12 animate-spin mx-auto mb-4" />
                <h3 class="text-lg font-medium mb-2">Analyse en cours...</h3>
                <p class="text-muted-foreground">Notre IA analyse vos réponses pour vous donner des conseils personnalisés</p>
            </div>

            <!-- Résultats de l'analyse -->
            <div v-else-if="analysisResult" class="space-y-6">
                <!-- Score global -->
                <Card>
                    <CardHeader>
                        <CardTitle>Score global</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div class="text-center">
                            <div class="text-4xl font-bold text-primary mb-2">{{ analysisResult.score_global }}/10</div>
                            <div class="text-sm text-muted-foreground">
                                {{ analysisResult.score_global >= 8 ? 'Excellent !' : 
                                   analysisResult.score_global >= 6 ? 'Bon travail !' : 
                                   analysisResult.score_global >= 4 ? 'À améliorer' : 'Besoin de pratique' }}
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <!-- Points forts -->
                <Card>
                    <CardHeader>
                        <CardTitle class="flex items-center gap-2">
                            <CheckCircle class="h-5 w-5 text-green-500" />
                            Vos points forts
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div class="space-y-2">
                            <div v-for="(point, index) in analysisResult.points_forts" :key="index" 
                                class="flex items-center gap-2 p-3 bg-green-50 rounded-lg">
                                <CheckCircle class="h-4 w-4 text-green-500" />
                                <span class="text-sm">{{ point }}</span>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <!-- Points d'amélioration -->
                <Card>
                    <CardHeader>
                        <CardTitle class="flex items-center gap-2">
                            <MessageSquare class="h-5 w-5 text-orange-500" />
                            Points d'amélioration
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div class="space-y-2">
                            <div v-for="(point, index) in analysisResult.points_amelioration" :key="index" 
                                class="flex items-center gap-2 p-3 bg-orange-50 rounded-lg">
                                <MessageSquare class="h-4 w-4 text-orange-500" />
                                <span class="text-sm">{{ point }}</span>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <!-- Suggestions personnalisées -->
                <Card>
                    <CardHeader>
                        <CardTitle class="flex items-center gap-2">
                            <Lightbulb class="h-5 w-5 text-blue-500" />
                            Suggestions d'amélioration
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div class="space-y-4">
                            <div v-for="(suggestion, index) in analysisResult.suggestions" :key="index" 
                                class="border rounded-lg p-4">
                                <div class="flex items-start gap-3">
                                    <div class="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center mt-0.5">
                                        <span class="text-xs font-bold text-blue-600">{{ index + 1 }}</span>
                                    </div>
                                    <div class="flex-1">
                                        <div class="flex items-center gap-2 mb-2">
                                            <h4 class="font-medium text-blue-700">{{ suggestion.titre }}</h4>
                                            <span class="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">
                                                {{ suggestion.priorite }}
                                            </span>
                                        </div>
                                        <p class="text-sm text-muted-foreground">{{ suggestion.description }}</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <!-- Conseils spécifiques -->
                <Card v-if="analysisResult.conseils_specifiques && analysisResult.conseils_specifiques.length > 0">
                    <CardHeader>
                        <CardTitle class="flex items-center gap-2">
                            <Edit class="h-5 w-5 text-purple-500" />
                            Conseils spécifiques
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div class="space-y-4">
                            <div v-for="(conseil, index) in analysisResult.conseils_specifiques" :key="index" 
                                class="border rounded-lg p-4">
                                <div class="flex items-start gap-3">
                                    <div class="w-6 h-6 bg-purple-100 rounded-full flex items-center justify-center mt-0.5">
                                        <span class="text-xs font-bold text-purple-600">{{ index + 1 }}</span>
                                    </div>
                                    <div class="flex-1">
                                        <h4 class="font-medium text-purple-700 mb-1">{{ conseil.question }}</h4>
                                        <p class="text-sm text-muted-foreground">{{ conseil.conseil }}</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <!-- Actions -->
                <div class="flex justify-center gap-4 pt-6">
                    <Button variant="outline" @click="resetSimulator">
                        <RotateCcw class="h-4 w-4 mr-2" />
                        Nouvel entretien
                    </Button>
                    <Button @click="goToDashboard">
                        <ArrowLeft class="h-4 w-4 mr-2" />
                        Retour au dashboard
                    </Button>
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
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { 
  FileText, 
  User,
  Upload,
  Edit,
  CheckCircle, 
  Loader2, 
  Play, 
  Pause, 
  RotateCcw,
  ChevronLeft,
  ChevronRight,
  MessageSquare,
  Lightbulb,
  ArrowLeft
} from 'lucide-vue-next'
import { generateInterviewQuestions, analyzeInterviewResponses } from '@/lib/api'
import PDFUpload from '@/components/PDFUpload.vue'

const router = useRouter()

// État de l'application
const currentStep = ref(1)
const cvText = ref('')
const jobText = ref('')
const cvActiveTab = ref('upload')
const jobActiveTab = ref('upload')
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
const isAnalyzing = ref(false)
const analysisResult = ref<any>(null)
let timerInterval: NodeJS.Timeout | null = null

// Calculs
const currentQuestion = computed(() => {
  return questions.value[currentQuestionIndex.value]?.text || ''
})

const currentQuestionCategory = computed(() => {
  return questions.value[currentQuestionIndex.value]?.category || ''
})

const estimatedTime = computed(() => {
  return Math.round(questions.value.length * 2) // 2 minutes par question
})

// Gestion des inputs
const handleCVInput = (event: Event) => {
  const target = event.target as HTMLTextAreaElement
  cvText.value = target.value
  error.value = '' // Effacer l'erreur quand l'utilisateur tape
}

const handleJobInput = (event: Event) => {
  const target = event.target as HTMLTextAreaElement
  jobText.value = target.value
  error.value = '' // Effacer l'erreur quand l'utilisateur tape
}

const handleCVTextUpdate = (text: string) => {
  cvText.value = text
  error.value = ''
}

const handleJobTextUpdate = (text: string) => {
  jobText.value = text
  error.value = ''
}

// Génération des questions
const generateQuestions = async () => {
  if (!cvText.value || !jobText.value) {
    error.value = 'Veuillez remplir le CV et l\'offre d\'emploi'
    return
  }

  isLoading.value = true
  error.value = ''
  
  try {
    // Créer un fichier temporaire pour le CV
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
  } catch (error: any) {
    console.error('Erreur lors de la génération des questions:', error)
    error.value = error.message || 'Erreur lors de la génération des questions'
    // Fallback avec des questions simulées en cas d'erreur
    questions.value = [
      {
        text: "Pouvez-vous nous parler de votre expérience en développement web et comment elle s'applique à ce poste ?",
        category: "Expérience"
      },
      {
        text: "Quels sont vos points forts techniques et comment les utilisez-vous dans vos projets ?",
        category: "Compétences"
      },
      {
        text: "Comment gérez-vous les délais serrés et les priorités multiples ?",
        category: "Soft Skills"
      },
      {
        text: "Pouvez-vous nous donner un exemple de projet où vous avez dû résoudre un problème technique complexe ?",
        category: "Problème"
      },
      {
        text: "Pourquoi souhaitez-vous rejoindre notre entreprise et ce poste en particulier ?",
        category: "Motivation"
      }
    ]
    currentStep.value = 2
  } finally {
    isLoading.value = false
  }
}

// Navigation
const goToDashboard = () => {
  router.push('/dashboard')
}

// Navigation dans l'entretien
const startInterview = () => {
  isInterviewStarted.value = true
  startTimer()
}

const nextQuestion = () => {
  // Sauvegarder la réponse actuelle
  saveCurrentAnswer()
  
  if (currentQuestionIndex.value < questions.value.length - 1) {
    currentQuestionIndex.value++
    currentAnswer.value = ''
  }
}

const previousQuestion = () => {
  // Sauvegarder la réponse actuelle
  saveCurrentAnswer()
  
  if (currentQuestionIndex.value > 0) {
    currentQuestionIndex.value--
    currentAnswer.value = ''
  }
}

const goToQuestion = (index: number) => {
  // Sauvegarder la réponse actuelle
  saveCurrentAnswer()
  
  currentQuestionIndex.value = index
  currentAnswer.value = ''
}

const finishInterview = async () => {
  // Analyser les réponses avec l'IA
  await analyzeResponses()
}

// Analyser les réponses avec l'IA
const analyzeResponses = async () => {
  if (!questions.value.length || !answers.value.length) {
    error.value = 'Aucune réponse à analyser'
    return
  }

  isAnalyzing.value = true
  error.value = ''
  
  try {
    const result = await analyzeInterviewResponses(
      questions.value,
      answers.value,
      cvText.value,
      jobText.value
    )
    
    if (result.success && result.analysis) {
      analysisResult.value = result.analysis
      currentStep.value = 3 // Passer à l'étape des résultats
    } else {
      throw new Error(result.message)
    }
  } catch (error: any) {
    console.error('Erreur lors de l\'analyse des réponses:', error)
    error.value = error.message || 'Erreur lors de l\'analyse des réponses'
    // Fallback : passer quand même aux résultats
    currentStep.value = 3
  } finally {
    isAnalyzing.value = false
  }
}

// Sauvegarder la réponse actuelle
const saveCurrentAnswer = () => {
  if (currentAnswer.value.trim()) {
    const answerData = {
      questionIndex: currentQuestionIndex.value,
      question: questions.value[currentQuestionIndex.value]?.text || '',
      category: questions.value[currentQuestionIndex.value]?.category || '',
      answer: currentAnswer.value,
      time: 0 // TODO: calculer le temps par question
    }
    
    // Mettre à jour ou ajouter la réponse
    const existingIndex = answers.value.findIndex(a => a.questionIndex === currentQuestionIndex.value)
    if (existingIndex >= 0) {
      answers.value[existingIndex] = answerData
    } else {
      answers.value.push(answerData)
    }
  }
}

// Timer
const startTimer = () => {
  timerInterval = setInterval(() => {
    if (!isPaused.value) {
      interviewTimer.value++
    }
  }, 1000)
}

const pauseInterview = () => {
  isPaused.value = true
}

const resumeInterview = () => {
  isPaused.value = false
}

const formatTime = (seconds: number) => {
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
}

// Reset
const resetSimulator = () => {
  currentStep.value = 1
  cvText.value = ''
  jobText.value = ''
  cvActiveTab.value = 'upload'
  jobActiveTab.value = 'upload'
  questions.value = []
  isInterviewStarted.value = false
  currentQuestionIndex.value = 0
  currentAnswer.value = ''
  interviewTimer.value = 0
  isPaused.value = false
  interviewSession.value = null
  answers.value = []
  isAnalyzing.value = false
  analysisResult.value = null
  error.value = ''
}

// Cleanup
onUnmounted(() => {
  if (timerInterval) {
    clearInterval(timerInterval)
  }
  // Sauvegarder la session à la fermeture
  // saveSession() // Removed as per edit hint
})
</script>