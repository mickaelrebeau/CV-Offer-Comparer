import { defineStore } from 'pinia'
import { computed, ref, watch } from 'vue'
import posthog from 'posthog-js'
import { STORAGE_KEYS } from '@/lib/storageKeys'

/**
 * Contexte de candidature (CV + offre) partagé par le comparateur, le simulateur
 * d'entretien et la lettre de motivation. Persisté en sessionStorage uniquement :
 * il survit au rechargement et à la navigation PWA, pas à la fermeture de l'onglet.
 */

export type ContextModule = 'compare' | 'interview' | 'coverLetter'

export interface ApplicationContext {
  cvText: string
  cvFileName: string | null
  /** CV de la bibliothèque (« Mes CV ») dont provient le texte, tant qu'il n'est pas modifié */
  savedCvId: string | null
  offerText: string
  offerUrl: string | null
  updatedAt: string | null
  /** Module qui a saisi le contexte en dernier (analytics `context_reused`) */
  source: ContextModule | null
}

export const CONTEXT_VERSION = 1

interface StoredContext extends ApplicationContext {
  version: typeof CONTEXT_VERSION
}

const MODULES: readonly ContextModule[] = ['compare', 'interview', 'coverLetter']

const text = (value: unknown) => (typeof value === 'string' ? value : '')
const optionalText = (value: unknown) => (typeof value === 'string' && value.trim() ? value : null)

export function emptyContext(): ApplicationContext {
  return {
    cvText: '',
    cvFileName: null,
    savedCvId: null,
    offerText: '',
    offerUrl: null,
    updatedAt: null,
    source: null,
  }
}

/**
 * Normalise une valeur lue en sessionStorage vers le schéma courant.
 * - v0 (sans `version`) : noms de champs des anciens stores (`jobText`, `offer_text`, `cv_text`…)
 * - version inconnue (plus récente) ou contenu invalide : ignoré
 */
export function migrateContext(raw: unknown): ApplicationContext | null {
  if (!raw || typeof raw !== 'object' || Array.isArray(raw)) return null
  const data = raw as Record<string, unknown>
  const version = data.version ?? 0
  if (version !== 0 && version !== CONTEXT_VERSION) return null

  const context: ApplicationContext = {
    cvText: text(data.cvText ?? data.cv_text),
    cvFileName: optionalText(data.cvFileName ?? data.cv_file_name),
    savedCvId: optionalText(data.savedCvId),
    offerText: text(data.offerText ?? data.jobText ?? data.offer_text ?? data.job_text),
    offerUrl: optionalText(data.offerUrl ?? data.offer_url),
    updatedAt: optionalText(data.updatedAt ?? data.updated_at),
    source: MODULES.includes(data.source as ContextModule) ? (data.source as ContextModule) : null,
  }
  return context.cvText.trim() || context.offerText.trim() ? context : null
}

function storage(): Storage | null {
  try {
    return typeof window === 'undefined' ? null : window.sessionStorage
  } catch {
    // Accès refusé (cookies bloqués, navigation privée stricte)
    return null
  }
}

function readContext(): ApplicationContext | null {
  const store = storage()
  if (!store) return null
  try {
    const raw = store.getItem(STORAGE_KEYS.applicationContext)
    if (raw === null) return null
    const context = migrateContext(JSON.parse(raw))
    if (!context) store.removeItem(STORAGE_KEYS.applicationContext)
    return context
  } catch {
    store.removeItem(STORAGE_KEYS.applicationContext)
    return null
  }
}

function writeContext(context: ApplicationContext) {
  const store = storage()
  if (!store) return
  try {
    if (!context.cvText.trim() && !context.offerText.trim()) {
      store.removeItem(STORAGE_KEYS.applicationContext)
      return
    }
    const payload: StoredContext = { version: CONTEXT_VERSION, ...context }
    store.setItem(STORAGE_KEYS.applicationContext, JSON.stringify(payload))
  } catch {
    // Quota dépassé : le contexte reste disponible en mémoire pour la session
  }
}

/** Purge sans instancier le store (déconnexion, suppression du compte). */
export function clearStoredApplicationContext() {
  try {
    storage()?.removeItem(STORAGE_KEYS.applicationContext)
  } catch {
    // ignoré
  }
}

