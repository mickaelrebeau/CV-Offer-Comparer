<template>
  <div class="max-w-7xl mx-auto px-6 py-10 sm:py-16 space-y-8">
    <div class="space-y-3">
      <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 text-xs font-semibold tracking-wider uppercase">
        <span>ESSAI OFFERT</span>
      </div>
      <h1 class="text-3xl sm:text-4xl font-extrabold tracking-tight text-foreground">
        Analyse Gratuite CV ↔ Offre d'emploi
      </h1>
      <p class="text-base text-muted-foreground max-w-2xl">
        Testez le moteur de diagnostic immédiatement. Une analyse complète vous est offerte.
      </p>
      
      <div v-if="freeAnalysisStatus" class="mt-4 p-4 rounded-xl border text-sm font-medium transition-all" 
           :class="freeAnalysisStatus.can_use_free_analysis ? 'border-emerald-500/30 bg-emerald-500/5 text-emerald-600 dark:text-emerald-400' : 'border-amber-500/30 bg-amber-500/5 text-amber-600 dark:text-amber-400'">
        <div class="flex items-center gap-2.5">
          <CheckCircle v-if="freeAnalysisStatus.can_use_free_analysis" class="h-5 w-5 text-emerald-500 shrink-0" />
          <AlertCircle v-else class="h-5 w-5 text-amber-500 shrink-0" />
          <span>{{ freeAnalysisStatus.message }}</span>
        </div>
      </div>
    </div>

    <FreeTrialComparison />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { CheckCircle, AlertCircle } from 'lucide-vue-next'
import FreeTrialComparison from '@/components/FreeTrialComparison.vue'
import { checkFreeAnalysisStatus } from '@/lib/api'

const freeAnalysisStatus = ref<any>(null)

onMounted(async () => {
  try {
    freeAnalysisStatus.value = await checkFreeAnalysisStatus()
  } catch (error) {
    console.error('Erreur lors de la vérification du statut:', error)
  }
})
</script>
