<template>
    <div class="max-w-4xl mx-auto">
        <!-- Header -->
        <div class="text-center space-y-4 py-8">
            <h1 class="text-3xl font-bold text-primary">
                Résultats de votre entretien
            </h1>
            <p class="text-lg text-muted-foreground">
                Analysez vos performances et découvrez des suggestions d'amélioration
            </p>
        </div>

        <!-- Chargement -->
        <div v-if="isLoading" class="text-center py-12">
            <Loader2 class="h-12 w-12 animate-spin mx-auto mb-4" />
            <h3 class="text-lg font-medium mb-2">Chargement des résultats...</h3>
            <p class="text-muted-foreground">Récupération de vos données d'entretien</p>
        </div>

        <!-- Erreur -->
        <div v-else-if="error" class="text-center py-12">
            <AlertCircle class="h-12 w-12 text-destructive mx-auto mb-4" />
            <h3 class="text-lg font-medium mb-2">Aucune analyse trouvée</h3>
            <p class="text-muted-foreground">{{ error }}</p>
            <div class="flex justify-center gap-4 mt-6">
                <Button @click="loadInterviewData" variant="outline">
                    <RotateCcw class="h-4 w-4 mr-2" />
                    Réessayer
                </Button>
                <Button @click="startNewInterview">
                    <MessageSquare class="h-4 w-4 mr-2" />
                    Commencer un entretien
                </Button>
            </div>
        </div>

        <!-- Contenu principal -->
        <div v-else-if="interviewData" class="space-y-6">
            <!-- Statistiques générales -->
            <Card class="mb-6">
                <CardHeader>
                    <CardTitle>Résumé de votre entretien</CardTitle>
                </CardHeader>
                <CardContent>
                    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
                        <div class="text-center">
                            <div class="text-2xl font-bold text-primary">{{ interviewData.num_questions }}</div>
                            <div class="text-sm text-muted-foreground">Questions répondues</div>
                        </div>
                        <div class="text-center">
                            <div class="text-2xl font-bold text-blue-500">{{ formatTime(interviewData.duration) }}</div>
                            <div class="text-sm text-muted-foreground">Temps total</div>
                        </div>
                        <div class="text-center">
                            <div class="text-2xl font-bold text-green-500">{{ averageTimePerQuestion }}</div>
                            <div class="text-sm text-muted-foreground">Temps moyen/question</div>
                        </div>
                        <div class="text-center">
                            <div class="text-2xl font-bold text-purple-500">{{ completionRate }}%</div>
                            <div class="text-sm text-muted-foreground">Taux de complétion</div>
                        </div>
                    </div>
                </CardContent>
            </Card>

            <!-- Score global -->
            <Card class="mb-6">
                <CardHeader>
                    <CardTitle class="flex items-center gap-2">
                        <Trophy class="h-5 w-5 text-yellow-500" />
                        Score global
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div class="text-center">
                        <div class="text-4xl font-bold text-primary mb-2">{{ analysisResult?.score_global || 'N/A' }}/10
                        </div>
                        <div class="text-sm text-muted-foreground">
                            {{ getScoreMessage(analysisResult?.score_global) }}
                        </div>
                    </div>
                </CardContent>
            </Card>

            <!-- Analyse par catégorie -->
            <Card class="mb-6">
                <CardHeader>
                    <CardTitle>Analyse par catégorie</CardTitle>
                </CardHeader>
                <CardContent>
                    <div class="space-y-4">
                        <div v-for="category in categoryStats" :key="category.name" class="space-y-2">
                            <div class="flex items-center justify-between">
                                <div class="flex items-center gap-2">
                                    <span class="text-sm font-medium">{{ category.name }}</span>
                                    <span class="text-xs bg-primary/10 text-primary px-2 py-1 rounded-full">
                                        {{ category.count }} question{{ category.count > 1 ? 's' : '' }}
                                    </span>
                                </div>
                                <div class="text-sm text-muted-foreground">
                                    Temps moyen: {{ category.avgTime }}
                                </div>
                            </div>
                            <div class="w-full bg-muted rounded-full h-2">
                                <div class="bg-primary h-2 rounded-full transition-all duration-300"
                                    :style="{ width: `${category.percentage}%` }">
                                </div>
                            </div>
                        </div>
                    </div>
                </CardContent>
            </Card>

            <!-- Points forts -->
            <Card v-if="analysisResult?.points_forts?.length" class="mb-6">
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
            <Card v-if="analysisResult?.points_amelioration?.length" class="mb-6">
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

            <!-- Détail des réponses -->
            <Card class="mb-6">
                <CardHeader>
                    <CardTitle>Détail de vos réponses</CardTitle>
                </CardHeader>
                <CardContent>
                    <div class="space-y-6">
                        <div v-for="(answer, index) in interviewData.answers" :key="index"
                            class="border rounded-lg p-4">
                            <div class="flex items-start justify-between mb-3">
                                <div class="flex items-center gap-2">
                                    <span class="text-sm font-medium text-primary">Question {{ index + 1 }}</span>
                                    <span class="text-xs bg-primary/10 text-primary px-2 py-1 rounded-full">
                                        {{ answer.category }}
                                    </span>
                                </div>
                                <div class="text-xs text-muted-foreground">
                                    {{ formatTime(answer.time || 0) }}
                                </div>
                            </div>
                            <div class="space-y-2">
                                <p class="text-sm font-medium">{{ answer.question }}</p>
                                <div class="bg-muted/50 rounded p-3">
                                    <p class="text-sm">{{ answer.answer || 'Aucune réponse fournie' }}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </CardContent>
            </Card>

            <!-- Suggestions d'amélioration -->
            <Card class="mb-6">
                <CardHeader>
                    <CardTitle class="flex items-center gap-2">
                        <Lightbulb class="h-5 w-5" />
                        Suggestions d'amélioration
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div class="space-y-4">
                        <div v-for="(suggestion, index) in suggestions" :key="index" class="flex items-start gap-3">
                            <div class="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center mt-0.5">
                                <span class="text-xs font-bold text-blue-600">{{ index + 1 }}</span>
                            </div>
                            <div>
                                <h4 class="font-medium text-blue-700">{{ suggestion.title }}</h4>
                                <p class="text-sm text-muted-foreground mt-1">{{ suggestion.description }}</p>
                            </div>
                        </div>
                    </div>
                </CardContent>
            </Card>

            <!-- Actions -->
            <div class="flex justify-center gap-4">
                <Button variant="outline" @click="goToDashboard">
                    <ArrowLeft class="h-4 w-4 mr-2" />
                    Retour au dashboard
                </Button>
                <Button @click="startNewInterview">
                    <RotateCcw class="h-4 w-4 mr-2" />
                    Nouvel entretien
                </Button>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import {
    Lightbulb,
    ArrowLeft,
    RotateCcw,
    CheckCircle,
    MessageSquare,
    Trophy,
    AlertCircle,
    Loader2
} from 'lucide-vue-next'


