import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import posthog from 'posthog-js'
import * as api from '@/lib/api'
import type { SavedCv, SavedCvListing } from '@/lib/api'
import { useApplicationContextStore } from '@/stores/applicationContext'
import { useSavedCvsStore } from '@/stores/savedCvs'

vi.mock('posthog-js', () => ({ default: { capture: vi.fn(), reset: vi.fn(), identify: vi.fn() } }))
vi.mock('@/lib/api', () => ({
  listSavedCvs: vi.fn(),
  getSavedCv: vi.fn(),
  createSavedCv: vi.fn(),
  updateSavedCv: vi.fn(),
  setDefaultSavedCv: vi.fn(),
  deleteSavedCv: vi.fn(),
}))

const FRONT_TEXT = 'Jane Doe — Développeuse front Vue.js'
const LEAD_TEXT = 'Jane Doe — Lead technique'

function cv(overrides: Partial<SavedCv>): SavedCv {
  return {
    id: 'cv-front',
    label: 'CV Dev Front',
    source_filename: 'cv-front.pdf',
    is_default: true,
    char_count: FRONT_TEXT.length,
    excerpt: FRONT_TEXT,
    created_at: '2026-10-01T10:00:00Z',
    updated_at: '2026-10-01T10:00:00Z',
    ...overrides,
  }
}

const FRONT = cv({})
const LEAD = cv({ id: 'cv-lead', label: 'CV Lead', source_filename: null, is_default: false })
const listing = (items: SavedCv[]): SavedCvListing => ({
  items,
  default_id: items.find((item) => item.is_default)?.id ?? null,
  limit: 5,
})

function setup() {
  setActivePinia(createPinia())
  return { store: useSavedCvsStore(), context: useApplicationContextStore() }
}

const capturedPayloads = () => JSON.stringify(vi.mocked(posthog.capture).mock.calls)

beforeEach(() => {
  sessionStorage.clear()
  vi.clearAllMocks()
  vi.mocked(api.listSavedCvs).mockResolvedValue(listing([FRONT, LEAD]))
  vi.mocked(api.getSavedCv).mockImplementation(async (id) => ({
    ...(id === FRONT.id ? FRONT : LEAD),
    text: id === FRONT.id ? FRONT_TEXT : LEAD_TEXT,
  }))
})

describe('liste', () => {
  it('charge la liste une seule fois, sauf rafraîchissement forcé', async () => {
    const { store } = setup()
    await Promise.all([store.fetch(), store.fetch()])
    await store.fetch()
    expect(api.listSavedCvs).toHaveBeenCalledTimes(1)
    expect(store.defaultCv?.id).toBe(FRONT.id)
    await store.fetch(true)
    expect(api.listSavedCvs).toHaveBeenCalledTimes(2)
  })

  it('expose la limite atteinte', async () => {
    vi.mocked(api.listSavedCvs).mockResolvedValue({ ...listing([FRONT, LEAD]), limit: 2 })
    const { store } = setup()
    await store.fetch()
    expect(store.limitReached).toBe(true)
  })

  it('garde un message en cas d’échec (hors ligne)', async () => {
    vi.mocked(api.listSavedCvs).mockRejectedValue(new Error('Network Error'))
    const { store } = setup()
    await store.fetch()
    expect(store.loaded).toBe(false)
    expect(store.error).toBeTruthy()
  })
})

describe('sélection', () => {
  it('charge le CV dans le contexte partagé et le garde en cache', async () => {
    const { store, context } = setup()
    await store.fetch()
    await store.select(LEAD.id, 'interview')

    expect(context.cvText).toBe(LEAD_TEXT)
    expect(context.savedCvId).toBe(LEAD.id)
    expect(context.cvFileName).toBe('CV Lead')
    expect(context.source).toBe('interview')

    await store.select(LEAD.id, 'coverLetter')
    expect(api.getSavedCv).toHaveBeenCalledTimes(1)
    expect(store.isCached(LEAD.id)).toBe(true)
  })

  it('envoie cv_selected sans contenu', async () => {
    const { store } = setup()
    await store.fetch()
    await store.select(FRONT.id, 'compare')
    expect(posthog.capture).toHaveBeenCalledWith('cv_selected', {
      module: 'compare',
      is_default: true,
      saved_cv_count: 2,
    })
    expect(capturedPayloads()).not.toContain('Jane')
    expect(capturedPayloads()).not.toContain('CV Dev Front')
  })

  it('une édition manuelle détache le CV enregistré', async () => {
    const { store, context } = setup()
    await store.fetch()
    await store.select(FRONT.id, 'compare')
    context.setCv(`${FRONT_TEXT} (retouché)`, { from: 'compare' })
    expect(context.savedCvId).toBeNull()
  })
})

