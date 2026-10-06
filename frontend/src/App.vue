<template>
  <div class="relative flex min-h-screen flex-col bg-paper font-sans text-ink antialiased">
    <a
      href="#main-content"
      class="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[110] focus:rounded-lg focus:bg-ink focus:px-4 focus:py-2 focus:font-mono focus:text-caption focus:uppercase focus:text-paper"
    >
      {{ t('nav.skipToContent') }}
    </a>
    <div
      v-if="authStore.loading"
      class="fixed inset-0 z-[100] flex items-center justify-center bg-paper/85 backdrop-blur-sm"
      role="status"
      aria-live="polite"
    >
      <div class="space-y-4 text-center font-mono">
        <div class="mx-auto h-8 w-8 animate-spin rounded-full border-2 border-ink/20 border-t-ink" aria-hidden="true"></div>
        <p class="text-caption uppercase text-ink-soft">{{ t('session.loading') }}</p>
      </div>
    </div>

    <header
      v-if="!isLanding"
      class="sticky top-0 z-50 border-b border-ink/10 bg-paper/90 backdrop-blur-md"
    >
      <div class="mx-auto flex h-14 max-w-[100rem] items-center justify-between px-5 sm:px-8 lg:px-16">
        <RouterLink
          :to="localePath(authStore.isAuthenticated ? '/dashboard' : '/')"
          :aria-label="t('nav.homeAria')"
          class="group transition-opacity hover:opacity-70"
        >
          <BrandLogo tag="span" size="sm" />
        </RouterLink>

        <nav :aria-label="t('nav.primary')" class="hidden items-center gap-6 font-mono text-caption uppercase md:flex">
          <template v-if="authStore.isAuthenticated">
            <RouterLink
              v-for="link in appLinks"
              :key="link.path"
              :to="localePath(link.path)"
              class="transition-colors"
              :class="currentPath === link.path ? 'text-ink' : 'text-ink-soft hover:text-ink'"
            >
              {{ t(link.label) }}
            </RouterLink>
          </template>
        </nav>

        <div class="flex items-center gap-3">
          <template v-if="!authStore.isAuthenticated">
            <RouterLink
              :to="localePath('/login')"
              class="hidden font-mono text-caption uppercase text-ink-soft transition-colors hover:text-ink sm:block"
            >
              {{ t('nav.login') }}
            </RouterLink>
            <RouterLink :to="localePath('/register')" class="btn-primary !h-9 !px-4 !text-micro">
              {{ t('nav.getStarted') }}
            </RouterLink>
          </template>
          <UserMenu v-else />
          <InstallAppButton class="hidden md:inline-flex" />
          <LanguageSwitcher class="hidden md:flex" />
          <button
            type="button"
            class="p-1.5 md:hidden"
            :aria-label="isMobileMenuOpen ? t('nav.closeMenu') : t('nav.openMenu')"
            :aria-expanded="isMobileMenuOpen"
            aria-controls="mobile-menu"
            @click="isMobileMenuOpen = !isMobileMenuOpen"
          >
            <Menu v-if="!isMobileMenuOpen" class="h-5 w-5" aria-hidden="true" />
            <X v-else class="h-5 w-5" aria-hidden="true" />
          </button>
        </div>
      </div>

      <nav
        v-if="isMobileMenuOpen"
        id="mobile-menu"
        :aria-label="t('nav.mobile')"
        class="flex flex-col items-start gap-3 border-t border-ink/10 px-5 py-4 font-mono text-caption uppercase md:hidden"
      >
        <template v-if="!authStore.isAuthenticated">
          <RouterLink :to="localePath('/login')" class="text-ink-soft">{{ t('nav.login') }}</RouterLink>
          <RouterLink :to="localePath('/register')" class="text-ink">{{ t('nav.getStarted') }}</RouterLink>
        </template>
        <template v-else>
          <RouterLink
            v-for="link in appLinks"
            :key="link.path"
            :to="localePath(link.path)"
            :class="currentPath === link.path ? 'text-ink' : 'text-ink-soft'"
          >
            {{ t(link.label) }}
          </RouterLink>
          <RouterLink :to="localePath('/profile')" class="text-ink-soft">{{ t('nav.profile') }}</RouterLink>
          <button type="button" class="uppercase text-rose-700" @click="handleSignOut">{{ t('nav.signOut') }}</button>
        </template>
        <InstallAppButton />
        <LanguageSwitcher />
      </nav>
    </header>

    <EmailVerificationBanner />

    <main id="main-content" tabindex="-1" class="flex-grow focus:outline-none">
      <RouterView />
    </main>

    <CookieConsentBanner />
    <OfflineBanner />

    <footer v-if="!isLanding" class="border-t border-ink/10 py-8 font-mono text-micro uppercase">
      <div class="mx-auto flex max-w-[100rem] flex-col items-center justify-between gap-4 px-5 text-ink-soft sm:flex-row sm:px-8 lg:px-16">
        <span>{{ t('nav.footerTagline') }}</span>
        <span>{{ t('nav.footerLicense') }}</span>
        <div class="flex flex-wrap justify-center gap-5">
          <RouterLink :to="localePath('/mentions-legales')" class="transition-colors hover:text-ink">{{ t('nav.legalNotice') }}</RouterLink>
          <RouterLink :to="localePath('/cgv')" class="transition-colors hover:text-ink">{{ t('nav.terms') }}</RouterLink>
          <RouterLink :to="localePath('/confidentialite')" class="transition-colors hover:text-ink">{{ t('nav.privacy') }}</RouterLink>
          <a href="mailto:rebeau.mickael@gmail.com" class="transition-colors hover:text-ink">{{ t('nav.contact') }}</a>
          <a
            href="https://github.com/mickaelrebeau/CV-Offer-Comparer"
            target="_blank"
            rel="noopener"
            class="transition-colors hover:text-ink"
          >
            GitHub
          </a>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink, RouterView, useRoute } from 'vue-router'
