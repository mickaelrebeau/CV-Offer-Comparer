<template>
  <div class="max-w-6xl mx-auto px-6 py-10 sm:py-16 space-y-10">
    <!-- Header -->
    <div class="space-y-3">
      <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-zinc-100 dark:bg-zinc-800 text-xs font-semibold tracking-wider uppercase text-muted-foreground">
        <span>ESPACE CANDIDAT</span>
      </div>
      <h1 class="text-3xl sm:text-4xl font-extrabold tracking-tight text-foreground">
        Tableau de bord
      </h1>
      <p class="text-base text-muted-foreground max-w-xl">
        Sélectionnez le module d'optimisation adapté à l'avancement de votre candidature.
      </p>
    </div>

    <!-- Core Tools Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
      <!-- Comparateur CV ↔ Offre Card -->
      <Card class="glass-card p-8 rounded-2xl cursor-pointer hover:border-brand-500/50 transition-all flex flex-col justify-between group relative overflow-hidden" @click="goToComparator">
        <div class="space-y-6 z-10">
          <div class="w-12 h-12 rounded-xl bg-indigo-500/10 text-indigo-500 flex items-center justify-center group-hover:scale-110 transition-transform">
            <FileText class="h-6 w-6" />
          </div>

          <div class="space-y-2">
            <h2 class="text-2xl font-bold tracking-tight text-foreground group-hover:text-brand-500 transition-colors">
              Comparateur CV ↔ Offre
            </h2>
            <p class="text-sm text-muted-foreground leading-relaxed">
              Analysez le niveau d'adéquation entre votre CV et une fiche de poste. Identifiez instantanément les mots-clés manquants.
            </p>
          </div>

          <div class="space-y-2.5 pt-2">
            <div class="flex items-center gap-2.5 text-xs font-medium text-foreground">
              <CheckCircle class="h-4 w-4 text-emerald-500 shrink-0" />
              <span>Diagnostic d'écart sémantique</span>
            </div>
            <div class="flex items-center gap-2.5 text-xs font-medium text-foreground">
              <CheckCircle class="h-4 w-4 text-emerald-500 shrink-0" />
              <span>Extraction automatique des compétences requises</span>
            </div>
            <div class="flex items-center gap-2.5 text-xs font-medium text-foreground">
              <CheckCircle class="h-4 w-4 text-emerald-500 shrink-0" />
              <span>Suggestions de reformulation directes</span>
            </div>
          </div>
        </div>

        <div class="mt-8 pt-6 border-t border-border flex items-center justify-between z-10">
          <span class="text-xs font-semibold text-foreground group-hover:text-brand-500 transition-colors flex items-center gap-1.5">
            Lancer une comparaison
            <ArrowRight class="h-4 w-4 group-hover:translate-x-1 transition-transform" />
          </span>
          <span class="text-xs font-mono text-muted-foreground">Module 01</span>
        </div>
      </Card>

      <!-- Simulateur d'entretien Card -->
      <Card class="glass-card p-8 rounded-2xl cursor-pointer hover:border-brand-500/50 transition-all flex flex-col justify-between group relative overflow-hidden" @click="goToInterviewSimulator">
        <div class="space-y-6 z-10">
          <div class="w-12 h-12 rounded-xl bg-purple-500/10 text-purple-500 flex items-center justify-center group-hover:scale-110 transition-transform">
            <MessageSquare class="h-6 w-6" />
          </div>

          <div class="space-y-2">
            <h2 class="text-2xl font-bold tracking-tight text-foreground group-hover:text-brand-500 transition-colors">
              Simulateur d'Entretien
            </h2>
            <p class="text-sm text-muted-foreground leading-relaxed">
              Préparez l'étape décisive avec des questions sur-mesure générées selon les spécificités de votre profil et de l'employeur.
            </p>
          </div>

          <div class="space-y-2.5 pt-2">
            <div class="flex items-center gap-2.5 text-xs font-medium text-foreground">
              <CheckCircle class="h-4 w-4 text-emerald-500 shrink-0" />
              <span>Questions prédictives ciblées</span>
            </div>
            <div class="flex items-center gap-2.5 text-xs font-medium text-foreground">
              <CheckCircle class="h-4 w-4 text-emerald-500 shrink-0" />
              <span>Chronomètre d'entraînement en direct</span>
            </div>
            <div class="flex items-center gap-2.5 text-xs font-medium text-foreground">
              <CheckCircle class="h-4 w-4 text-emerald-500 shrink-0" />
              <span>Évaluation détaillée de vos réponses</span>
            </div>
          </div>
        </div>

        <div class="mt-8 pt-6 border-t border-border flex items-center justify-between z-10">
          <span class="text-xs font-semibold text-foreground group-hover:text-brand-500 transition-colors flex items-center gap-1.5">
            Démarrer la simulation
            <ArrowRight class="h-4 w-4 group-hover:translate-x-1 transition-transform" />
          </span>
          <span class="text-xs font-mono text-muted-foreground">Module 02</span>
        </div>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Card } from '@/components/ui/card'
import { FileText, MessageSquare, CheckCircle, ArrowRight } from 'lucide-vue-next'

const router = useRouter()

const goToComparator = () => {
  router.push('/compare')
}

const goToInterviewSimulator = () => {
  router.push('/interview-simulator')
}
</script>
