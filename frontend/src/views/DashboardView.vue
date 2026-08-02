<template>
  <div class="page-shell">
    <AppPageHeader
      label="Espace candidat"
      title="Tableau de bord"
      description="Sélectionnez le module adapté à l'avancement de votre candidature."
    />

    <div class="grid grid-cols-1 gap-6 md:grid-cols-2">
      <article
        v-for="module in modules"
        :key="module.path"
        class="panel group cursor-pointer p-6 transition-colors hover:border-ink/30 sm:p-8"
        @click="router.push(module.path)"
      >
        <div class="mb-6 font-mono text-micro uppercase text-ink-soft">{{ module.id }}</div>
        <h2 class="mb-3 font-medium text-title transition-colors group-hover:text-ink-soft">
          {{ module.title }}
        </h2>
        <p class="mb-6 max-w-[42ch] text-lead text-ink-soft">{{ module.description }}</p>
        <ul class="mb-8 space-y-2 font-mono text-micro uppercase text-ink-soft">
          <li v-for="feature in module.features" :key="feature" class="flex gap-2">
            <span class="text-ink/30">—</span>
            <span>{{ feature }}</span>
          </li>
        </ul>
        <div class="flex items-center justify-between border-t border-ink/10 pt-5 font-mono text-micro uppercase">
          <span class="text-ink transition-opacity group-hover:opacity-70">{{ module.cta }}</span>
          <ArrowRight class="h-4 w-4 text-ink-soft transition-transform group-hover:translate-x-1" />
        </div>
      </article>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ArrowRight } from 'lucide-vue-next'
import AppPageHeader from '@/components/AppPageHeader.vue'

const router = useRouter()

const modules = [
  {
    id: 'Module 01',
    path: '/compare',
    title: 'Comparateur CV ↔ Offre',
    description: "Analysez l'adéquation entre votre CV et une fiche de poste. Identifiez les mots-clés manquants.",
    features: ['Diagnostic d\'écart sémantique', 'Extraction des compétences requises', 'Reformulations directes'],
    cta: 'Lancer une comparaison',
  },
  {
    id: 'Module 02',
    path: '/interview-simulator',
    title: "Simulateur d'entretien",
    description: 'Préparez l\'étape décisive avec des questions générées selon votre profil et l\'offre visée.',
    features: ['Questions prédictives ciblées', 'Chronomètre en direct', 'Évaluation des réponses'],
    cta: 'Démarrer la simulation',
  },
]
</script>