interface InterviewAnswer {
    question: string
    answer: string
    category: string
    time: number
}

interface InterviewData {
    id: string
    num_questions: number
    duration: number
    completed: boolean
    answers: InterviewAnswer[]
}

interface AnalysisResult {
    score_global: number
    points_forts: string[]
    points_amelioration: string[]
    suggestions: Array<{
        titre: string
        description: string
        priorite: string
    }>
    conseils_specifiques?: Array<{
        question: string
        conseil: string
    }>
}

interface Suggestion {
    title: string
    description: string
}

const router = useRouter()
const route = useRoute()

// État de l'application
const isLoading = ref(true)
const error = ref('')
const interviewData = ref<InterviewData | null>(null)
const analysisResult = ref<AnalysisResult | null>(null)

// Calculs
const averageTimePerQuestion = computed(() => {
    if (!interviewData.value) return '0:00'
    const totalTime = interviewData.value.answers.reduce((sum, answer) => sum + (answer.time || 0), 0)
    const avgSeconds = totalTime / interviewData.value.answers.length
    return formatTime(avgSeconds)
})

const completionRate = computed(() => {
    if (!interviewData.value) return 0
    const answeredQuestions = interviewData.value.answers.filter(a => a.answer && a.answer.trim().length > 0).length
    return Math.round((answeredQuestions / interviewData.value.num_questions) * 100)
})

