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

    <section class="mt-12">
      <div class="mb-5 flex items-end justify-between gap-4">
        <div>
          <p class="font-mono text-micro uppercase text-ink-soft">Historique</p>
          <h2 class="mt-1 font-medium text-title">Comparaisons récentes</h2>
        </div>
        <button
          v-if="history.length"
          type="button"
          class="btn-secondary h-9 px-4 text-micro"
          :disabled="historyLoading"
          @click="loadHistory"
        >
          Actualiser
        </button>
      </div>

      <div v-if="historyLoading" class="panel p-6 font-mono text-micro uppercase text-ink-soft">
        Chargement de l'historique…
      </div>

      <div
        v-else-if="historyError"
        class="panel border-rose-500/25 bg-rose-500/5 p-6 font-mono text-micro text-rose-700"
      >
        {{ historyError }}
      </div>

      <div v-else-if="!history.length" class="panel p-6 sm:p-8">
        <p class="text-lead text-ink-soft">
          Aucune comparaison enregistrée pour le moment. Lancez une analyse depuis le module comparateur
          — elle apparaîtra ici automatiquement.
        </p>
        <button type="button" class="btn-primary mt-6" @click="router.push('/compare')">
          Lancer une comparaison
        </button>
      </div>

      <ul v-else class="space-y-3">
        <li
          v-for="item in history"
          :key="item.id"
          class="panel flex flex-col gap-4 p-5 sm:flex-row sm:items-center sm:justify-between"
        >
          <div class="min-w-0 flex-1">
            <div class="mb-2 flex flex-wrap items-center gap-3 font-mono text-micro uppercase text-ink-soft">
              <span>{{ formatDate(item.created_at) }}</span>
              <span>{{ Math.round(item.match_percentage) }}% match</span>
              <span>{{ item.matches }}/{{ item.total_items }} critères</span>
            </div>
            <p class="truncate text-sm text-ink">{{ item.offer_excerpt || 'Offre sans extrait' }}</p>
            <p class="mt-1 truncate text-sm text-ink-soft">{{ item.cv_excerpt || 'CV sans extrait' }}</p>
          </div>
          <div class="flex shrink-0 gap-2">
            <button type="button" class="btn-secondary h-9 px-4 text-micro" @click="openHistory(item.id)">
              Voir
            </button>
            <button
              type="button"
              class="h-9 rounded-lg px-3 font-mono text-micro uppercase text-rose-700 transition-colors hover:bg-rose-500/10"
              :disabled="deletingId === item.id"
              @click="removeHistory(item.id)"
            >
              Supprimer
            </button>
          </div>
        </li>
      </ul>
    </section>

    <section class="mt-12">
      <div class="mb-5 flex items-end justify-between gap-4">
        <div>
          <p class="font-mono text-micro uppercase text-ink-soft">Historique</p>
          <h2 class="mt-1 font-medium text-title">Simulations d’entretien récentes</h2>
        </div>
        <button
          v-if="interviewHistory.length"
          type="button"
          class="btn-secondary h-9 px-4 text-micro"
          :disabled="interviewLoading"
          @click="loadInterviewHistory"
        >
          Actualiser
        </button>
      </div>

      <div v-if="interviewLoading" class="panel p-6 font-mono text-micro uppercase text-ink-soft">
        Chargement des simulations…
      </div>

      <div
        v-else-if="interviewError"
        class="panel border-rose-500/25 bg-rose-500/5 p-6 font-mono text-micro text-rose-700"
      >
        {{ interviewError }}
      </div>

      <div v-else-if="!interviewHistory.length" class="panel p-6 sm:p-8">
        <p class="text-lead text-ink-soft">
          Aucune simulation enregistrée pour le moment. Terminez un entretien depuis le simulateur —
          le rapport apparaîtra ici automatiquement.
        </p>
        <button type="button" class="btn-primary mt-6" @click="router.push('/interview-simulator')">
          Démarrer une simulation
        </button>
      </div>

      <ul v-else class="space-y-3">
        <li
          v-for="item in interviewHistory"
          :key="item.id"
          class="panel flex flex-col gap-4 p-5 sm:flex-row sm:items-center sm:justify-between"
        >
          <div class="min-w-0 flex-1">
            <div class="mb-2 flex flex-wrap items-center gap-3 font-mono text-micro uppercase text-ink-soft">
              <span>{{ formatDate(item.created_at) }}</span>
              <span>{{ formatScore(item.score_global) }}/10</span>
              <span>{{ item.num_questions }} questions</span>
              <span>{{ formatDuration(item.duration_seconds) }}</span>
            </div>
            <p class="truncate text-sm text-ink">{{ item.job_excerpt || 'Offre sans extrait' }}</p>
            <p class="mt-1 truncate text-sm text-ink-soft">{{ item.cv_excerpt || 'CV sans extrait' }}</p>
          </div>
          <div class="flex shrink-0 gap-2">
            <button
              type="button"
              class="btn-secondary h-9 px-4 text-micro"
              @click="openInterviewHistory(item.id)"
            >
              Voir
            </button>
            <button
              type="button"
              class="h-9 rounded-lg px-3 font-mono text-micro uppercase text-rose-700 transition-colors hover:bg-rose-500/10"
              :disabled="deletingInterviewId === item.id"
              @click="removeInterviewHistory(item.id)"
            >
              Supprimer
            </button>
          </div>
        </li>
      </ul>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowRight } from 'lucide-vue-next'
