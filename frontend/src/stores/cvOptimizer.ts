import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import posthog from 'posthog-js'
import { getCvOptimization, streamCvOptimization, type CvSuggestion } from '@/lib/api'
import { applySuggestions, type SuggestionDecision } from '@/lib/cvOptimizer'
import { t } from '@/i18n'
import { useApplicationContextStore } from './applicationContext'

export const useCvOptimizerStore = defineStore('cvOptimizer', () => {
  // CV et offre : contexte de candidature partagé entre les modules
  const context = useApplicationContextStore()

  // Propositions et textes sur lesquels elles portent (figés au lancement ou lus dans l'historique)
  const suggestions = ref<CvSuggestion[]>([])
  const decisions = ref<Record<string, SuggestionDecision>>({})
  const summary = ref('')
  const sourceCv = ref('')
  const sourceOffer = ref<{ text: string; url: string | null } | null>(null)
  // Analyse d'origine (exigences manquantes ou floues ciblées) et entrée d'historique
  const comparisonId = ref<string | null>(null)
  const optimizationId = ref<string | null>(null)

  const loading = ref(false)
  const progress = ref(0)
  const status = ref('')
  const error = ref<string | null>(null)
  const errorCode = ref<string | null>(null)

  const hasData = computed(() => context.isComplete)
  const optimized = computed(() => applySuggestions(sourceCv.value, suggestions.value, decisions.value))
  const counts = computed(() => {
    const values = Object.values(decisions.value)
    return {
      accepted: values.filter((decision) => decision.status === 'accepted').length,
      rejected: values.filter((decision) => decision.status === 'rejected').length,
      pending: values.filter((decision) => decision.status === 'pending').length,
    }
  })

  function addSuggestion(suggestion: CvSuggestion) {
    suggestions.value.push(suggestion)
    decisions.value[suggestion.id] = { status: 'pending', text: suggestion.proposed }
  }

  function clearResult() {
    suggestions.value = []
    decisions.value = {}
    summary.value = ''
    optimizationId.value = null
    error.value = null
    errorCode.value = null
  }

  /** Lance l'optimisation : depuis une analyse (`fromComparisonId`) ou depuis le contexte courant. */
  async function optimize(fromComparisonId: string | null = null) {
    if (!fromComparisonId && !hasData.value) {
      error.value = t('cvOptimizer.errors.missingInput')
      return
    }

    clearResult()
    comparisonId.value = fromComparisonId
    sourceCv.value = fromComparisonId ? '' : context.cvText
    sourceOffer.value = fromComparisonId ? null : { text: context.offerText, url: context.offerUrl }
    loading.value = true
    progress.value = 0
    status.value = t('cvOptimizer.statusStart')

    try {
      await streamCvOptimization(
        fromComparisonId
          ? { comparisonId: fromComparisonId }
          : { cvText: context.cvText, jobText: context.offerText, offerUrl: context.offerUrl },
        {
          onStatus: (message) => (status.value = message),
          onProgress: (value) => (progress.value = value),
          onSuggestion: addSuggestion,
          onResult: async (resultSummary, id) => {
            summary.value = resultSummary
            optimizationId.value = id
            status.value = t('cvOptimizer.statusDone')
            posthog.capture('cv_optimized', {
              suggestion_count: suggestions.value.length,
              from_analysis: Boolean(fromComparisonId),
              saved_to_history: Boolean(id),
            })
            // Depuis une analyse, le CV et l'offre sont ceux enregistrés côté serveur : relus via l'historique
            if (fromComparisonId && id) await loadSources(id)
          },
          onError: (message, code) => {
            error.value = message
            errorCode.value = code || null
            suggestions.value = []
            decisions.value = {}
          },
        },
      )
    } finally {
      loading.value = false
      progress.value = 0
    }
  }

  async function loadSources(id: string) {
    try {
      const detail = await getCvOptimization(id)
      sourceCv.value = detail.cv_text
      sourceOffer.value = { text: detail.job_text, url: detail.offer_url }
    } catch (err) {
      console.error('Optimisation : CV source indisponible', err)
    }
  }

  async function loadFromHistory(id: string) {
    loading.value = true
    error.value = null
    errorCode.value = null
    try {
      const detail = await getCvOptimization(id)
      clearResult()
      detail.suggestions.forEach(addSuggestion)
      summary.value = detail.summary
      sourceCv.value = detail.cv_text
      sourceOffer.value = { text: detail.job_text, url: detail.offer_url }
      comparisonId.value = detail.comparison_id
      optimizationId.value = detail.id
      status.value = t('cvOptimizer.historyLoaded')
    } catch (err: any) {
      error.value = err.response?.data?.detail || t('cvOptimizer.errors.loadHistory')
      throw err
    } finally {
      loading.value = false
    }
  }

  function decide(id: string, next: SuggestionDecision['status'], text?: string) {
    const decision = decisions.value[id]
    if (!decision) return
    decisions.value[id] = { status: next, text: text?.trim() || decision.text }
    if (next === 'accepted') {
      const suggestion = suggestions.value.find((item) => item.id === id)
      posthog.capture('cv_suggestion_accepted', {
        edited: decisions.value[id].text !== suggestion?.proposed,
        section: suggestion?.section || null,
      })
    }
  }

  const accept = (id: string, text?: string) => decide(id, 'accepted', text)
  const reject = (id: string) => decide(id, 'rejected')
  const reset = (id: string) => decide(id, 'pending')

  function acceptAll() {
    for (const suggestion of suggestions.value) {
      if (decisions.value[suggestion.id]?.status === 'pending') accept(suggestion.id)
    }
  }

  /** Le CV optimisé devient le CV courant (réanalyse, lettre, entretien). */
  function useOptimizedCv() {
    context.setCv(optimized.value.text, { from: 'cvOptimizer' })
    if (sourceOffer.value && context.offerText.trim() !== sourceOffer.value.text.trim()) {
      context.setOffer(sourceOffer.value.text, { url: sourceOffer.value.url, from: 'cvOptimizer' })
    }
  }

  return {
    suggestions,
    decisions,
    summary,
    sourceCv,
    sourceOffer,
    comparisonId,
    optimizationId,
    loading,
    progress,
    status,
    error,
    errorCode,
    hasData,
    optimized,
    counts,
    optimize,
    loadFromHistory,
    accept,
    reject,
    reset,
    acceptAll,
    useOptimizedCv,
    clearResult,
  }
})
