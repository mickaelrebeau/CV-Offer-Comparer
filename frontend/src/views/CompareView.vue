<template>
  <div class="max-w-7xl mx-auto">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-primary mb-2">
        Comparateur CV ↔ Offre d'emploi
      </h1>
      <p class="text-muted-foreground">
        Analysez la correspondance entre votre CV et l'offre d'emploi
      </p>
    </div>

    <ComparisonView />
  </div>
</template>

<script setup lang="ts">
import ComparisonView from '@/components/ComparisonView.vue'
</script> 