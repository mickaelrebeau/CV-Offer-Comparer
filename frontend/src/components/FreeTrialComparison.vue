<template>
  <div class="space-y-10">
    <!-- Input Workspace (Dual Pane) -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <!-- Job Offer Pane -->
      <Card class="glass-card rounded-2xl overflow-hidden border border-border">
        <CardHeader class="border-b border-border bg-zinc-50/50 dark:bg-zinc-900/50">
          <CardTitle class="text-base font-bold flex items-center gap-2">
            <div class="p-1.5 rounded-lg bg-indigo-500/10 text-indigo-500">
              <FileText class="h-4 w-4" />
            </div>
            <span>Offre d'emploi</span>
          </CardTitle>
          <CardDescription class="text-xs">
            Collez la description complète de l'offre ou fiche de poste.
          </CardDescription>
        </CardHeader>
        <CardContent class="p-6">
          <Textarea v-model="offerText" placeholder="Exemple : Nous recherchons un Développeur Senior Fullstack maîtrisant Vue 3, TypeScript, Docker..." class="min-h-[220px]" />
        </CardContent>
      </Card>

      <!-- CV Input Pane -->
      <Card class="glass-card rounded-2xl overflow-hidden border border-border">
        <CardHeader class="border-b border-border bg-zinc-50/50 dark:bg-zinc-900/50">
          <CardTitle class="text-base font-bold flex items-center justify-between">
            <div class="flex items-center gap-2">
              <div class="p-1.5 rounded-lg bg-purple-500/10 text-purple-500">
                <User class="h-4 w-4" />
              </div>
              <span>Mon CV</span>
            </div>
            <div class="flex items-center gap-1 bg-zinc-200/60 dark:bg-zinc-800/80 p-1 rounded-lg">
              <button @click="activeTab = 'upload'" class="px-3 py-1 text-xs font-semibold rounded-md transition-all flex items-center gap-1.5" :class="activeTab === 'upload' ? 'bg-background text-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'">
                <Upload class="h-3.5 w-3.5" />
                <span>PDF</span>
              </button>
              <button @click="activeTab = 'manual'" class="px-3 py-1 text-xs font-semibold rounded-md transition-all flex items-center gap-1.5" :class="activeTab === 'manual' ? 'bg-background text-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'">
                <Edit class="h-3.5 w-3.5" />
                <span>Texte</span>
              </button>
            </div>
          </CardTitle>
          <CardDescription class="text-xs">
            Uploadez votre CV en PDF ou saisissez votre texte directement.
          </CardDescription>
        </CardHeader>
        <CardContent class="p-6">
          <div v-if="activeTab === 'upload'">
            <FreeTrialPDFUpload :model-value="cvText" @update:model-value="(value) => { cvText = value; }" />
          </div>
          <div v-else class="space-y-2">
            <Textarea v-model="cvText" placeholder="Collez le texte de votre CV ici..." class="min-h-[220px]" />
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- Action Bar & Progress Bar -->
    <div class="flex flex-col items-center justify-center space-y-4 max-w-xl mx-auto text-center">
      <div v-if="loading" class="w-full space-y-2">
        <div class="flex items-center justify-between text-xs font-mono text-muted-foreground">
          <span>{{ status }}</span>
          <span>{{ Math.round(progress) }}%</span>
        </div>
        <div class="w-full bg-zinc-200 dark:bg-zinc-800 rounded-full h-2 overflow-hidden">
          <div class="bg-indigo-500 h-full rounded-full transition-all duration-300" :style="{ width: progress + '%' }"></div>
        </div>
      </div>

      <Button :disabled="!hasData || loading || !canAnalyze" @click="compareCVWithOffer" size="lg" class="w-full sm:w-auto px-10 py-3.5 rounded-full font-semibold shadow-glow">
        <Loader2 v-if="loading" class="mr-2 h-4 w-4 animate-spin" />
        <ArrowRightLeft v-else class="mr-2 h-4 w-4" />
        <span>{{ canAnalyze ? 'Lancer le diagnostic gratuit' : 'Essai gratuit déjà utilisé' }}</span>
      </Button>
    </div>

    <!-- Error Banner -->
    <div v-if="error" class="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-600 dark:text-rose-400 text-sm">
      {{ error }}
    </div>

    <!-- Results Section -->
    <div v-if="comparisonResult" class="space-y-8 animate-in fade-in duration-500">
      <!-- Summary Dashboard -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-6">
        <Card class="glass-card p-6 rounded-2xl text-center space-y-1">
          <div class="text-3xl font-extrabold text-emerald-500">{{ comparisonResult.summary.matches }}</div>
          <div class="text-xs uppercase tracking-wider font-semibold text-muted-foreground">Correspondances</div>
        </Card>
        <Card class="glass-card p-6 rounded-2xl text-center space-y-1">
          <div class="text-3xl font-extrabold text-rose-500">{{ comparisonResult.summary.missing }}</div>
          <div class="text-xs uppercase tracking-wider font-semibold text-muted-foreground">Manquants</div>
        </Card>
        <Card class="glass-card p-6 rounded-2xl text-center space-y-1">
          <div class="text-3xl font-extrabold text-amber-500">{{ comparisonResult.summary.unclear }}</div>
          <div class="text-xs uppercase tracking-wider font-semibold text-muted-foreground">Confus / À préciser</div>
        </Card>
        <Card class="glass-card p-6 rounded-2xl text-center space-y-1 border-brand-500/30">
          <div class="text-3xl font-extrabold text-brand-500">{{ formatPercentage(comparisonResult.summary.matchPercentage) }}</div>
          <div class="text-xs uppercase tracking-wider font-semibold text-muted-foreground">Score Global ATS</div>
        </Card>
      </div>

      <!-- Detail Analysis Items -->
      <Card class="glass-card rounded-2xl overflow-hidden border border-border">
        <CardHeader class="border-b border-border bg-zinc-50/50 dark:bg-zinc-900/50">
          <CardTitle class="text-base font-bold">Rapport d'Analyse Détaillé par Point Fort / Point Faible</CardTitle>
        </CardHeader>
        <CardContent class="p-6 space-y-4">
          <div v-for="item in comparisonResult.items" :key="item.id" class="p-4 rounded-xl border transition-all" :class="getStatusColorClass(item.status)">
            <div class="flex items-start justify-between gap-4">
              <div class="space-y-2 flex-1">
                <div class="flex items-center gap-2">
                  <span class="text-xs font-semibold uppercase tracking-wider font-mono text-foreground px-2 py-0.5 rounded bg-zinc-200/50 dark:bg-zinc-800/50">
                    {{ item.category }}
                  </span>
                </div>
                <p class="text-sm font-semibold text-foreground">{{ item.offerText }}</p>
                
                <p v-if="item.cvText" class="text-xs text-muted-foreground">
                  <span class="font-bold text-foreground">Extrait CV :</span> {{ item.cvText }}
                </p>

                <div v-if="item.suggestions && item.suggestions.length > 0" class="mt-3 pt-3 border-t border-border/50 space-y-1.5">
                  <span class="text-xs font-semibold text-indigo-500">Suggestions de reformulation :</span>
                  <ul class="text-xs text-muted-foreground space-y-1">
                    <li v-for="sug in item.suggestions" :key="sug" class="flex items-center justify-between gap-2">
                      <span>• {{ sug }}</span>
                      <button @click="copyToClipboard(sug)" class="text-[10px] font-semibold px-2 py-0.5 rounded bg-zinc-200 dark:bg-zinc-800 text-foreground hover:bg-zinc-300 dark:hover:bg-zinc-700 transition-colors">
                        Copier
                      </button>
                    </li>
                  </ul>
                </div>
              </div>

              <div class="shrink-0">
                <CheckCircle v-if="item.status === 'match'" class="h-5 w-5 text-emerald-500" />
                <XCircle v-else-if="item.status === 'missing'" class="h-5 w-5 text-rose-500" />
                <AlertCircle v-else class="h-5 w-5 text-amber-500" />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- Conversion Banner -->
      <Card class="glass-card rounded-2xl p-8 text-center border-brand-500/30 bg-gradient-to-b from-brand-500/5 to-transparent">
        <h3 class="text-xl font-bold tracking-tight text-foreground mb-2">Passez à la vitesse supérieure</h3>
        <p class="text-sm text-muted-foreground mb-6 max-w-md mx-auto">
          Créez un compte gratuit pour enregistrer vos analyses, accéder aux comparaisons illimitées et lancer le simulateur d'entretien.
        </p>
        <div class="flex items-center justify-center gap-4">
          <Button @click="goToRegister" class="rounded-full px-6 shadow-glow">
            Créer un compte
          </Button>
          <Button @click="goToLogin" variant="outline" class="rounded-full px-6">
            Connexion
          </Button>
        </div>
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
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { streamFreeCompare, checkFreeAnalysisStatus } from '@/lib/api'
import FreeTrialPDFUpload from './FreeTrialPDFUpload.vue'

