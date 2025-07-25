<template>
  <div class="max-w-7xl mx-auto">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-primary mb-2">
        🎁 Essai Gratuit - Comparateur CV ↔ Offre d'emploi
      </h1>
      <p class="text-muted-foreground">
        Testez notre outil gratuitement ! Une seule analyse gratuite par utilisateur.
      </p>
      
      <!-- Statut de l'essai gratuit -->
      <div v-if="freeAnalysisStatus" class="mt-4 p-4 rounded-lg border" 
           :class="freeAnalysisStatus.can_use_free_analysis ? 'border-green-200 bg-green-50' : 'border-amber-200 bg-amber-50'">
        <div class="flex items-center">
          <CheckCircle v-if="freeAnalysisStatus.can_use_free_analysis" class="h-5 w-5 text-green-600 mr-2" />
          <AlertCircle v-else class="h-5 w-5 text-amber-600 mr-2" />
          <span class="text-sm font-medium" :class="freeAnalysisStatus.can_use_free_analysis ? 'text-green-800' : 'text-amber-800'">
            {{ freeAnalysisStatus.message }}
          </span>
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