describe('enregistrement', () => {
  it('crée le CV et envoie cv_saved sans contenu', async () => {
    vi.mocked(api.createSavedCv).mockResolvedValue({ ...FRONT, text: FRONT_TEXT })
    const { store } = setup()
    await store.create({ label: 'CV Dev Front', text: FRONT_TEXT, sourceFilename: 'cv-front.pdf' }, 'compare')

    expect(api.createSavedCv).toHaveBeenCalledWith({
      label: 'CV Dev Front',
      text: FRONT_TEXT,
      source_filename: 'cv-front.pdf',
      is_default: false,
    })
    expect(posthog.capture).toHaveBeenCalledWith('cv_saved', {
      origin: 'compare',
      is_default: true,
      has_source_file: true,
      saved_cv_count: 2,
    })
    expect(capturedPayloads()).not.toContain('Jane')
    expect(capturedPayloads()).not.toContain('cv-front.pdf')
  })

  it('propage l’erreur de limite de l’API', async () => {
    const error = Object.assign(new Error('409'), {
      response: { status: 409, data: { code: 'cvs.limit_reached', detail: 'Limite atteinte' } },
    })
    vi.mocked(api.createSavedCv).mockRejectedValue(error)
    const { store } = setup()
    await expect(store.create({ label: 'Extra', text: FRONT_TEXT }, 'profile')).rejects.toBe(error)
    expect(posthog.capture).not.toHaveBeenCalled()
  })
})

describe('gestion', () => {
  it('remplacer un CV suivi par le contexte met le contexte à jour', async () => {
    vi.mocked(api.updateSavedCv).mockResolvedValue({ ...FRONT, source_filename: 'cv-v2.pdf', text: 'CV v2' })
    const { store, context } = setup()
    await store.fetch()
    await store.select(FRONT.id, 'compare')
    await store.replace(FRONT.id, 'CV v2', 'cv-v2.pdf')

    expect(context.cvText).toBe('CV v2')
    expect(context.cvFileName).toBe('CV Dev Front')
    expect(context.savedCvId).toBe(FRONT.id)
  })

  it('supprimer le CV suivi garde le texte mais le détache', async () => {
    vi.mocked(api.deleteSavedCv).mockResolvedValue(listing([{ ...LEAD, is_default: true }]))
    const { store, context } = setup()
    await store.fetch()
    await store.select(FRONT.id, 'compare')
    await store.remove(FRONT.id)

    expect(context.cvText).toBe(FRONT_TEXT)
    expect(context.savedCvId).toBeNull()
    expect(store.isCached(FRONT.id)).toBe(false)
    expect(store.defaultCv?.id).toBe(LEAD.id)
  })
})

describe('pré-chargement à la connexion', () => {
  it('charge le CV par défaut quand le contexte n’a pas de CV', async () => {
    const { store, context } = setup()
    await store.preloadDefault()
    expect(context.cvText).toBe(FRONT_TEXT)
    expect(context.savedCvId).toBe(FRONT.id)
    expect(context.cvFileName).toBe('CV Dev Front')
  })

  it('n’écrase jamais un CV déjà en contexte', async () => {
    const { store, context } = setup()
    context.setCv('CV saisi à la main', { from: 'compare' })
    await store.preloadDefault()
    expect(context.cvText).toBe('CV saisi à la main')
    expect(api.listSavedCvs).not.toHaveBeenCalled()
  })

  it('ne fait rien sans CV par défaut ou hors ligne', async () => {
    vi.mocked(api.listSavedCvs).mockResolvedValue(listing([]))
    const { store, context } = setup()
    await store.preloadDefault()
    expect(context.hasCv).toBe(false)

    vi.mocked(api.listSavedCvs).mockRejectedValue(new Error('Network Error'))
    const offline = setup()
    await expect(offline.store.preloadDefault()).resolves.toBeUndefined()
    expect(offline.context.hasCv).toBe(false)
  })
})

describe('purge', () => {
  it('reset() vide la liste et les textes en mémoire', async () => {
    const { store } = setup()
    await store.fetch()
    await store.loadText(FRONT.id)
    store.reset()
    expect(store.items).toEqual([])
    expect(store.loaded).toBe(false)
    expect(store.isCached(FRONT.id)).toBe(false)
  })

  it('la déconnexion purge la bibliothèque en mémoire', async () => {
    const { store } = setup()
    await store.fetch()
    await store.loadText(FRONT.id)
    const { useAuthStore } = await import('@/stores/auth')
    await useAuthStore().signOut()
    expect(store.items).toEqual([])
    expect(store.isCached(FRONT.id)).toBe(false)
  })
})
