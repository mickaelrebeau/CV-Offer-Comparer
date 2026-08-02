<template>
  <div class="max-w-7xl mx-auto px-6 py-10 sm:py-16 space-y-8">
    <div class="space-y-3">
      <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 text-xs font-semibold tracking-wider uppercase">
        <span>ESPACE COMPARATEUR</span>
      </div>
      <h1 class="text-3xl sm:text-4xl font-extrabold tracking-tight text-foreground">
        Comparateur CV ↔ Offre d'emploi
      </h1>
      <p class="text-base text-muted-foreground max-w-2xl">
        Évaluez l'adéquation sémantique exacte entre votre profil et la fiche de poste.
      </p>
    </div>

    <ComparisonView />
  </div>
</template>

<script setup lang="ts">
import ComparisonView from '@/components/ComparisonView.vue'
</script>
