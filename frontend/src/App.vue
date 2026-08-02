<template>
  <div
    class="relative flex min-h-screen flex-col font-sans antialiased"
    :class="isLanding ? 'bg-paper text-ink' : 'bg-background text-foreground'"
  >
    <!-- Overlay uniquement — ne jamais démonter RouterView (casse /auth/callback) -->
    <div
      v-if="authStore.loading"
      class="fixed inset-0 z-[100] flex items-center justify-center backdrop-blur-sm"
      :class="isLanding ? 'bg-paper/85' : 'bg-background/85'"
    >
      <div class="space-y-4 text-center font-mono">
        <div
          class="mx-auto h-8 w-8 animate-spin rounded-full border-2"
          :class="isLanding ? 'border-ink/20 border-t-ink' : 'border-muted border-t-foreground'"
        ></div>
        <p class="text-caption uppercase" :class="isLanding ? 'text-ink-soft' : 'text-muted-foreground'">
          Chargement de la session
        </p>
      </div>
    </div>

    <!-- En-tête applicatif (la landing gère sa propre navigation) -->
    <header
      v-if="!isLanding"
      class="sticky top-0 z-50 w-full border-b border-border bg-background/85 backdrop-blur-md"
    >
      <div class="mx-auto max-w-7xl px-5 sm:px-8">
        <div class="flex h-14 items-center justify-between font-mono text-caption uppercase">
          <a @click="handleLogoClick" class="group flex cursor-pointer items-center gap-2">
            <span class="h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
            <span class="tracking-wide transition-opacity group-hover:opacity-70">CV Offer Comparer</span>
          </a>

          <div class="hidden items-center gap-6 md:flex">
            <template v-if="authStore.isAuthenticated">
              <a
                v-for="link in appLinks"
                :key="link.path"
                @click="navigateTo(link.path)"
                class="cursor-pointer text-muted-foreground transition-colors hover:text-foreground"
                :class="{ 'text-foreground': route.path === link.path }"
              >
                {{ link.label }}
              </a>
            </template>

            <div class="flex items-center gap-3 border-l border-border pl-6">
              <button
                @click="toggleTheme"
                class="rounded p-1.5 text-muted-foreground transition-colors hover:text-foreground"
                title="Changer le thème"
              >
                <Sun v-if="isDark" class="h-3.5 w-3.5" />
                <Moon v-else class="h-3.5 w-3.5" />
              </button>

              <template v-if="!authStore.isAuthenticated">
                <a
                  @click="navigateTo('/login')"
                  class="cursor-pointer text-muted-foreground transition-colors hover:text-foreground"
                >
                  Connexion
                </a>
                <a
                  @click="navigateTo('/register')"
                  class="cursor-pointer rounded-full bg-foreground px-4 py-2 text-background transition-opacity hover:opacity-85"
                >
                  Commencer
                </a>
              </template>
              <UserMenu v-else />
            </div>
          </div>

          <div class="flex items-center gap-2 md:hidden">
            <button @click="toggleTheme" class="p-1.5 text-muted-foreground">
              <Sun v-if="isDark" class="h-4 w-4" />
              <Moon v-else class="h-4 w-4" />
            </button>
            <button @click="isMobileMenuOpen = !isMobileMenuOpen" class="p-1.5">
              <Menu v-if="!isMobileMenuOpen" class="h-5 w-5" />
              <X v-else class="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>

      <div
        v-if="isMobileMenuOpen"
        class="flex flex-col gap-3 border-b border-border px-5 py-4 font-mono text-caption uppercase md:hidden"
      >
        <template v-if="!authStore.isAuthenticated">
          <a @click="navigateTo('/login')" class="cursor-pointer text-muted-foreground">Connexion</a>
          <a @click="navigateTo('/register')" class="cursor-pointer">Commencer</a>
        </template>
        <template v-else>
          <a
            v-for="link in appLinks"
            :key="link.path"
            @click="navigateTo(link.path)"
            class="cursor-pointer text-muted-foreground"
          >
            {{ link.label }}
          </a>
          <a @click="navigateTo('/profile')" class="cursor-pointer text-muted-foreground">Profil</a>
          <a @click="handleSignOut" class="cursor-pointer text-destructive">Déconnexion</a>
        </template>
      </div>
    </header>

    <main class="flex-grow">
      <RouterView />
    </main>

    <footer v-if="!isLanding" class="border-t border-border py-8 font-mono text-micro uppercase">
      <div
        class="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 px-5 text-muted-foreground sm:flex-row sm:px-8"
      >
        <span>CV Offer Comparer — analyse ATS de précision</span>
        <span>© 2026 — Licence MIT</span>
        <div class="flex gap-5">
          <a href="mailto:rebeau.mickael@gmail.com" class="transition-colors hover:text-foreground">Contact</a>
          <a
            href="https://github.com/mickaelrebeau/CV-Offer-Comparer"
            target="_blank"
            rel="noopener"
            class="transition-colors hover:text-foreground"
          >
            GitHub
          </a>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'
import { Menu, X, Sun, Moon } from 'lucide-vue-next'
import UserMenu from '@/components/UserMenu.vue'
import { useTheme } from '@/composables/useTheme'
import { useAuthStore } from '@/stores/auth'

const { isDark, toggleTheme } = useTheme()
const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

const isMobileMenuOpen = ref(false)
const isLanding = computed(() => route.path === '/')

// La landing impose sa propre palette papier : le body doit suivre pour l'overscroll.
watch(
  isLanding,
  (landing) => {
    document.body.classList.toggle('landing-surface', landing)
  },
  { immediate: true },
)

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
