import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { nextTick } from 'vue'
import posthog from 'posthog-js'
import { STORAGE_KEYS } from '@/lib/storageKeys'
import {
  CONTEXT_VERSION,
  clearStoredApplicationContext,
  migrateContext,
  useApplicationContextStore,
} from '@/stores/applicationContext'

vi.mock('posthog-js', () => ({ default: { capture: vi.fn(), reset: vi.fn(), identify: vi.fn() } }))

const KEY = STORAGE_KEYS.applicationContext
const CV = 'Jane Doe\nDéveloppeuse Vue.js — 5 ans'
const OFFER = 'Nous recrutons un·e développeur·se front-end Vue 3 / TypeScript.'

const stored = () => JSON.parse(sessionStorage.getItem(KEY) ?? 'null')

function freshStore() {
  setActivePinia(createPinia())
  return useApplicationContextStore()
}

beforeEach(() => {
  sessionStorage.clear()
  localStorage.clear()
  vi.mocked(posthog.capture).mockClear()
})

describe('persistance', () => {
  it('écrit en sessionStorage, jamais en localStorage', async () => {
    const store = freshStore()
    store.setCv(CV, { fileName: 'cv.pdf', from: 'compare' })
    store.setOffer(OFFER, { from: 'compare' })
    await nextTick()

    expect(stored()).toMatchObject({
      version: CONTEXT_VERSION,
      cvText: CV,
      cvFileName: 'cv.pdf',
      offerText: OFFER,
      source: 'compare',
    })
    expect(stored().updatedAt).toEqual(expect.any(String))
    expect(localStorage.length).toBe(0)
  })

  it('ne garde pas de clé pour un contexte vide', async () => {
    const store = freshStore()
    store.setOffer(OFFER)
    await nextTick()
    store.setOffer('')
    await nextTick()
    expect(sessionStorage.getItem(KEY)).toBeNull()
  })

  it('oublie le nom de fichier et le CV enregistré quand le CV est saisi à la main', () => {
    const store = freshStore()
    store.setCv(CV, { fileName: 'cv.pdf', savedCvId: 'cv-1' })
    expect(store.savedCvId).toBe('cv-1')
    store.setCv(`${CV} (modifié)`)
    expect(store.cvFileName).toBeNull()
    expect(store.savedCvId).toBeNull()
  })

  it('persiste le lien vers le CV enregistré', async () => {
    const store = freshStore()
    store.setCv(CV, { fileName: 'CV Lead', savedCvId: 'cv-1' })
    await nextTick()
    expect(stored().savedCvId).toBe('cv-1')
    expect(freshStore().savedCvId).toBe('cv-1')
  })
})

describe('hydratation', () => {
  it('restaure le contexte après un rechargement', () => {
    sessionStorage.setItem(
      KEY,
      JSON.stringify({
        version: CONTEXT_VERSION,
        cvText: CV,
        cvFileName: 'cv.pdf',
        offerText: OFFER,
        offerUrl: 'https://example.com/job/1',
        updatedAt: '2026-10-06T10:00:00.000Z',
        source: 'interview',
      }),
    )
    const store = freshStore()
    expect(store.cvText).toBe(CV)
    expect(store.cvFileName).toBe('cv.pdf')
    expect(store.offerText).toBe(OFFER)
    expect(store.offerUrl).toBe('https://example.com/job/1')
    expect(store.source).toBe('interview')
    expect(store.isComplete).toBe(true)
  })

  it('ignore et supprime une valeur corrompue', () => {
    sessionStorage.setItem(KEY, '{pas du json')
    const store = freshStore()
    expect(store.hasContext).toBe(false)
    expect(sessionStorage.getItem(KEY)).toBeNull()
  })

  it('démarre vide sans valeur stockée', () => {
    const store = freshStore()
    expect(store.hasContext).toBe(false)
    expect(store.updatedAt).toBeNull()
  })
})

