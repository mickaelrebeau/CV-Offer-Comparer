<template>
  <div class="max-w-4xl mx-auto px-6 py-10 sm:py-16 space-y-8">
    <!-- Header -->
    <div class="text-center space-y-3">
      <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 text-xs font-semibold tracking-wider uppercase">
        <span>RAPPORT D'ENTRETIEN</span>
      </div>
      <h1 class="text-3xl sm:text-4xl font-extrabold tracking-tight text-foreground">
        Résultats de votre Simulation
      </h1>
      <p class="text-base text-muted-foreground max-w-xl mx-auto">
        Découvrez l'évaluation synthétique et les recommandations pour perfectionner vos arguments.
      </p>
    </div>

    <!-- Loading state -->
    <div v-if="isLoading" class="text-center py-16 space-y-4">
      <Loader2 class="h-10 w-10 animate-spin text-brand-500 mx-auto" />
      <p class="text-sm font-semibold text-foreground">Récupération des résultats de l'entretien...</p>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="text-center py-16 space-y-6">
      <AlertCircle class="h-12 w-12 text-rose-500 mx-auto" />
      <div class="space-y-2">
        <h3 class="text-lg font-bold text-foreground">Aucun résultat récent trouvé</h3>
        <p class="text-sm text-muted-foreground max-w-md mx-auto">{{ error }}</p>
      </div>
      <div class="flex justify-center gap-4">
        <Button @click="startNewInterview" class="rounded-full shadow-glow">
          <MessageSquare class="h-4 w-4 mr-2" />
          Nouveau Simulateur
        </Button>
      </div>
    </div>

    <!-- Results Report -->
    <div v-else-if="interviewData" class="space-y-8 animate-in fade-in duration-500">
      <!-- Global Score & Stats Header -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card class="glass-card p-6 rounded-2xl text-center space-y-1 md:col-span-2 border-brand-500/30">
          <div class="text-xs uppercase tracking-wider font-semibold text-muted-foreground">Score Global de Simulation</div>
          <div class="text-4xl font-extrabold text-brand-500 py-1">{{ analysisResult?.score_global || 'N/A' }}/10</div>
          <p class="text-xs font-medium text-emerald-500">{{ getScoreMessage(analysisResult?.score_global) }}</p>
        </Card>

        <Card class="glass-card p-6 rounded-2xl text-center space-y-1">
          <div class="text-xs uppercase tracking-wider font-semibold text-muted-foreground">Questions</div>
          <div class="text-3xl font-extrabold text-foreground py-1">{{ interviewData.num_questions }}</div>
          <p class="text-xs text-muted-foreground">Complétées</p>
        </Card>

        <Card class="glass-card p-6 rounded-2xl text-center space-y-1">
          <div class="text-xs uppercase tracking-wider font-semibold text-muted-foreground">Durée Totale</div>
          <div class="text-3xl font-extrabold text-foreground py-1">{{ formatTime(interviewData.duration) }}</div>
          <p class="text-xs text-muted-foreground">Minutes</p>
        </Card>
      </div>

      <!-- Points Forts -->
      <Card class="glass-card rounded-2xl p-6 border border-emerald-500/30 space-y-4">
        <h3 class="text-base font-bold text-foreground flex items-center gap-2">
          <CheckCircle class="h-5 w-5 text-emerald-500 shrink-0" />
          <span>Points Forts Validés</span>
        </h3>
        <div v-if="analysisResult?.points_forts?.length" class="space-y-2">
          <div v-for="(pf, idx) in analysisResult.points_forts" :key="idx" class="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-700 dark:text-emerald-300 font-medium">
            ✓ {{ pf }}
          </div>
        </div>
      </Card>

      <!-- Points d'Amélioration -->
      <Card v-if="analysisResult?.points_amelioration?.length" class="glass-card rounded-2xl p-6 border border-amber-500/30 space-y-4">
        <h3 class="text-base font-bold text-foreground flex items-center gap-2">
          <MessageSquare class="h-5 w-5 text-amber-500 shrink-0" />
          <span>Pistes d'Amélioration</span>
        </h3>
        <div class="space-y-2">
          <div v-for="(pa, idx) in analysisResult.points_amelioration" :key="idx" class="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs text-amber-700 dark:text-amber-300 font-medium">
            • {{ pa }}
          </div>
        </div>
      </Card>

      <!-- Details per question -->
      <Card class="glass-card rounded-2xl p-6 border border-border space-y-6">
        <h3 class="text-base font-bold text-foreground">Détail des Réponses & Questions</h3>
        <div class="space-y-4">
          <div v-for="(ans, idx) in interviewData.answers" :key="idx" class="p-4 rounded-xl bg-card border border-border space-y-2">
            <div class="flex items-center justify-between text-xs">
              <span class="font-mono font-bold text-purple-500">Question {{ idx + 1 }} • {{ ans.category }}</span>
            </div>
            <p class="text-sm font-semibold text-foreground">{{ ans.question }}</p>
            <div class="p-3 rounded-lg bg-zinc-100/50 dark:bg-zinc-900/50 border border-border text-xs text-muted-foreground">
              {{ ans.answer || 'Aucune réponse rédigée.' }}
            </div>
          </div>
        </div>
      </Card>

      <!-- Actions -->
      <div class="flex justify-center gap-4 pt-4">
        <Button variant="outline" @click="goToDashboard" class="rounded-full">
          <ArrowLeft class="h-4 w-4 mr-2" />
          Tableau de bord
        </Button>
        <Button @click="startNewInterview" class="rounded-full shadow-glow">
          <RotateCcw class="h-4 w-4 mr-2" />
          Nouvelle Simulation
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import {
  ArrowLeft, RotateCcw, CheckCircle, MessageSquare, AlertCircle, Loader2
} from 'lucide-vue-next'

const router = useRouter()

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

const loadInterviewData = async () => {
  isLoading.value = true
  error.value = ''

  try {
    const storedAnalysis = localStorage.getItem('interviewAnalysis')

    if (storedAnalysis) {
      const analysisData = JSON.parse(storedAnalysis)

      interviewData.value = {
        id: 'analysis-session',
        num_questions: analysisData.questions.length,
        duration: analysisData.duration,
        answers: analysisData.answers.map((answer: any) => ({
          question: answer.question,
          answer: answer.answer,
          category: answer.category,
          time: answer.time || 0
        }))
      }

      analysisResult.value = analysisData.analysis
      localStorage.removeItem('interviewAnalysis')
      return
    }

    error.value = 'Aucune session récente trouvée.'
  } catch (err: any) {
    error.value = err.message || 'Erreur lors du chargement'
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
