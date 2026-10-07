import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import posthog from 'posthog-js'
import {
  getCoverLetter,
  streamCoverLetter,
  type CoverLetter,
  type CoverLetterLanguage,
  type CoverLetterLength,
  type CoverLetterSection,
  type CoverLetterTone,
} from '@/lib/api'
import { letterFromSections } from '@/lib/coverLetter'
import { t } from '@/i18n'
import { useApplicationContextStore } from './applicationContext'
import type { HistoryContext } from './compare'

export const useCoverLetterStore = defineStore('coverLetter', () => {
  // CV et offre : contexte de candidature partagé entre les modules
  const context = useApplicationContextStore()
  const historyContext = ref<HistoryContext | null>(null)
  const tone = ref<CoverLetterTone>('professional')
  const length = ref<CoverLetterLength>('standard')
  const language = ref<CoverLetterLanguage>('auto')

  // Sections reçues au fil du flux, puis lettre complète renvoyée en fin de flux (ou historique)
  const sections = ref<CoverLetterSection[]>([])
  const finalLetter = ref<CoverLetter | null>(null)
  const letterId = ref<string | null>(null)

  const loading = ref(false)
  const progress = ref(0)
  const status = ref('')
  const error = ref<string | null>(null)
  const errorCode = ref<string | null>(null)

  const hasData = computed(() => context.isComplete)
  const letter = computed<CoverLetter | null>(() => {
    if (finalLetter.value) return finalLetter.value
    return sections.value.length ? letterFromSections(sections.value) : null
  })

  function clearResult() {
    sections.value = []
    finalLetter.value = null
    letterId.value = null
    historyContext.value = null
    error.value = null
    errorCode.value = null
  }

  /** Définit le CV et l'offre de la lettre ouverte depuis l'historique comme contexte courant */
  function adoptHistoryContext() {
    if (!historyContext.value) return
    context.setContext(historyContext.value, 'coverLetter')
    historyContext.value = null
  }

  function dismissHistoryContext() {
    historyContext.value = null
  }

  async function generate() {
    if (!hasData.value) {
      error.value = t('coverLetter.errors.missingInput')
      return
    }

    clearResult()
    loading.value = true
    progress.value = 0
    status.value = t('coverLetter.statusStart')

    try {
      await streamCoverLetter(
        {
          jobText: context.offerText,
          cvText: context.cvText,
          tone: tone.value,
          length: length.value,
          language: language.value,
          offerUrl: context.offerUrl,
          applicationId: context.applicationId,
        },
        {
          onStatus: (message) => (status.value = message),
          onProgress: (value) => (progress.value = value),
          onSection: (section) => sections.value.push(section),
          onLetter: (result, id) => {
            finalLetter.value = result
            letterId.value = id
            status.value = t('coverLetter.statusDone')
            posthog.capture('cover_letter_generated', {
              tone: tone.value,
              length: length.value,
              language: language.value,
              letter_language: result.language || null,
              body_paragraph_count: result.body.length,
              saved_to_history: Boolean(id),
            })
          },
          onError: (message, code) => {
            error.value = message
            errorCode.value = code || null
            // Lettre partielle inutilisable : on n'affiche que l'erreur
            sections.value = []
          },
        },
      )
    } finally {
      loading.value = false
      progress.value = 0
    }
  }

  async function loadFromHistory(id: string) {
    loading.value = true
    error.value = null
    errorCode.value = null
    try {
      const detail = await getCoverLetter(id)
      const fromHistory = {
        cvText: detail.cv_text || '',
        offerText: detail.job_text || '',
        offerUrl: detail.offer_url || null,
      }
      // Contexte vide ou identique : repris directement, sinon proposé à l'utilisateur
      if (!context.hasContext) context.setContext(fromHistory, 'coverLetter')
      historyContext.value = context.matches(fromHistory.cvText, fromHistory.offerText) ? null : fromHistory
      tone.value = detail.tone
      length.value = detail.length
      sections.value = []
      finalLetter.value = detail.letter
      letterId.value = detail.id
      status.value = t('coverLetter.historyLoaded')
    } catch (err: any) {
      error.value = err.response?.data?.detail || t('coverLetter.errors.loadHistory')
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    historyContext,
    tone,
    length,
    language,
    letter,
    letterId,
    loading,
    progress,
    status,
    error,
    errorCode,
    hasData,
    generate,
    loadFromHistory,
    clearResult,
    adoptHistoryContext,
    dismissHistoryContext,
  }
})