import { Menu, X } from 'lucide-vue-next'
import BrandLogo from '@/components/BrandLogo.vue'
import CookieConsentBanner from '@/components/CookieConsentBanner.vue'
import EmailVerificationBanner from '@/components/EmailVerificationBanner.vue'
import InstallAppButton from '@/components/InstallAppButton.vue'
import LanguageSwitcher from '@/components/LanguageSwitcher.vue'
import OfflineBanner from '@/components/OfflineBanner.vue'
import UserMenu from '@/components/UserMenu.vue'
import { useAuthStore } from '@/stores/auth'
import { useSavedCvsStore } from '@/stores/savedCvs'
import { usePageSeo } from '@/composables/usePageSeo'
import { stripLocale } from '@/i18n/routing'
import { useLocale } from '@/i18n/useLocale'
import { isOnline } from '@/lib/pwa'

const { t } = useI18n()
const { localePath, push } = useLocale()
const authStore = useAuthStore()
const savedCvs = useSavedCvsStore()
const route = useRoute()

const isMobileMenuOpen = ref(false)
// Chemin sans préfixe de langue (/en/compare → /compare)
const currentPath = computed(() => stripLocale(route.path))
const isLanding = computed(() => currentPath.value === '/')

usePageSeo(
  computed(() => ({
    title: route.meta.seo ? t(`seo.${route.meta.seo}.title`) : undefined,
    description: route.meta.seo ? t(`seo.${route.meta.seo}.description`) : undefined,
    path: route.path,
    // La home gère son propre JSON-LD ; les espaces connectés restent hors index.
    noindex: Boolean(route.meta.noindex || route.meta.requiresAuth),
  })),
)

watch(
  () => route.path,
  () => {
    isMobileMenuOpen.value = false
  },
)

// Connexion (ou session restaurée) : le CV par défaut de « Mes CV » rejoint le contexte partagé
watch(
  () => authStore.isAuthenticated,
  (authenticated) => {
    if (authenticated) savedCvs.preloadDefault()
  },
  { immediate: true },
)

// Session gardée hors ligne : la revérifier dès le retour du réseau
watch(isOnline, (online) => {
  if (online && authStore.sessionUnverified) authStore.getCurrentUser()
})

const appLinks = [
  { path: '/dashboard', label: 'nav.dashboard' },
  { path: '/compare', label: 'nav.compare' },
  { path: '/interview-simulator', label: 'nav.simulator' },
  { path: '/cover-letter', label: 'nav.coverLetter' },
]

const handleSignOut = async () => {
  await authStore.signOut()
  push('/')
  isMobileMenuOpen.value = false
}

// Auth initialisée dans le beforeEach de main.ts (avant le mount).
</script>