import AppPageHeader from '@/components/AppPageHeader.vue'
import {
  deleteComparison,
  deleteInterview,
  listComparisons,
  listInterviews,
  type ComparisonHistoryItem,
  type InterviewHistoryItem,
} from '@/lib/api'

const router = useRouter()
const history = ref<ComparisonHistoryItem[]>([])
const historyLoading = ref(true)
const historyError = ref('')
const deletingId = ref<string | null>(null)

const interviewHistory = ref<InterviewHistoryItem[]>([])
const interviewLoading = ref(true)
const interviewError = ref('')
const deletingInterviewId = ref<string | null>(null)

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

async function loadHistory() {
  historyLoading.value = true
  historyError.value = ''
  try {
    const data = await listComparisons(10)
    history.value = data.items
  } catch (err: any) {
    historyError.value = err.response?.data?.detail || 'Impossible de charger l\'historique'
  } finally {
    historyLoading.value = false
  }
}

async function loadInterviewHistory() {
  interviewLoading.value = true
  interviewError.value = ''
  try {
    const data = await listInterviews(10)
    interviewHistory.value = data.items
  } catch (err: any) {
    interviewError.value = err.response?.data?.detail || 'Impossible de charger les simulations'
  } finally {
    interviewLoading.value = false
  }
}

function formatDate(value: string | null) {
  if (!value) return '—'
  return new Intl.DateTimeFormat('fr-FR', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

function formatScore(score: number) {
  return Number.isFinite(score) ? Math.round(score * 10) / 10 : '—'
}

function formatDuration(seconds: number) {
  const m = Math.floor((seconds || 0) / 60)
  const s = (seconds || 0) % 60
  return `${m}:${s.toString().padStart(2, '0')}`
}

function openHistory(id: string) {
  router.push({ path: '/compare', query: { history: id } })
}

function openInterviewHistory(id: string) {
  router.push({ path: '/interview-results', query: { history: id } })
}

async function removeHistory(id: string) {
  deletingId.value = id
  try {
    await deleteComparison(id)
    history.value = history.value.filter((item) => item.id !== id)
  } catch (err: any) {
    historyError.value = err.response?.data?.detail || 'Suppression impossible'
  } finally {
    deletingId.value = null
  }
}

async function removeInterviewHistory(id: string) {
  deletingInterviewId.value = id
  try {
    await deleteInterview(id)
    interviewHistory.value = interviewHistory.value.filter((item) => item.id !== id)
  } catch (err: any) {
    interviewError.value = err.response?.data?.detail || 'Suppression impossible'
  } finally {
    deletingInterviewId.value = null
  }
}

onMounted(() => {
  loadHistory()
  loadInterviewHistory()
})
</script>
