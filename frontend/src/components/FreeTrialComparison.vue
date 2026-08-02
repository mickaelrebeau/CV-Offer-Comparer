<template>
  <div class="space-y-10">
    <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
      <div class="panel overflow-hidden">
        <div class="panel-header justify-between">
          <span>01 · Offre d'emploi</span>
          <FileText class="h-3.5 w-3.5" />
        </div>
        <div class="p-4 sm:p-5">
          <Textarea v-model="offerText" placeholder="Collez la description complète de l'offre..." class="min-h-[220px]" />
        </div>
      </div>

      <div class="panel overflow-hidden">
        <div class="panel-header justify-between">
          <span>02 · Mon CV</span>
          <div class="flex gap-1">
            <button
              @click="activeTab = 'upload'"
              class="rounded px-2 py-0.5 transition-colors"
              :class="activeTab === 'upload' ? 'bg-ink text-paper' : 'text-ink-soft hover:text-ink'"
            >
              PDF
            </button>
            <button
              @click="activeTab = 'manual'"
              class="rounded px-2 py-0.5 transition-colors"
              :class="activeTab === 'manual' ? 'bg-ink text-paper' : 'text-ink-soft hover:text-ink'"
            >
              Texte
            </button>
          </div>
        </div>
        <div class="p-4 sm:p-5">
          <FreeTrialPDFUpload v-if="activeTab === 'upload'" :model-value="cvText" @update:model-value="(v) => { cvText = v }" />
          <Textarea v-else v-model="cvText" placeholder="Collez le texte de votre CV..." class="min-h-[220px]" />
        </div>
      </div>
    </div>

    <div class="mx-auto flex max-w-xl flex-col items-center gap-4">
      <div v-if="loading" class="w-full space-y-2">
        <div class="flex items-center justify-between font-mono text-micro uppercase text-ink-soft">
          <span>{{ status }}</span>
          <span>{{ Math.round(progress) }}%</span>
        </div>
        <div class="progress-track">
          <div class="progress-fill" :style="{ width: progress + '%' }"></div>
        </div>
      </div>

      <Button :disabled="!hasData || loading || !canAnalyze" size="lg" @click="compareCVWithOffer">
        <Loader2 v-if="loading" class="mr-2 h-4 w-4 animate-spin" />
        <ArrowRightLeft v-else class="mr-2 h-4 w-4" />
        {{ canAnalyze ? 'Lancer le diagnostic gratuit' : 'Essai gratuit déjà utilisé' }}
      </Button>
    </div>

    <div v-if="error" class="rounded-lg border border-rose-500/25 bg-rose-500/5 p-4 font-mono text-micro text-rose-700">
      {{ error }}
    </div>

    <div v-if="comparisonResult" class="space-y-8">
      <div class="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <div class="panel p-5 text-center">
          <div class="mb-1 font-mono text-micro uppercase text-ink-soft">Correspondances</div>
          <div class="text-3xl font-medium tabular-nums text-emerald-600">{{ comparisonResult.summary.matches }}</div>
        </div>
        <div class="panel p-5 text-center">
          <div class="mb-1 font-mono text-micro uppercase text-ink-soft">Manquants</div>
          <div class="text-3xl font-medium tabular-nums text-rose-600">{{ comparisonResult.summary.missing }}</div>
        </div>
        <div class="panel p-5 text-center">
          <div class="mb-1 font-mono text-micro uppercase text-ink-soft">À préciser</div>
          <div class="text-3xl font-medium tabular-nums text-amber-600">{{ comparisonResult.summary.unclear }}</div>
        </div>
        <div class="panel p-5 text-center">
          <div class="mb-1 font-mono text-micro uppercase text-ink-soft">Score ATS</div>
          <div class="text-3xl font-medium tabular-nums">{{ formatPercentage(comparisonResult.summary.matchPercentage) }}</div>
        </div>
      </div>

      <div class="panel-dark">
        <div class="panel-dark-inner">
          <div class="panel-dark-header">Rapport détaillé</div>
          <div class="space-y-0 p-4 sm:p-6">
            <div
              v-for="item in comparisonResult.items"
              :key="item.id"
              class="border-b border-white/5 py-4 last:border-0"
            >
              <div class="flex items-start justify-between gap-4">
                <div class="flex-1 space-y-2">
                  <div class="font-mono text-micro uppercase text-paper/40">{{ item.category }}</div>
                  <p class="text-sm text-paper/90">{{ item.offerText }}</p>
                  <p v-if="item.cvText" class="text-xs text-paper/50">
                    <span class="text-paper/70">Extrait CV :</span> {{ item.cvText }}
                  </p>
                  <div v-if="item.suggestions?.length" class="mt-3 space-y-1.5 border-t border-white/10 pt-3">
                    <div class="font-mono text-micro uppercase text-paper/40">Reformulations</div>
                    <ul class="space-y-1.5 text-xs text-paper/70">
                      <li v-for="sug in item.suggestions" :key="sug" class="flex items-start justify-between gap-3">
                        <span>{{ sug }}</span>
                        <button @click="copyToClipboard(sug)" class="shrink-0 font-mono text-micro uppercase text-paper/40 hover:text-paper">Copier</button>
                      </li>
                    </ul>
                  </div>
                </div>
                <div class="shrink-0 font-mono text-micro uppercase" :class="statusTone(item.status)">
                  {{ statusLabel(item.status) }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="panel p-8 text-center">
        <h3 class="mb-2 font-medium text-title">Passez à la vitesse supérieure</h3>
        <p class="mx-auto mb-6 max-w-md text-lead text-ink-soft">
          Créez un compte gratuit pour enregistrer vos analyses, accéder aux comparaisons illimitées et lancer le simulateur d'entretien.
        </p>
        <div class="flex flex-col items-center justify-center gap-3 sm:flex-row">
          <Button @click="goToRegister">Créer un compte</Button>
          <Button variant="outline" @click="goToLogin">Connexion</Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { FileText, ArrowRightLeft, Loader2 } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { streamFreeCompare, checkFreeAnalysisStatus } from '@/lib/api'
import FreeTrialPDFUpload from './FreeTrialPDFUpload.vue'
import posthog from 'posthog-js'

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

const statusTone = (st: string) => {
  if (st === 'match') return 'text-emerald-400'
  if (st === 'missing') return 'text-rose-400'
  return 'text-amber-400'
}

const statusLabel = (st: string) => {
  if (st === 'match') return 'couvert'
  if (st === 'missing') return 'manquant'
  return 'partiel'
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
        posthog.capture('free_trial_comparison_completed', { comparison_mode: 'free_trial' })
      },
      (eMsg: string) => {
        loading.value = false
        error.value = eMsg
      },
    )
  } catch (err: any) {
    loading.value = false
    error.value = err.message || 'Erreur lors de la comparaison'
  }
}
</script>