describe('migration', () => {
  it('reprend un contexte v0 (noms de champs des anciens stores)', () => {
    sessionStorage.setItem(KEY, JSON.stringify({ cvText: CV, jobText: OFFER }))
    const store = freshStore()
    expect(store.cvText).toBe(CV)
    expect(store.offerText).toBe(OFFER)
  })

  it('reprend les champs snake_case de l’API', () => {
    expect(migrateContext({ cv_text: CV, offer_text: OFFER, offer_url: ' ' })).toMatchObject({
      cvText: CV,
      offerText: OFFER,
      offerUrl: null,
    })
  })

  it('rejette une version inconnue ou un contenu invalide', () => {
    expect(migrateContext({ version: CONTEXT_VERSION + 1, cvText: CV })).toBeNull()
    expect(migrateContext({ version: CONTEXT_VERSION, cvText: '  ', offerText: '' })).toBeNull()
    expect(migrateContext(['cv'])).toBeNull()
    expect(migrateContext(null)).toBeNull()
  })

  it('normalise les types inattendus', () => {
    expect(migrateContext({ cvText: 42, offerText: OFFER, source: 'admin', cvFileName: {} })).toMatchObject({
      cvText: '',
      offerText: OFFER,
      source: null,
      cvFileName: null,
    })
  })

  it('réécrit le contexte migré au format courant à la première modification', async () => {
    sessionStorage.setItem(KEY, JSON.stringify({ cvText: CV, jobText: OFFER }))
    const store = freshStore()
    store.setOffer(`${OFFER} CDI.`)
    await nextTick()
    expect(stored()).toMatchObject({ version: CONTEXT_VERSION, offerText: `${OFFER} CDI.` })
    expect(stored().jobText).toBeUndefined()
  })
})

describe('purge', () => {
  it('clear() vide le store et le sessionStorage', async () => {
    const store = freshStore()
    store.setContext({ cvText: CV, offerText: OFFER }, 'compare')
    await nextTick()
    store.clear()
    await nextTick()
    expect(store.hasContext).toBe(false)
    expect(store.source).toBeNull()
    expect(sessionStorage.getItem(KEY)).toBeNull()
  })

  it('clearStoredApplicationContext() purge sans instancier le store', () => {
    sessionStorage.setItem(KEY, JSON.stringify({ version: CONTEXT_VERSION, cvText: CV, offerText: OFFER }))
    clearStoredApplicationContext()
    expect(sessionStorage.getItem(KEY)).toBeNull()
  })

  it('la déconnexion et la suppression du compte purgent le contexte', async () => {
    vi.doMock('@/lib/api', () => ({ api: { delete: vi.fn().mockResolvedValue({}) }, getApiBaseURL: () => '' }))
    const { useAuthStore } = await import('@/stores/auth')

    for (const action of ['signOut', 'deleteAccount'] as const) {
      const context = freshStore()
      context.setContext({ cvText: CV, offerText: OFFER }, 'compare')
      await nextTick()
      await useAuthStore()[action]()
      expect(context.hasContext).toBe(false)
      expect(sessionStorage.getItem(KEY)).toBeNull()
    }
    vi.doUnmock('@/lib/api')
  })
})

describe('analytics', () => {
  it('signale la réutilisation entre modules sans contenu du CV', () => {
    const store = freshStore()
    store.setContext({ cvText: CV, offerText: OFFER }, 'compare')
    store.trackReuse('interview')

    expect(posthog.capture).toHaveBeenCalledWith('context_reused', {
      source_module: 'compare',
      target_module: 'interview',
      has_cv: true,
      has_offer: true,
    })
    const payload = JSON.stringify(vi.mocked(posthog.capture).mock.calls)
    expect(payload).not.toContain('Jane')
    expect(payload).not.toContain('Vue 3')
  })

  it('ne signale rien dans le module source ou sans contexte', () => {
    const store = freshStore()
    store.trackReuse('coverLetter')
    store.setContext({ cvText: CV, offerText: OFFER }, 'coverLetter')
    store.trackReuse('coverLetter')
    expect(posthog.capture).not.toHaveBeenCalled()
  })
})
