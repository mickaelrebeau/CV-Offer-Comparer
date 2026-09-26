<template>
  <div class="relative flex min-h-screen flex-col bg-paper font-sans text-ink antialiased">
    <a
      href="#main-content"
      class="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[110] focus:rounded-lg focus:bg-ink focus:px-4 focus:py-2 focus:font-mono focus:text-caption focus:uppercase focus:text-paper"
    >
      Aller au contenu
    </a>
    <div
      v-if="authStore.loading"
      class="fixed inset-0 z-[100] flex items-center justify-center bg-paper/85 backdrop-blur-sm"
      role="status"
      aria-live="polite"
    >
      <div class="space-y-4 text-center font-mono">
        <div class="mx-auto h-8 w-8 animate-spin rounded-full border-2 border-ink/20 border-t-ink" aria-hidden="true"></div>
        <p class="text-caption uppercase text-ink-soft">Chargement de la session</p>
      </div>
    </div>

    <header
      v-if="!isLanding"
      class="sticky top-0 z-50 border-b border-ink/10 bg-paper/90 backdrop-blur-md"
    >
      <div class="mx-auto flex h-14 max-w-[100rem] items-center justify-between px-5 sm:px-8 lg:px-16">
        <RouterLink
          :to="authStore.isAuthenticated ? '/dashboard' : '/'"
          aria-label="Talento — accueil"
          class="group transition-opacity hover:opacity-70"
        >
          <BrandLogo tag="span" size="sm" />
        </RouterLink>

        <nav aria-label="Navigation principale" class="hidden items-center gap-6 font-mono text-caption uppercase md:flex">
          <template v-if="authStore.isAuthenticated">
            <RouterLink
              v-for="link in appLinks"
              :key="link.path"
              :to="link.path"
              class="transition-colors"
              :class="route.path === link.path ? 'text-ink' : 'text-ink-soft hover:text-ink'"
            >
              {{ link.label }}
            </RouterLink>
          </template>
        </nav>

        <div class="flex items-center gap-3">
          <template v-if="!authStore.isAuthenticated">
            <RouterLink
              to="/login"
              class="hidden font-mono text-caption uppercase text-ink-soft transition-colors hover:text-ink sm:block"
            >
              Connexion
            </RouterLink>
            <RouterLink to="/register" class="btn-primary !h-9 !px-4 !text-micro">
              Commencer
            </RouterLink>
          </template>
          <UserMenu v-else />
          <button
            type="button"
            class="p-1.5 md:hidden"
            :aria-label="isMobileMenuOpen ? 'Fermer le menu' : 'Ouvrir le menu'"
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
        aria-label="Navigation mobile"
        class="flex flex-col items-start gap-3 border-t border-ink/10 px-5 py-4 font-mono text-caption uppercase md:hidden"
      >
        <template v-if="!authStore.isAuthenticated">
          <RouterLink to="/login" class="text-ink-soft">Connexion</RouterLink>
          <RouterLink to="/register" class="text-ink">Commencer</RouterLink>
        </template>
        <template v-else>
          <RouterLink
            v-for="link in appLinks"
            :key="link.path"
            :to="link.path"
            :class="route.path === link.path ? 'text-ink' : 'text-ink-soft'"
          >
            {{ link.label }}
          </RouterLink>
          <RouterLink to="/profile" class="text-ink-soft">Profil</RouterLink>
          <button type="button" class="uppercase text-rose-700" @click="handleSignOut">Déconnexion</button>
        </template>
      </nav>
    </header>

    <EmailVerificationBanner />

    <main id="main-content" tabindex="-1" class="flex-grow focus:outline-none">
      <RouterView />
    </main>

    <CookieConsentBanner />

    <footer v-if="!isLanding" class="border-t border-ink/10 py-8 font-mono text-micro uppercase">
      <div class="mx-auto flex max-w-[100rem] flex-col items-center justify-between gap-4 px-5 text-ink-soft sm:flex-row sm:px-8 lg:px-16">
        <span>Talento — analyse ATS de précision</span>
        <span>© 2026 — Licence MIT</span>
        <div class="flex flex-wrap justify-center gap-5">
          <RouterLink to="/mentions-legales" class="transition-colors hover:text-ink">Mentions légales</RouterLink>
          <RouterLink to="/cgv" class="transition-colors hover:text-ink">CGV</RouterLink>
          <RouterLink to="/confidentialite" class="transition-colors hover:text-ink">Confidentialité</RouterLink>
          <a href="mailto:rebeau.mickael@gmail.com" class="transition-colors hover:text-ink">Contact</a>
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
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'
import { Menu, X } from 'lucide-vue-next'
import BrandLogo from '@/components/BrandLogo.vue'
import CookieConsentBanner from '@/components/CookieConsentBanner.vue'
import EmailVerificationBanner from '@/components/EmailVerificationBanner.vue'
import UserMenu from '@/components/UserMenu.vue'
import { useAuthStore } from '@/stores/auth'
import { usePageSeo } from '@/composables/usePageSeo'
import { SITE_DESCRIPTION } from '@/lib/site'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

const isMobileMenuOpen = ref(false)
const isLanding = computed(() => route.path === '/')

usePageSeo(
  computed(() => ({
    title: typeof route.meta.title === 'string' ? route.meta.title : undefined,
    description:
      typeof route.meta.description === 'string' ? route.meta.description : SITE_DESCRIPTION,
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

const appLinks = [
  { path: '/dashboard', label: 'Tableau de bord' },
  { path: '/compare', label: 'Comparateur' },
  { path: '/interview-simulator', label: 'Simulateur' },
]

const handleSignOut = async () => {
  await authStore.signOut()
  router.push('/')
  isMobileMenuOpen.value = false
}

// Auth initialisée dans le beforeEach de main.ts (avant le mount).
</script>
