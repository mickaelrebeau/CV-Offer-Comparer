<template>
  <div class="relative flex min-h-screen flex-col bg-paper font-sans text-ink antialiased">
    <div
      v-if="authStore.loading"
      class="fixed inset-0 z-[100] flex items-center justify-center bg-paper/85 backdrop-blur-sm"
    >
      <div class="space-y-4 text-center font-mono">
        <div class="mx-auto h-8 w-8 animate-spin rounded-full border-2 border-ink/20 border-t-ink"></div>
        <p class="text-caption uppercase text-ink-soft">Chargement de la session</p>
      </div>
    </div>

    <header
      v-if="!isLanding"
      class="sticky top-0 z-50 border-b border-ink/10 bg-paper/90 backdrop-blur-md"
    >
      <div class="mx-auto flex h-14 max-w-[100rem] items-center justify-between px-5 sm:px-8 lg:px-16">
        <a @click="handleLogoClick" class="group flex cursor-pointer items-center gap-2 font-mono text-caption uppercase">
          <span class="h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
          <span class="tracking-wide transition-opacity group-hover:opacity-70">CV Offer Comparer</span>
        </a>

        <nav class="hidden items-center gap-6 font-mono text-caption uppercase md:flex">
          <template v-if="authStore.isAuthenticated">
            <a
              v-for="link in appLinks"
              :key="link.path"
              @click="navigateTo(link.path)"
              class="cursor-pointer transition-colors"
              :class="route.path === link.path ? 'text-ink' : 'text-ink-soft hover:text-ink'"
            >
              {{ link.label }}
            </a>
          </template>
        </nav>

        <div class="flex items-center gap-3">
          <template v-if="!authStore.isAuthenticated">
            <a
              @click="navigateTo('/login')"
              class="hidden cursor-pointer font-mono text-caption uppercase text-ink-soft transition-colors hover:text-ink sm:block"
            >
              Connexion
            </a>
            <a @click="navigateTo('/register')" class="btn-primary !h-9 !px-4 !text-micro">
              Commencer
            </a>
          </template>
          <UserMenu v-else />
          <button @click="isMobileMenuOpen = !isMobileMenuOpen" class="p-1.5 md:hidden">
            <Menu v-if="!isMobileMenuOpen" class="h-5 w-5" />
            <X v-else class="h-5 w-5" />
          </button>
        </div>
      </div>

      <div
        v-if="isMobileMenuOpen"
        class="flex flex-col gap-3 border-t border-ink/10 px-5 py-4 font-mono text-caption uppercase md:hidden"
      >
        <template v-if="!authStore.isAuthenticated">
          <a @click="navigateTo('/login')" class="cursor-pointer text-ink-soft">Connexion</a>
          <a @click="navigateTo('/register')" class="cursor-pointer text-ink">Commencer</a>
        </template>
        <template v-else>
          <a
            v-for="link in appLinks"
            :key="link.path"
            @click="navigateTo(link.path)"
            class="cursor-pointer text-ink-soft"
          >
            {{ link.label }}
          </a>
          <a @click="navigateTo('/profile')" class="cursor-pointer text-ink-soft">Profil</a>
          <a @click="handleSignOut" class="cursor-pointer text-rose-600">Déconnexion</a>
        </template>
      </div>
    </header>

    <main class="flex-grow">
      <RouterView />
    </main>

    <footer v-if="!isLanding" class="border-t border-ink/10 py-8 font-mono text-micro uppercase">
      <div class="mx-auto flex max-w-[100rem] flex-col items-center justify-between gap-4 px-5 text-ink-soft sm:flex-row sm:px-8 lg:px-16">
        <span>CV Offer Comparer — analyse ATS de précision</span>
        <span>© 2026 — Licence MIT</span>
        <div class="flex gap-5">
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
import { ref, computed, onMounted } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'
import { Menu, X } from 'lucide-vue-next'
import UserMenu from '@/components/UserMenu.vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

const isMobileMenuOpen = ref(false)
const isLanding = computed(() => route.path === '/')

const appLinks = [
  { path: '/dashboard', label: 'Tableau de bord' },
  { path: '/compare', label: 'Comparateur' },
  { path: '/interview-simulator', label: 'Simulateur' },
]

const navigateTo = (path: string) => {
  router.push(path)
  isMobileMenuOpen.value = false
}

const handleLogoClick = () => {
  router.push(authStore.isAuthenticated ? '/dashboard' : '/')
  isMobileMenuOpen.value = false
}

const handleSignOut = async () => {
  await authStore.signOut()
  router.push('/')
  isMobileMenuOpen.value = false
}

onMounted(async () => {
  await authStore.initializeAuth()
})
</script>
