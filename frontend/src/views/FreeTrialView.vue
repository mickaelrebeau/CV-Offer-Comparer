<template>
  <div class="page-shell">
    <AppPageHeader
      label="Essai offert"
      title="Analyse gratuite"
      description="Testez le moteur de diagnostic immédiatement. Une analyse complète vous est offerte."
    >
      <div
        v-if="freeAnalysisStatus"
        class="mt-4 max-w-xl rounded-lg border p-4 font-mono text-micro uppercase"
        :class="freeAnalysisStatus.can_use_free_analysis
          ? 'border-emerald-500/25 bg-emerald-500/5 text-emerald-800'
          : 'border-amber-500/25 bg-amber-500/5 text-amber-800'"
      >
        <div class="flex items-center gap-2.5">
          <CheckCircle v-if="freeAnalysisStatus.can_use_free_analysis" class="h-4 w-4 shrink-0" />
          <AlertCircle v-else class="h-4 w-4 shrink-0" />
          <span>{{ freeAnalysisStatus.message }}</span>
        </div>
      </div>
    </AppPageHeader>

    <FreeTrialComparison />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { CheckCircle, AlertCircle } from 'lucide-vue-next'
import AppPageHeader from '@/components/AppPageHeader.vue'
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
