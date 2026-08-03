<template>
  <div class="page-shell">
    <AppPageHeader
      label="Rapport"
      title="Résultats de la simulation"
      description="Évaluation synthétique et recommandations pour perfectionner vos arguments."
    />

    <div v-if="isLoading" class="py-16 text-center">
      <Loader2 class="mx-auto h-8 w-8 animate-spin text-ink-soft" />
      <p class="mt-4 font-mono text-micro uppercase text-ink-soft">Récupération des résultats...</p>
    </div>

    <div v-else-if="error" class="py-16 text-center space-y-6">
      <AlertCircle class="mx-auto h-10 w-10 text-rose-500" />
      <p class="text-lead text-ink-soft">{{ error }}</p>
      <Button @click="startNewInterview">
        <MessageSquare class="mr-2 h-4 w-4" />
        Nouveau simulateur
      </Button>
    </div>

    <div v-else-if="interviewData" class="space-y-8">
      <div class="grid grid-cols-1 gap-4 md:grid-cols-4">
        <div class="panel p-6 text-center md:col-span-2">
          <div class="mb-1 font-mono text-micro uppercase text-ink-soft">Score global</div>
          <div class="text-4xl font-medium tabular-nums">{{ analysisResult?.score_global || 'N/A' }}/10</div>
          <p class="mt-1 font-mono text-micro uppercase text-emerald-600">{{ getScoreMessage(analysisResult?.score_global) }}</p>
        </div>
        <div class="panel p-6 text-center">
          <div class="mb-1 font-mono text-micro uppercase text-ink-soft">Questions</div>
          <div class="text-3xl font-medium tabular-nums">{{ interviewData.num_questions }}</div>
        </div>
        <div class="panel p-6 text-center">
          <div class="mb-1 font-mono text-micro uppercase text-ink-soft">Durée</div>
          <div class="text-3xl font-medium tabular-nums">{{ formatTime(interviewData.duration) }}</div>
        </div>
      </div>

      <div v-if="analysisResult?.points_forts?.length" class="panel p-6 space-y-4">
        <h3 class="flex items-center gap-2 font-mono text-caption uppercase">
          <CheckCircle class="h-4 w-4 text-emerald-500" />
          Points forts
        </h3>
        <div class="space-y-2">
          <div v-for="(pf, idx) in analysisResult.points_forts" :key="idx" class="rounded-lg border border-emerald-500/20 bg-emerald-500/5 p-3 text-sm text-emerald-800">
            {{ pf }}
          </div>
        </div>
      </div>

      <div v-if="analysisResult?.points_amelioration?.length" class="panel p-6 space-y-4">
        <h3 class="flex items-center gap-2 font-mono text-caption uppercase">
          <MessageSquare class="h-4 w-4 text-amber-600" />
          Pistes d'amélioration
        </h3>
        <div class="space-y-2">
          <div v-for="(pa, idx) in analysisResult.points_amelioration" :key="idx" class="rounded-lg border border-amber-500/20 bg-amber-500/5 p-3 text-sm text-amber-800">
            {{ pa }}
          </div>
        </div>
      </div>

      <div class="panel-dark">
        <div class="panel-dark-inner">
          <div class="panel-dark-header">Détail des réponses</div>
          <div class="space-y-0 p-4 sm:p-6">
            <div v-for="(ans, idx) in interviewData.answers" :key="idx" class="border-b border-white/5 py-4 last:border-0">
              <div class="mb-2 font-mono text-micro uppercase text-paper/40">
                Question {{ idx + 1 }} · {{ ans.category }}
              </div>
              <p class="mb-3 text-sm font-medium text-paper/90">{{ ans.question }}</p>
              <div class="rounded-lg border border-white/10 p-3 text-xs text-paper/60">
                {{ ans.answer || 'Aucune réponse rédigée.' }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="flex flex-col items-center justify-center gap-3 sm:flex-row">
        <Button variant="outline" @click="goToDashboard">
          <ArrowLeft class="mr-2 h-4 w-4" />
          Tableau de bord
        </Button>
        <Button @click="startNewInterview">
          <RotateCcw class="mr-2 h-4 w-4" />
          Nouvelle simulation
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppPageHeader from '@/components/AppPageHeader.vue'
import { Button } from '@/components/ui/button'
import { getInterview } from '@/lib/api'
import { ArrowLeft, RotateCcw, CheckCircle, MessageSquare, AlertCircle, Loader2 } from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()

const isLoading = ref(true)
const error = ref('')
const interviewData = ref<any>(null)
const analysisResult = ref<any>(null)

const formatTime = (seconds: number) => {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${m}:${s.toString().padStart(2, '0')}`
}

const getScoreMessage = (score: number | undefined) => {
  if (!score) return 'Non évalué'
  if (score >= 8) return 'Excellente maîtrise'
  if (score >= 6) return 'Bonne prestation'
  return 'À travailler'
}

function applySession(payload: {
  questions: any[]
  answers: any[]
  analysis: any
  duration: number
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
      })
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
      })
      localStorage.removeItem('interviewAnalysis')
      return
    }

    error.value = 'Aucune session récente trouvée.'
  } catch (err: any) {
    error.value = err.response?.data?.detail || err.message || 'Erreur lors du chargement'
  } finally {
    isLoading.value = false
  }
}

const goToDashboard = () => router.push('/dashboard')
const startNewInterview = () => router.push('/interview-simulator')

onMounted(() => {
  loadInterviewData()
})
</script>
