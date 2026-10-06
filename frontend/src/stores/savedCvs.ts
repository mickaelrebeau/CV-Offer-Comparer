import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import posthog from 'posthog-js'
import {
  createSavedCv,
  deleteSavedCv,
  getSavedCv,
  listSavedCvs,
  setDefaultSavedCv,
  updateSavedCv,
  type SavedCv,
  type SavedCvListing,
} from '@/lib/api'
import { t } from '@/i18n'
import { useApplicationContextStore, type ContextModule } from './applicationContext'

/** Module où le CV est enregistré ou choisi (analytics) */
export type SavedCvOrigin = ContextModule | 'profile'

/**
 * Bibliothèque « Mes CV » d'un compte connecté. Les textes complets ne sont chargés qu'à la
 * sélection, puis gardés en mémoire (jamais en stockage navigateur) : réutilisables hors ligne
 * pendant la session, purgés à la déconnexion.
 */
export const useSavedCvsStore = defineStore('savedCvs', () => {
  const context = useApplicationContextStore()

  const items = ref<SavedCv[]>([])
  const limit = ref(5)
  const loaded = ref(false)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const texts = new Map<string, string>()
  let pending: Promise<void> | null = null

  const defaultCv = computed(() => items.value.find((item) => item.is_default) ?? null)
  const limitReached = computed(() => items.value.length >= limit.value)

  function apiMessage(err: any, fallback: string) {
    return err?.response?.data?.detail || fallback
  }

  function applyListing(listing: SavedCvListing) {
    items.value = listing.items
    limit.value = listing.limit
    loaded.value = true
    // Textes des CV supprimés : retirés du cache
    const ids = new Set(listing.items.map((item) => item.id))
    for (const id of texts.keys()) if (!ids.has(id)) texts.delete(id)
  }

  /** Liste des CV (une seule requête à la fois ; `force` pour rafraîchir). */
  async function fetch(force = false) {
    if (loaded.value && !force) return
    if (pending) return pending
    loading.value = true
    error.value = null
    pending = (async () => {
      try {
        applyListing(await listSavedCvs())
      } catch (err: any) {
        error.value = apiMessage(err, t('savedCvs.errors.load'))
      } finally {
        loading.value = false
        pending = null
      }
    })()
    return pending
  }

  async function loadText(id: string) {
    const cached = texts.get(id)
    if (cached !== undefined) return cached
    const detail = await getSavedCv(id)
    texts.set(id, detail.text)
    return detail.text
  }

  // Nom affiché dans le contexte (encart, import) : celui donné au CV, plus parlant que le fichier
  const displayName = (cv: Pick<SavedCv, 'label'>) => cv.label

  /** Charge un CV enregistré dans le contexte partagé. */
  async function select(id: string, module: ContextModule) {
    const cv = items.value.find((item) => item.id === id)
    if (!cv) return
    const text = await loadText(id)
    context.setCv(text, { fileName: displayName(cv), savedCvId: id, from: module })
    posthog.capture('cv_selected', { module, is_default: cv.is_default, saved_cv_count: items.value.length })
  }

  async function create(
    body: { label: string; text: string; sourceFilename?: string | null; makeDefault?: boolean },
    origin: SavedCvOrigin,
  ) {
    const created = await createSavedCv({
      label: body.label,
      text: body.text,
      source_filename: body.sourceFilename ?? null,
      is_default: Boolean(body.makeDefault),
    })
    texts.set(created.id, created.text)
    await fetch(true)
    posthog.capture('cv_saved', {
      origin,
      is_default: created.is_default,
      has_source_file: Boolean(created.source_filename),
      saved_cv_count: items.value.length,
    })
    return created
  }

  function upsertItem(updated: SavedCv) {
    items.value = items.value.map((item) => (item.id === updated.id ? { ...item, ...updated } : item))
  }

  async function rename(id: string, label: string) {
    const updated = await updateSavedCv(id, { label })
    texts.set(id, updated.text)
    upsertItem(updated)
    return updated
  }

  async function replace(id: string, text: string, sourceFilename: string | null) {
    const updated = await updateSavedCv(id, { text, source_filename: sourceFilename })
    texts.set(id, updated.text)
    upsertItem(updated)
    // Le contexte suivait ce CV : il reprend le nouveau contenu
    if (context.savedCvId === id) {
      context.setCv(updated.text, { fileName: displayName(updated), savedCvId: id })
    }
    return updated
  }

  async function setDefault(id: string) {
    applyListing(await setDefaultSavedCv(id))
  }

  async function remove(id: string) {
    applyListing(await deleteSavedCv(id))
    // Le texte reste dans le contexte, mais n'est plus rattaché à un CV enregistré
    if (context.savedCvId === id) context.savedCvId = null
  }

  /** À la connexion : le CV par défaut est pré-chargé si aucun CV n'est déjà en contexte. */
  async function preloadDefault() {
    if (context.hasCv) return
    await fetch()
    const cv = defaultCv.value
    if (!cv || context.hasCv) return
    try {
      const text = await loadText(cv.id)
      // L'utilisateur a pu saisir un CV entre-temps : ne jamais l'écraser
      if (!context.hasCv) context.setCv(text, { fileName: displayName(cv), savedCvId: cv.id })
    } catch {
      // Hors ligne : rien à pré-charger, le sélecteur reste disponible
    }
  }

  /** Déconnexion / changement de compte : rien ne reste en mémoire. */
  function reset() {
    items.value = []
    limit.value = 5
    loaded.value = false
    error.value = null
    texts.clear()
  }

  return {
    items,
    limit,
    loaded,
    loading,
    error,
    defaultCv,
    limitReached,
    fetch,
    loadText,
    select,
    create,
    rename,
    replace,
    setDefault,
    remove,
    preloadDefault,
    reset,
    isCached: (id: string) => texts.has(id),
  }
})
