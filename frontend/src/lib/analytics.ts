import posthog from 'posthog-js'

const token = import.meta.env.VITE_POSTHOG_PROJECT_TOKEN as string | undefined
const host = import.meta.env.VITE_POSTHOG_HOST as string | undefined

export const isAnalyticsConfigured = Boolean(token && host)

let initialized = false

export function initAnalytics() {
  if (initialized || !isAnalyticsConfigured || typeof window === 'undefined') {
    return isAnalyticsConfigured
  }

  posthog.init(token!, {
    api_host: host!,
    person_profiles: 'identified_only',
    capture_pageview: 'history_change',
    // Aucun cookie / localStorage tant que l’utilisateur n’a pas accepté ;
    // en cas de refus, tracking cookieless (hash côté serveur PostHog).
    cookieless_mode: 'on_reject',
  })

  initialized = true
  return true
}

export function getConsentStatus(): 'pending' | 'granted' | 'denied' | 'unavailable' {
  if (!isAnalyticsConfigured || !initialized) return 'unavailable'
  return posthog.get_explicit_consent_status()
}

export function acceptAnalytics() {
  if (!isAnalyticsConfigured || !initialized) return
  posthog.opt_in_capturing()
}

export function declineAnalytics() {
  if (!isAnalyticsConfigured || !initialized) return
  posthog.opt_out_capturing()
}

export function captureAnalyticsException(error: unknown) {
  if (!isAnalyticsConfigured || !initialized) return
  posthog.captureException(error)
}

export { posthog }
