<template>
  <div class="space-y-6">
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
            Collez le texte de l'offre d'emploi ici
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Textarea v-model="offerText" placeholder="Collez le texte de l'offre d'emploi..."
            class="min-h-[300px] w-full border-2 border-gray-300 rounded-md p-2" />
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
          <div class="flex space-x-1 mb-4">
            <Button variant="outline" size="sm"
              :class="activeTab === 'upload' ? 'bg-primary text-primary-foreground p-2 flex items-center justify-center rounded-md' : 'p-2 flex items-center justify-center rounded-md'"
              @click="activeTab = 'upload'">
              <Upload class="h-4 w-4 mr-2" />
              Upload PDF
            </Button>
            <Button variant="outline" size="sm"
              :class="activeTab === 'manual' ? 'bg-primary text-primary-foreground p-2 flex items-center justify-center rounded-md' : 'p-2 flex items-center justify-center'"
              @click="activeTab = 'manual'">
              <Edit class="h-4 w-4 mr-2" />
              Saisie manuelle
            </Button>
          </div>

          <!-- Contenu des onglets -->
          <div v-if="activeTab === 'upload'">
            <FreeTrialPDFUpload :model-value="cvText"
              @update:model-value="(value) => { console.log('FreeTrialPDFUpload event:', value.length); cvText = value; }" />
          </div>

          <div v-else-if="activeTab === 'manual'">
            <Textarea v-model="cvText" placeholder="Collez le texte de votre CV..."
              class="min-h-[300px] w-full border-2 border-gray-300 rounded-md p-2" />
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- Bouton de comparaison -->
    <div class="flex justify-center items-center flex-col">
      <!-- Indicateur de progression -->
      <div v-if="loading" class="mb-4 w-full max-w-md">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm text-muted-foreground">{{ status }}</span>
          <span class="text-sm font-medium">{{ Math.round(progress) }}%</span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2">
          <div class="bg-primary h-2 rounded-full transition-all duration-300" :style="{ width: progress + '%' }"></div>
        </div>
      </div>

      <Button :disabled="!hasData || loading || !canAnalyze" @click="compareCVWithOffer"
        class="px-8 py-3 p-2 flex items-center justify-center rounded-md border-2 border-primary disabled:opacity-50">
        <Loader2 v-if="loading" class="mr-2 h-4 w-4 animate-spin" />
        <ArrowRightLeft class="mr-2 h-4 w-4" />
        {{ canAnalyze ? 'Commencer l\'essai gratuit' : 'Essai gratuit utilisé' }}
      </Button>
    </div>

    <!-- Message d'erreur -->
    <div v-if="error" class="bg-destructive/10 border border-destructive text-destructive px-4 py-3 rounded-md">
      {{ error }}
    </div>

    <!-- Résultats de comparaison -->
    <div v-if="comparisonResult" class="space-y-6">
      <!-- Résumé -->
      <Card>
        <CardHeader>
          <CardTitle>Résumé de la comparaison</CardTitle>
        </CardHeader>
        <CardContent>
          <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <div class="text-center">
              <div class="text-2xl font-bold text-match">{{ comparisonResult.summary.matches }}</div>
              <div class="text-sm text-muted-foreground">Correspondances</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-missing">{{ comparisonResult.summary.missing }}</div>
              <div class="text-sm text-muted-foreground">Manquants</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-unclear">{{ comparisonResult.summary.unclear }}</div>
              <div class="text-sm text-muted-foreground">Confus</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-primary">
                {{ formatPercentage(comparisonResult.summary.matchPercentage) }}
              </div>
              <div class="text-sm text-muted-foreground">Score global</div>
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- Graphique de correspondance -->
      <Card>
        <CardHeader>
          <CardTitle>Répartition des compétences</CardTitle>
        </CardHeader>
        <CardContent>
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <span class="text-sm">Correspondances</span>
              <span class="text-sm font-medium text-match">{{ comparisonResult.summary.matches }}</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div class="bg-green-500 h-2 rounded-full transition-all duration-300"
                :style="{ width: getMatchPercentage(comparisonResult.summary.matches) + '%' }"></div>
            </div>

            <div class="flex items-center justify-between">
              <span class="text-sm">Manquants</span>
              <span class="text-sm font-medium text-missing">{{ comparisonResult.summary.missing }}</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div class="bg-red-500 h-2 rounded-full transition-all duration-300"
                :style="{ width: getMatchPercentage(comparisonResult.summary.missing) + '%' }"></div>
            </div>

            <div class="flex items-center justify-between">
              <span class="text-sm">Confus</span>
              <span class="text-sm font-medium text-unclear">{{ comparisonResult.summary.unclear }}</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div class="bg-amber-500 h-2 rounded-full transition-all duration-300"
                :style="{ width: getMatchPercentage(comparisonResult.summary.unclear) + '%' }"></div>
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- Offre d'emploi avec highlights -->
      <Card>
        <CardHeader>
          <CardTitle>Offre d'emploi analysée</CardTitle>
        </CardHeader>
        <CardContent>
          <div class="space-y-3">
            <div v-for="item in comparisonResult.items" :key="item.id" class="p-3 rounded-md border"
              :class="getStatusColor(item.status)">
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <div class="font-medium">{{ item.category }}</div>
                  <div class="text-sm mt-1">{{ item.offerText }}</div>
                  <div v-if="item.cvText" class="text-sm mt-1 text-muted-foreground">
                    <span class="font-bold text-primary">CV:</span> {{ item.cvText }}
                  </div>
                  <div v-if="item.suggestions && item.suggestions.length > 0" class="mt-2">
                    <div class="text-xs font-medium text-muted-foreground mb-1">Suggestions:</div>
                    <ul class="text-xs space-y-1">
                      <li v-for="suggestion in item.suggestions" :key="suggestion" class="text-muted-foreground">
                        • {{ suggestion }}
                      </li>
                    </ul>
                  </div>
                </div>
                <div class="ml-2">
                  <CheckCircle v-if="item.status === 'match'" class="h-4 w-4 text-green-600" />
                  <XCircle v-else-if="item.status === 'missing'" class="h-4 w-4 text-red-600" />
                  <AlertCircle v-else class="h-4 w-4 text-amber-600" />
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- Call to action -->
      <Card class="bg-gradient-to-r from-primary/10 to-primary/5 border-primary/20 rounded-lg">
        <CardContent class="p-6">
          <div class="text-center">
            <h3 class="text-lg font-semibold mb-2">Vous avez aimé l'essai gratuit ?</h3>
            <p class="text-muted-foreground mb-4">
              Créez un compte pour accéder à des analyses illimitées et des fonctionnalités avancées.
            </p>
            <div class="flex justify-center space-x-4">
              <Button @click="goToRegister">
                Créer un compte
              </Button>
              <Button @click="goToLogin" variant="outline">
                Se connecter
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
  FileText, User, ArrowRightLeft, Loader2, CheckCircle, XCircle, AlertCircle, Upload, Edit
} from 'lucide-vue-next'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { streamFreeCompare, checkFreeAnalysisStatus } from '@/lib/api'
import FreeTrialPDFUpload from './FreeTrialPDFUpload.vue'