export const useApplicationContextStore = defineStore('applicationContext', () => {
  const initial = readContext() ?? emptyContext()

  const cvText = ref(initial.cvText)
  const cvFileName = ref<string | null>(initial.cvFileName)
  const savedCvId = ref<string | null>(initial.savedCvId)
  const offerText = ref(initial.offerText)
  const offerUrl = ref<string | null>(initial.offerUrl)
  const updatedAt = ref<string | null>(initial.updatedAt)
  const source = ref<ContextModule | null>(initial.source)

  const hasCv = computed(() => Boolean(cvText.value.trim()))
  const hasOffer = computed(() => Boolean(offerText.value.trim()))
  const hasContext = computed(() => hasCv.value || hasOffer.value)
  const isComplete = computed(() => hasCv.value && hasOffer.value)

  const snapshot = computed<ApplicationContext>(() => ({
    cvText: cvText.value,
    cvFileName: cvFileName.value,
    savedCvId: savedCvId.value,
    offerText: offerText.value,
    offerUrl: offerUrl.value,
    updatedAt: updatedAt.value,
    source: source.value,
  }))

  watch(snapshot, writeContext)

  function touch(from?: ContextModule) {
    updatedAt.value = new Date().toISOString()
    if (from) source.value = from
  }

  /**
   * CV saisi, importé ou choisi dans « Mes CV ». Le nom de fichier et le lien vers le CV
   * enregistré sont oubliés dès que le texte est édité à la main.
   */
  function setCv(
    value: string,
    options: { fileName?: string | null; savedCvId?: string | null; from?: ContextModule } = {},
  ) {
    cvText.value = String(value || '')
    const hasText = Boolean(cvText.value.trim())
    cvFileName.value = hasText ? options.fileName ?? null : null
    savedCvId.value = hasText ? options.savedCvId ?? null : null
    touch(options.from)
  }

  /** Offre saisie ou importée ; `url` omis = lien conservé, effacé avec le texte. */
  function setOffer(value: string, options: { url?: string | null; from?: ContextModule } = {}) {
    offerText.value = String(value || '')
    if (!offerText.value.trim()) offerUrl.value = null
    else if (options.url !== undefined) offerUrl.value = optionalText(options.url)
    touch(options.from)
  }

  /** Remplace tout le contexte (ex. élément de l'historique choisi comme contexte courant). */
  function setContext(next: Partial<ApplicationContext>, from?: ContextModule) {
    cvText.value = text(next.cvText)
    cvFileName.value = optionalText(next.cvFileName)
    savedCvId.value = optionalText(next.savedCvId)
    offerText.value = text(next.offerText)
    offerUrl.value = optionalText(next.offerUrl)
    touch(from)
  }

  /** Vrai si le CV et l'offre donnés sont déjà ceux du contexte courant. */
  function matches(cv: string, offer: string) {
    return cvText.value.trim() === cv.trim() && offerText.value.trim() === offer.trim()
  }

  function clear() {
    const empty = emptyContext()
    cvText.value = empty.cvText
    cvFileName.value = empty.cvFileName
    savedCvId.value = empty.savedCvId
    offerText.value = empty.offerText
    offerUrl.value = empty.offerUrl
    updatedAt.value = empty.updatedAt
    source.value = empty.source
    clearStoredApplicationContext()
  }

  /** À l'ouverture d'un module : signale la réutilisation d'un contexte saisi ailleurs (aucun contenu envoyé). */
  function trackReuse(target: ContextModule) {
    if (!hasContext.value || !source.value || source.value === target) return
    posthog.capture('context_reused', {
      source_module: source.value,
      target_module: target,
      has_cv: hasCv.value,
      has_offer: hasOffer.value,
    })
  }

  return {
    cvText,
    cvFileName,
    savedCvId,
    offerText,
    offerUrl,
    updatedAt,
    source,
    hasCv,
    hasOffer,
    hasContext,
    isComplete,
    setCv,
    setOffer,
    setContext,
    matches,
    clear,
    trackReuse,
  }
})
