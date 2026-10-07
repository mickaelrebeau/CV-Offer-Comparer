import { defineStore } from 'pinia'
import { ref } from 'vue'
import posthog from 'posthog-js'
import {
  createApplication,
  deleteApplication,
  listApplications,
  updateApplication,
  type Application,
  type ApplicationDetail,
  type ApplicationInput,
  type ApplicationStatus,
} from '@/lib/api'
import { t } from '@/i18n'
import { useApplicationContextStore } from './applicationContext'

export type ApplicationSource = 'manual' | 'analysis'

/** « Mes candidatures » : une offre suivie, son statut et ses analyses, lettres et simulations. */
export const useApplicationsStore = defineStore('applications', () => {
  const context = useApplicationContextStore()
  const items = ref<Application[]>([])
  const loaded = ref(false)
  const loading = ref(false)
  const error = ref<string | null>(null)

  function apiMessage(err: any, fallback: string) {
    return err?.response?.data?.detail || fallback
  }

  function upsert(application: Application) {
    const index = items.value.findIndex((item) => item.id === application.id)
    if (index === -1) items.value.unshift(application)
    else items.value[index] = application
  }

  async function fetch() {
    loading.value = true
    error.value = null
    try {
      items.value = (await listApplications()).items
      loaded.value = true
    } catch (err: any) {
      error.value = apiMessage(err, t('applications.errors.load'))
    } finally {
      loading.value = false
    }
  }

  async function create(body: ApplicationInput & { comparison_id?: string | null }, source: ApplicationSource) {
    const created = await createApplication(body)
    upsert(created)
    posthog.capture('application_created', { source, status: created.status, has_offer_url: Boolean(created.offer_url) })
    return created
  }

  async function update(id: string, body: ApplicationInput): Promise<ApplicationDetail> {
    const previous = items.value.find((item) => item.id === id)?.status
    const updated = await updateApplication(id, body)
    upsert(updated)
    if (body.status && previous && body.status !== previous) {
      posthog.capture('application_status_changed', { from_status: previous, to_status: body.status })
    }
    // Intitulé affiché dans le contexte partagé
    if (context.applicationId === id) context.setApplication({ id, title: updated.title })
    return updated
  }

  const setStatus = (id: string, status: ApplicationStatus) => update(id, { status })

  async function remove(id: string) {
    await deleteApplication(id)
    items.value = items.value.filter((item) => item.id !== id)
    if (context.applicationId === id) context.setApplication(null)
  }

  /** Charge l'offre de la candidature dans le contexte partagé (le CV courant est conservé). */
  function select(application: ApplicationDetail) {
    context.useApplication({
      id: application.id,
      title: application.title,
      offerText: application.offer_text,
      offerUrl: application.offer_url,
    })
  }

  function reset() {
    items.value = []
    loaded.value = false
    error.value = null
  }

  return { items, loaded, loading, error, fetch, create, update, setStatus, remove, select, reset }
})