const router = useRouter()

// État local
const offerText = ref('')
const cvText = ref('')
const loading = ref(false)
const status = ref('')
const progress = ref(0)
const error = ref('')
const comparisonResult = ref<any>(null)
const canAnalyze = ref(true)
const activeTab = ref('upload')

// Computed properties
const hasData = computed(() => offerText.value.trim() && cvText.value.trim())

// Vérifier le statut de l'analyse gratuite au montage
onMounted(async () => {
  try {
    const status = await checkFreeAnalysisStatus()
    canAnalyze.value = status.can_use_free_analysis
  } catch (error) {
    console.error('Erreur lors de la vérification du statut:', error)
  }
})

// Fonctions utilitaires
const formatPercentage = (value: number) => {
  return `${Math.round(value * 100)}%`
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'match':
      return 'border-green-200 bg-green-50'
    case 'missing':
      return 'border-red-200 bg-red-50'
    case 'unclear':
      return 'border-amber-200 bg-amber-50'
    default:
      return 'border-gray-200 bg-gray-50'
  }
}

const getMatchPercentage = (count: number) => {
  const total = comparisonResult.value?.summary?.totalItems || 1
  return (count / total) * 100
}

// Navigation
const goToRegister = () => {
  router.push('/register')
}

const goToLogin = () => {
  router.push('/login')
}

// Fonction de comparaison
const compareCVWithOffer = async () => {
  if (!hasData.value || loading.value || !canAnalyze.value) return

  loading.value = true
  error.value = ''
  status.value = 'Début de l\'analyse...'
  progress.value = 0
  comparisonResult.value = null

  try {
    const items: any[] = []
    let summary: any = null

    await streamFreeCompare(
      offerText.value,
      cvText.value,
      (message: string) => {
        status.value = message
      },
      (progressValue: number, current: number, total: number) => {
        progress.value = progressValue
      },
      (item: any) => {
        items.push(item)
      },
      (summaryData: any) => {
        summary = summaryData
      },
      () => {
        loading.value = false
        comparisonResult.value = { items, summary }
        canAnalyze.value = false // Marquer comme utilisé
      },
      (errorMessage: string) => {
        loading.value = false
        error.value = errorMessage
      }
    )
  } catch (err: any) {
    loading.value = false
    error.value = err.message || 'Une erreur est survenue lors de l\'analyse'
  }
}
</script>

<style scoped>
.text-match {
  color: rgb(34 197 94);
}

.text-missing {
  color: rgb(239 68 68);
}

.text-unclear {
  color: rgb(245 158 11);
}
</style> 