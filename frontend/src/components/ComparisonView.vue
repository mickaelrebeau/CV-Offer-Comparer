<template>
  <div class="space-y-10">
    <!-- Dual Pane Input Workspace -->
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
            Collez la description de l'offre d'emploi.
          </CardDescription>
        </CardHeader>
        <CardContent class="p-6">
          <Textarea :model-value="compareStore.offerText" placeholder="Collez l'offre d'emploi ici..." class="min-h-[220px]" @input="handleOfferInput" />
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
            Uploadez votre CV en PDF ou saisissez votre texte.
          </CardDescription>
        </CardHeader>
        <CardContent class="p-6">
          <div v-if="activeTab === 'upload'">
            <PDFUpload :model-value="compareStore.cvText" @update:model-value="(val) => compareStore.updateCVText(val)" />
          </div>
          <div v-else>
            <Textarea :model-value="compareStore.cvText" placeholder="Collez le texte de votre CV ici..." class="min-h-[220px]" @input="handleCVInput" />
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- Action Bar & Progress Bar -->
    <div class="flex flex-col items-center justify-center space-y-4 max-w-xl mx-auto text-center">
      <div v-if="compareStore.loading" class="w-full space-y-2">
        <div class="flex items-center justify-between text-xs font-mono text-muted-foreground">
          <span>{{ compareStore.status }}</span>
          <span>{{ Math.round(compareStore.progress) }}%</span>
        </div>
        <div class="w-full bg-zinc-200 dark:bg-zinc-800 rounded-full h-2 overflow-hidden">
          <div class="bg-indigo-500 h-full rounded-full transition-all duration-300" :style="{ width: compareStore.progress + '%' }"></div>
        </div>
      </div>

      <Button :disabled="!compareStore.hasData || compareStore.loading" @click="compareStore.compareCVWithOfferStream" size="lg" class="w-full sm:w-auto px-10 py-3.5 rounded-full font-semibold shadow-glow">
        <Loader2 v-if="compareStore.loading" class="mr-2 h-4 w-4 animate-spin" />
        <ArrowRightLeft v-else class="mr-2 h-4 w-4" />
        <span>Lancer la comparaison</span>
      </Button>
    </div>

    <!-- Error Display -->
    <div v-if="compareStore.error" class="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-600 dark:text-rose-400 text-sm">
      {{ compareStore.error }}
    </div>

    <!-- Detailed Results -->
    <div v-if="compareStore.comparisonResult" class="space-y-8 animate-in fade-in duration-500">
      <!-- Summary Dashboard -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-6">
        <Card class="glass-card p-6 rounded-2xl text-center space-y-1">
          <div class="text-3xl font-extrabold text-emerald-500">{{ compareStore.comparisonResult.summary.matches }}</div>
          <div class="text-xs uppercase tracking-wider font-semibold text-muted-foreground">Correspondances</div>
        </Card>
        <Card class="glass-card p-6 rounded-2xl text-center space-y-1">
          <div class="text-3xl font-extrabold text-rose-500">{{ compareStore.comparisonResult.summary.missing }}</div>
          <div class="text-xs uppercase tracking-wider font-semibold text-muted-foreground">Manquants</div>
        </Card>
        <Card class="glass-card p-6 rounded-2xl text-center space-y-1">
          <div class="text-3xl font-extrabold text-amber-500">{{ compareStore.comparisonResult.summary.unclear }}</div>
          <div class="text-xs uppercase tracking-wider font-semibold text-muted-foreground">Confus / À préciser</div>
        </Card>
        <Card class="glass-card p-6 rounded-2xl text-center space-y-1 border-brand-500/30">
          <div class="text-3xl font-extrabold text-brand-500">{{ formatPercentage(compareStore.comparisonResult.summary.matchPercentage) }}</div>
          <div class="text-xs uppercase tracking-wider font-semibold text-muted-foreground">Score Global ATS</div>
        </Card>
      </div>

      <!-- Detail Analysis Items -->
      <Card class="glass-card rounded-2xl overflow-hidden border border-border">
        <CardHeader class="border-b border-border bg-zinc-50/50 dark:bg-zinc-900/50">
          <CardTitle class="text-base font-bold">Rapport d'Analyse Détaillé par Critère</CardTitle>
        </CardHeader>
        <CardContent class="p-6 space-y-4">
          <div v-for="item in compareStore.comparisonResult.items" :key="item.id" class="p-4 rounded-xl border transition-all" :class="getStatusColorClass(item.status)">
            <div class="flex items-start justify-between gap-4">
              <div class="space-y-2 flex-1">
                <div class="flex items-center gap-2">
                  <span class="text-xs font-semibold uppercase tracking-wider font-mono text-foreground px-2 py-0.5 rounded bg-zinc-200/50 dark:bg-zinc-800/50">
                    {{ item.category }}
                  </span>
                  <span class="text-xs font-mono text-muted-foreground">
                    Confiance : {{ Math.round(item.confidence * 100) }}%
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
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { FileText, User, ArrowRightLeft, Loader2, CheckCircle, XCircle, AlertCircle, Upload, Edit } from 'lucide-vue-next'
import { useCompareStore } from '@/stores/compare'
import { formatPercentage } from '@/lib/utils'
import PDFUpload from './PDFUpload.vue'

const compareStore = useCompareStore()
const activeTab = ref<'upload' | 'manual'>('upload')

const handleOfferInput = (event: Event) => {
  const target = event.target as HTMLTextAreaElement
  compareStore.updateOfferText(target.value)
}

const handleCVInput = (event: Event) => {
  const target = event.target as HTMLTextAreaElement
  compareStore.updateCVText(target.value)
}

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
</script>
