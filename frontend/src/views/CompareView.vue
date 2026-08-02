<template>
  <div class="page-shell">
    <AppPageHeader
      label="Comparateur"
      title="CV ↔ Offre d'emploi"
      description="Évaluez l'adéquation sémantique exacte entre votre profil et la fiche de poste."
    />
    <ComparisonView />
  </div>
</template>

<script setup lang="ts">
import AppPageHeader from '@/components/AppPageHeader.vue'
import ComparisonView from '@/components/ComparisonView.vue'
</script>
