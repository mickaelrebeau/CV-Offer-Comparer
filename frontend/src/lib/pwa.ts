import { readonly, ref } from 'vue'

type BeforeInstallPromptEvent = Event & {
  prompt: () => Promise<void>
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>
}

const installEvent = ref<BeforeInstallPromptEvent | null>(null)
const installable = ref(false)
const online = ref(true)

/** L'app peut être installée (Chromium desktop / Android) : `beforeinstallprompt` reçu. */
export const canInstall = readonly(installable)
export const isOnline = readonly(online)

/**
 * À appeler une fois, côté client, au démarrage : les événements `beforeinstallprompt`
 * et `online`/`offline` peuvent survenir avant le montage des composants.
 */
export function initPwa() {
  online.value = navigator.onLine
  window.addEventListener('online', () => (online.value = true))
  window.addEventListener('offline', () => (online.value = false))

  window.addEventListener('beforeinstallprompt', (event) => {
    // Pas de mini-barre native : l'app propose son propre bouton « Installer »
    event.preventDefault()
    installEvent.value = event as BeforeInstallPromptEvent
    installable.value = true
  })
  window.addEventListener('appinstalled', () => {
    installEvent.value = null
    installable.value = false
  })

  // Service worker uniquement en production (en dev, Vite sert des modules non versionnés)
  if (import.meta.env.PROD && 'serviceWorker' in navigator) {
    const register = () =>
      navigator.serviceWorker.register('/sw.js').catch((error) => {
        console.warn('[PWA] enregistrement du service worker impossible', error)
      })
    // Script chargé en async : `load` a pu déjà avoir lieu
    if (document.readyState === 'complete') register()
    else window.addEventListener('load', register, { once: true })
  }
}

/** Affiche l'invite d'installation native. Renvoie true si l'utilisateur accepte. */
export async function promptInstall(): Promise<boolean> {
  const event = installEvent.value
  if (!event) return false
  await event.prompt()
  const { outcome } = await event.userChoice
  installEvent.value = null
  installable.value = false
  return outcome === 'accepted'
}
