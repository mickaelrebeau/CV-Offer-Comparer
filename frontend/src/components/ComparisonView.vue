<template>
  <div class="space-y-10">
    <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
      <!-- Offre -->
      <div class="panel overflow-hidden">
        <div class="panel-header justify-between">
          <span>01 · Offre d'emploi</span>
          <FileText class="h-3.5 w-3.5" />
        </div>
        <div class="p-4 sm:p-5">
          <Textarea
            :model-value="compareStore.offerText"
            placeholder="Collez l'offre d'emploi ici..."
            class="min-h-[220px]"
            @input="handleOfferInput"
          />
        </div>
      </div>

      <!-- CV -->
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
          <PDFUpload v-if="activeTab === 'upload'" :model-value="compareStore.cvText" @update:model-value="(val) => compareStore.updateCVText(val)" />
          <Textarea
            v-else
            :model-value="compareStore.cvText"
            placeholder="Collez le texte de votre CV ici..."
            class="min-h-[220px]"
            @input="handleCVInput"
          />
        </div>
      </div>
    </div>

    <div class="mx-auto flex max-w-xl flex-col items-center gap-4">
      <div v-if="compareStore.loading" class="w-full space-y-2">
        <div class="flex items-center justify-between font-mono text-micro uppercase text-ink-soft">
          <span>{{ compareStore.status }}</span>
          <span>{{ Math.round(compareStore.progress) }}%</span>
        </div>
        <div class="progress-track">
          <div class="progress-fill" :style="{ width: compareStore.progress + '%' }"></div>
        </div>
      </div>

      <Button
        :disabled="!compareStore.hasData || compareStore.loading"
        size="lg"
        @click="compareStore.compareCVWithOfferStream"
      >
        <Loader2 v-if="compareStore.loading" class="mr-2 h-4 w-4 animate-spin" />
        <ArrowRightLeft v-else class="mr-2 h-4 w-4" />
        Lancer la comparaison
      </Button>
    </div>

    <div v-if="compareStore.error" class="rounded-lg border border-rose-500/25 bg-rose-500/5 p-4 font-mono text-micro text-rose-700">
      {{ compareStore.error }}
    </div>

    <div v-if="compareStore.comparisonResult" class="space-y-8">
      <div class="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <div v-for="stat in summaryStats" :key="stat.label" class="panel p-5 text-center">
          <div class="mb-1 font-mono text-micro uppercase text-ink-soft">{{ stat.label }}</div>
          <div class="text-3xl font-medium tabular-nums" :class="stat.color">{{ stat.value }}</div>
        </div>
      </div>

      <div class="panel-dark">
        <div class="panel-dark-inner">
          <div class="panel-dark-header">Rapport détaillé par critère</div>
          <div class="space-y-0 p-4 sm:p-6">
            <div
              v-for="item in compareStore.comparisonResult.items"
              :key="item.id"
              class="border-b border-white/5 py-4 last:border-0"
            >
              <div class="flex items-start justify-between gap-4">
                <div class="flex-1 space-y-2">
                  <div class="flex flex-wrap items-center gap-3 font-mono text-micro uppercase">
                    <span class="text-paper/40">{{ item.category }}</span>
                    <span class="text-paper/30">conf. {{ Math.round(item.confidence * 100) }}%</span>
                  </div>
                  <p class="text-sm text-paper/90">{{ item.offerText }}</p>
                  <p v-if="item.cvText" class="text-xs text-paper/50">
                    <span class="text-paper/70">Extrait CV :</span> {{ item.cvText }}
                  </p>
                  <div v-if="item.suggestions?.length" class="mt-3 space-y-1.5 border-t border-white/10 pt-3">
                    <div class="font-mono text-micro uppercase text-paper/40">Reformulations</div>
                    <ul class="space-y-1.5 text-xs text-paper/70">
                      <li v-for="sug in item.suggestions" :key="sug" class="flex items-start justify-between gap-3">
                        <span>{{ sug }}</span>
                        <button
                          @click="copyToClipboard(sug)"
                          class="shrink-0 font-mono text-micro uppercase text-paper/40 hover:text-paper"
                        >
                          Copier
                        </button>
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
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { FileText, ArrowRightLeft, Loader2 } from 'lucide-vue-next'
import { useCompareStore } from '@/stores/compare'
import { formatPercentage } from '@/lib/utils'
import PDFUpload from './PDFUpload.vue'

const compareStore = useCompareStore()
const activeTab = ref<'upload' | 'manual'>('upload')

const summaryStats = computed(() => {
  const s = compareStore.comparisonResult?.summary
  if (!s) return []
  return [
    { label: 'Correspondances', value: s.matches, color: 'text-emerald-500' },
    { label: 'Manquants', value: s.missing, color: 'text-rose-500' },
    { label: 'À préciser', value: s.unclear, color: 'text-amber-500' },
    { label: 'Score ATS', value: formatPercentage(s.matchPercentage), color: 'text-ink' },
  ]
})

const handleOfferInput = (event: Event) => {
  compareStore.updateOfferText((event.target as HTMLTextAreaElement).value)
}

const handleCVInput = (event: Event) => {
  compareStore.updateCVText((event.target as HTMLTextAreaElement).value)
}

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
</script>