const router = useRouter()

const offerText = ref('')
const cvText = ref('')
const loading = ref(false)
const status = ref('')
const progress = ref(0)
const error = ref('')
const comparisonResult = ref<any>(null)
const canAnalyze = ref(true)
const activeTab = ref('upload')

const hasData = computed(() => offerText.value.trim() && cvText.value.trim())

onMounted(async () => {
  try {
    const statusData = await checkFreeAnalysisStatus()
    canAnalyze.value = statusData.can_use_free_analysis
  } catch (err) {
    console.error('Erreur de statut:', err)
  }
})

const formatPercentage = (val: number) => `${Math.round(val * 100)}%`

const getStatusColorClass = (st: string) => {
  switch (st) {
    case 'match':
      return 'border-emerald-500/30 bg-emerald-500/5'
    case 'missing':
      return 'border-rose-500/30 bg-rose-500/5'
    case 'unclear':
      return 'border-amber-500/30 bg-amber-500/5'
    default:
      return 'border-border bg-card'
  }
}

const copyToClipboard = (text: string) => {
  navigator.clipboard.writeText(text)
}

const goToRegister = () => router.push('/register')
const goToLogin = () => router.push('/login')

const compareCVWithOffer = async () => {
  if (!hasData.value || loading.value || !canAnalyze.value) return

  loading.value = true
  error.value = ''
  status.value = 'Diagnostic en cours...'
  progress.value = 0
  comparisonResult.value = null

  try {
    const items: any[] = []
    let summary: any = null

    await streamFreeCompare(
      offerText.value,
      cvText.value,
      (m: string) => { status.value = m },
      (p: number) => { progress.value = p },
      (item: any) => { items.push(item) },
      (sData: any) => { summary = sData },
      () => {
        loading.value = false
        comparisonResult.value = { items, summary }
        canAnalyze.value = false
      },
      (eMsg: string) => {
        loading.value = false
        error.value = eMsg
      }
    )
  } catch (err: any) {
    loading.value = false
    error.value = err.message || 'Erreur lors de la comparaison'
  }
}
</script>