const categoryStats = computed(() => {
    if (!interviewData.value) return []

    const stats: { [key: string]: { count: number, totalTime: number, answers: InterviewAnswer[] } } = {}

    interviewData.value.answers.forEach(answer => {
        if (!stats[answer.category]) {
            stats[answer.category] = { count: 0, totalTime: 0, answers: [] }
        }
        stats[answer.category].count++
        stats[answer.category].totalTime += answer.time || 0
        stats[answer.category].answers.push(answer)
    })

    return Object.entries(stats).map(([name, data]) => ({
        name,
        count: data.count,
        avgTime: formatTime(data.totalTime / data.count),
        percentage: (data.count / interviewData.value!.num_questions) * 100
    }))
})

const suggestions = computed((): Suggestion[] => {
    const suggestions: Suggestion[] = []

    if (!interviewData.value) return suggestions

    // Suggestion basée sur le temps de réponse
    const avgTime = interviewData.value.answers.reduce((sum, a) => sum + (a.time || 0), 0) / interviewData.value.answers.length
    if (avgTime < 60) {
        suggestions.push({
            title: "Prenez plus de temps pour réfléchir",
            description: "Vos réponses sont rapides, mais prenez le temps de structurer vos pensées pour des réponses plus complètes."
        })
    } else if (avgTime > 300) {
        suggestions.push({
            title: "Améliorez votre concision",
            description: "Vos réponses sont détaillées, mais essayez d'être plus concis pour maintenir l'attention de l'interviewer."
        })
    }

    // Suggestion basée sur les réponses vides
    const emptyAnswers = interviewData.value.answers.filter(a => !a.answer || a.answer.trim().length < 10).length
    if (emptyAnswers > 0) {
        suggestions.push({
            title: "Préparez des exemples concrets",
            description: "Préparez des exemples spécifiques de vos expériences pour chaque type de question."
        })
    }

    // Suggestions générales
    suggestions.push({
        title: "Pratiquez régulièrement",
        description: "Utilisez ce simulateur régulièrement pour améliorer vos compétences d'entretien."
    })

    suggestions.push({
        title: "Analysez vos réponses",
        description: "Revenez sur vos réponses pour identifier les points d'amélioration."
    })

    return suggestions
})

// Fonctions utilitaires
const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
}

const getScoreMessage = (score: number | undefined) => {
    if (!score) return 'Non évalué'
    if (score >= 8) return 'Excellent !'
    if (score >= 6) return 'Bon travail !'
    if (score >= 4) return 'À améliorer'
    return 'Besoin de pratique'
}

// Charger les données de l'entretien
const loadInterviewData = async () => {
    isLoading.value = true
    error.value = ''

    try {
        // Récupérer les données d'analyse depuis localStorage
        const storedAnalysis = localStorage.getItem('interviewAnalysis')

        if (storedAnalysis) {
            const analysisData = JSON.parse(storedAnalysis)

            // Convertir le format des données
            interviewData.value = {
                id: 'analysis-session',
                num_questions: analysisData.questions.length,
                duration: analysisData.duration,
                completed: true,
                answers: analysisData.answers.map((answer: any, index: number) => ({
                    question: answer.question,
                    answer: answer.answer,
                    category: answer.category,
                    time: answer.time || 0
                }))
            }

            analysisResult.value = analysisData.analysis

            // Nettoyer le localStorage
            localStorage.removeItem('interviewAnalysis')
            return
        }

        // Si aucune donnée d'analyse n'est trouvée, afficher un message d'erreur
        error.value = 'Aucune analyse d\'entretien trouvée. Veuillez compléter un entretien pour voir les résultats.'

    } catch (err: any) {
        console.error('Erreur lors du chargement des résultats:', err)
        error.value = err.message || 'Erreur lors du chargement des résultats'
    } finally {
        isLoading.value = false
    }
}

// Navigation
const goToDashboard = () => {
    router.push('/dashboard')
}

const startNewInterview = () => {
    router.push('/interview-simulator')
}

// Charger les données au montage
onMounted(() => {
    loadInterviewData()
})
</script> 