<template>
  <div class="min-h-screen bg-background text-foreground relative flex flex-col font-sans selection:bg-brand-500/20 selection:text-brand-500">
    <!-- Ambient Background Radial Blurs -->
    <div class="fixed inset-0 overflow-hidden pointer-events-none z-0">
      <div class="absolute -top-40 left-1/2 -translate-x-1/2 w-[1000px] h-[500px] bg-gradient-to-b from-indigo-500/10 via-purple-500/5 to-transparent blur-[120px] rounded-full"></div>
    </div>

    <!-- Global Loading Spinner -->
    <div v-if="authStore.loading" class="flex items-center justify-center min-h-screen relative z-50">
      <div class="text-center space-y-4">
        <div class="w-10 h-10 border-2 border-brand-500/20 border-t-brand-500 rounded-full animate-spin mx-auto"></div>
        <p class="text-sm text-muted-foreground font-medium tracking-wide">Chargement de votre session...</p>
      </div>
    </div>

    <div v-else class="relative z-10 flex flex-col min-h-screen">
      <!-- Fixed Glass Navigation Header -->
      <header class="fixed top-0 w-full z-50 transition-all duration-300 glass-header border-b border-zinc-200/50 dark:border-zinc-800/50" id="navbar">
        <div class="max-w-7xl mx-auto px-6 lg:px-8">
          <div class="flex items-center justify-between h-16">
            <!-- Brand Logo -->
            <a @click="handleLogoClick" class="cursor-pointer flex items-center gap-2.5 group">
              <div class="w-8 h-8 rounded-lg bg-zinc-900 dark:bg-zinc-100 text-zinc-100 dark:text-zinc-900 flex items-center justify-center font-bold text-xs shadow-sm group-hover:scale-105 transition-transform">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
                  <polyline points="14 2 14 8 20 8" />
                  <line x1="16" y1="13" x2="8" y2="13" />
                  <line x1="16" y1="17" x2="8" y2="17" />
                </svg>
              </div>
              <span class="font-bold text-sm tracking-tight text-foreground group-hover:text-brand-500 transition-colors">
                CV Offer Comparer
              </span>
            </a>

            <!-- Desktop Menu Navigation -->
            <div class="hidden md:flex items-center gap-8">
              <template v-if="!authStore.isAuthenticated">
                <a href="#features" class="text-xs font-medium uppercase tracking-wider text-muted-foreground hover:text-foreground transition-colors">Fonctionnalités</a>
                <a href="#architecture" class="text-xs font-medium uppercase tracking-wider text-muted-foreground hover:text-foreground transition-colors">Démonstration</a>
                <a href="#how-it-works" class="text-xs font-medium uppercase tracking-wider text-muted-foreground hover:text-foreground transition-colors">Méthode</a>
              </template>
              <template v-else>
                <a @click="navigateTo('/dashboard')" class="text-xs font-medium uppercase tracking-wider text-muted-foreground hover:text-foreground transition-colors cursor-pointer" :class="{ 'text-foreground font-semibold': route.path === '/dashboard' }">
                  Tableau de bord
                </a>
                <a @click="navigateTo('/compare')" class="text-xs font-medium uppercase tracking-wider text-muted-foreground hover:text-foreground transition-colors cursor-pointer" :class="{ 'text-foreground font-semibold': route.path === '/compare' }">
                  Comparateur
                </a>
                <a @click="navigateTo('/interview-simulator')" class="text-xs font-medium uppercase tracking-wider text-muted-foreground hover:text-foreground transition-colors cursor-pointer" :class="{ 'text-foreground font-semibold': route.path === '/interview-simulator' }">
                  Simulateur
                </a>
              </template>

              <!-- Actions & Theme Toggle -->
              <div class="flex items-center gap-3 pl-4 border-l border-zinc-200 dark:border-zinc-800">
                <!-- Dark / Light Mode Toggle Button -->
                <button @click="toggleTheme" class="p-2 rounded-full text-muted-foreground hover:text-foreground hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors" title="Changer le thème">
                  <Sun v-if="isDark" class="w-4 h-4 text-amber-400" />
                  <Moon v-else class="w-4 h-4 text-zinc-700" />
                </button>

                <template v-if="!authStore.isAuthenticated">
                  <a @click="navigateTo('/login')" class="text-xs font-medium text-foreground hover:text-brand-500 transition-colors cursor-pointer px-3 py-1.5">
                    Connexion
                  </a>
                  <a @click="navigateTo('/register')" class="cursor-pointer px-4 py-2 rounded-full bg-foreground text-background text-xs font-semibold hover:opacity-90 transition-all shadow-sm">
                    Lancer l'App
                  </a>
                </template>
                <template v-else>
                  <UserMenu />
                </template>
              </div>
            </div>

            <!-- Mobile Menu Toggle Button -->
            <div class="md:hidden flex items-center gap-2">
              <button @click="toggleTheme" class="p-2 rounded-full text-muted-foreground hover:text-foreground">
                <Sun v-if="isDark" class="w-4 h-4 text-amber-400" />
                <Moon v-else class="w-4 h-4 text-zinc-700" />
              </button>

              <button @click="toggleMobileMenu" class="p-2 text-foreground">
                <Menu v-if="!isMobileMenuOpen" class="h-5 w-5" />
                <X v-else class="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>

        <!-- Mobile Drawer -->
        <div v-if="isMobileMenuOpen" class="md:hidden glass-header border-b border-zinc-200 dark:border-zinc-800 px-6 py-4 flex flex-col gap-4">
          <template v-if="!authStore.isAuthenticated">
            <a href="#features" @click="isMobileMenuOpen = false" class="text-sm font-medium text-muted-foreground">Fonctionnalités</a>
            <a href="#how-it-works" @click="isMobileMenuOpen = false" class="text-sm font-medium text-muted-foreground">Comment ça marche</a>
            <div class="flex flex-col gap-2 pt-2">
              <Button class="w-full" @click="navigateTo('/register')">Lancer l'App</Button>
              <Button variant="outline" class="w-full" @click="navigateTo('/login')">Se connecter</Button>
            </div>
          </template>
          <template v-else>
            <Button variant="ghost" class="w-full justify-start" @click="navigateTo('/dashboard')">Tableau de bord</Button>
            <Button variant="ghost" class="w-full justify-start" @click="navigateTo('/compare')">Comparateur CV</Button>
            <Button variant="ghost" class="w-full justify-start" @click="navigateTo('/interview-simulator')">Simulateur d'Entretien</Button>
            <Button variant="ghost" class="w-full justify-start" @click="navigateTo('/profile')">Mon Profil</Button>
            <Button variant="ghost" class="w-full justify-start text-red-500" @click="handleSignOut">Se déconnecter</Button>
          </template>
        </div>
      </header>

      <!-- Main Router Outlet -->
      <main class="flex-grow pt-16">
        <RouterView />
      </main>

      <!-- Minimalist Apple-style Footer -->
      <footer class="border-t border-zinc-200/80 dark:border-zinc-800/80 bg-background py-12 relative z-10">
        <div class="max-w-7xl mx-auto px-6 lg:px-8 flex flex-col md:flex-row justify-between items-center gap-6">
          <div class="flex items-center gap-3 text-xs text-muted-foreground">
            <div class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
            <span>CV Offer Comparer — Studio de Précision d'Analyse ATS</span>
          </div>

          <div class="text-xs text-muted-foreground">
            © 2026. Tous droits réservés.
          </div>

          <div class="flex items-center gap-6 text-xs text-muted-foreground">
            <a href="mailto:rebeau.mickael@gmail.com" class="hover:text-foreground transition-colors">Contact</a>
            <a href="https://github.com/mickaelrebeau" target="_blank" rel="noopener" class="hover:text-foreground transition-colors">GitHub</a>
          </div>
        </div>
      </footer>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'
import { Button } from '@/components/ui/button'
import { Menu, X, Sun, Moon } from 'lucide-vue-next'
import UserMenu from '@/components/UserMenu.vue'
import { useTheme } from '@/composables/useTheme'
import { useAuthStore } from '@/stores/auth'

const { isDark, toggleTheme } = useTheme()
const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

const isMobileMenuOpen = ref(false)

const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value
}

const navigateTo = (path: string) => {
  router.push(path)
  isMobileMenuOpen.value = false
}

const handleLogoClick = () => {
  if (authStore.isAuthenticated) {
    router.push('/dashboard')
  } else {
    router.push('/')
  }
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
