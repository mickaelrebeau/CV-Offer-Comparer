<template>
  <div class="min-h-screen bg-background">
    <div v-if="authStore.loading" class="flex items-center justify-center min-h-screen">
      <div class="text-center space-y-4">
        <div class="h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent mx-auto"></div>
        <p class="text-muted-foreground">Initialisation...</p>
      </div>
    </div>

    <div v-else>
      <header class="fixed top-0 left-0 right-0 z-50 border-b bg-card/95 backdrop-blur-sm transition-all duration-300"
        :class="{
          'translate-y-0 opacity-100': showHeader,
          '-translate-y-full opacity-0': !showHeader
        }">
        <div class="container mx-auto px-4 py-4">
          <nav class="flex items-center justify-between">
            <div class="flex items-center space-x-4">
              <h1 class="text-xl md:text-2xl font-bold text-primary cursor-pointer" @click="handleLogoClick">
                <span class="hidden sm:inline">Comparateur CV ↔ Offre</span>
                <span class="sm:hidden">CV ↔ Offre</span>
              </h1>
            </div>

            <div class="hidden md:flex items-center space-x-4">
              <UserMenu />
            </div>

            <div class="md:hidden flex items-center space-x-2">
              <Button variant="outline" @click="toggleTheme" size="sm">
                <Sun v-if="isDark" class="h-4 w-4" />
                <Moon v-else class="h-4 w-4" />
              </Button>
              <Button variant="outline" @click="toggleMobileMenu" size="sm">
                <Menu v-if="!isMobileMenuOpen" class="h-4 w-4" />
                <X v-else class="h-4 w-4" />
              </Button>
            </div>
          </nav>

          <div v-if="isMobileMenuOpen"
            class="md:hidden mt-4 pb-4 border-t pt-4 animate-in slide-in-from-top-2 duration-200">
            <div class="space-y-3">
              <div class="space-y-2">
                <Button v-if="!authStore.isAuthenticated" variant="ghost" class="w-full justify-start"
                  @click="navigateTo('/')" :class="{ 'bg-accent': $route.path === '/' }">
                  Accueil
                </Button>
                <Button v-if="authStore.isAuthenticated" variant="ghost" class="w-full justify-start"
                  @click="navigateTo('/dashboard')" :class="{ 'bg-accent rounded': $route.path === '/dashboard' }">
                  Tableau de bord
                </Button>
                <Button v-if="!authStore.isAuthenticated" variant="ghost" class="w-full justify-start"
                  @click="navigateTo('/free-trial')" :class="{ 'bg-accent rounded': $route.path === '/free-trial' }">
                  Essai gratuit
                </Button>
                <Button v-if="authStore.isAuthenticated" variant="ghost" class="w-full justify-start"
                  @click="navigateTo('/compare')" :class="{ 'bg-accent rounded': $route.path === '/compare' }">
                  Comparer un CV ↔ Offre
                </Button>
                <Button v-if="authStore.isAuthenticated" variant="ghost" class="w-full justify-start"
                  @click="navigateTo('/interview-simulator')"
                  :class="{ 'bg-accent rounded': $route.path === '/interview-simulator' }">
                  Simulateur d'entretien
                </Button>
              </div>

              <div class="border-t my-3"></div>

              <div v-if="!authStore.isAuthenticated" class="space-y-2">
                <Button variant="outline" class="w-full" @click="navigateTo('/login')">
                  Se connecter
                </Button>
                <Button variant="default" class="w-full" @click="navigateTo('/register')">
                  S'inscrire
                </Button>
              </div>

              <div v-else class="space-y-2 flex flex-col items-center">
                <div class="px-3 py-2 text-sm text-muted-foreground">
                  {{ authStore.user?.email }}
                </div>
                <Button variant="full-outline" @click="navigateTo('/profile')">
                  <User class="h-4 w-4 mr-2" />
                  Profile
                </Button>
                <Button variant="full" @click="handleSignOut">
                  <LogOut class="h-4 w-4 mr-2" />
                  Se déconnecter
                </Button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div class="h-20 md:h-20"></div>

      <main class="container mb-12 mx-auto px-4 py-8 min-h-[calc(100vh-20rem)]">
        <RouterView />
      </main>

      <footer class="bg-card border-t mt-auto">
        <div class="container mx-auto px-4 py-12">
          <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div class="col-span-1 md:col-span-2">
              <h3 class="text-xl font-bold text-primary mb-4">
                Comparateur CV ↔ Offre d'emploi
              </h3>
              <p class="text-muted-foreground mb-4 max-w-md">
                Analysez intelligemment la correspondance entre votre CV et les offres d'emploi
                grâce à l'intelligence artificielle. Votre confidentialité est notre priorité.
              </p>
            </div>

            <div>
              <h4 class="font-semibold mb-4">Fonctionnalités</h4>
              <ul class="space-y-2 text-sm text-muted-foreground">
                <li>• Comparaison CV ↔ Offre</li>
                <li>• Simulateur d'entretien IA</li>
                <li>• Analyse intelligente</li>
                <li>• Suggestions personnalisées</li>
              </ul>
            </div>

            <div>
              <h4 class="font-semibold mb-4">Contact</h4>
              <ul class="space-y-2 text-sm text-muted-foreground">
                <li class="flex items-center">
                  <Mail class="h-4 w-4 mr-2" />
                  rebeau.mickael@gmail.com
                </li>
              </ul>
            </div>
          </div>

          <div class="border-t mt-8 pt-8">
            <div class="flex flex-col md:flex-row justify-between items-center">
              <p class="text-sm text-muted-foreground">
                © 2025 Comparateur CV ↔ Offre. Tous droits réservés.
              </p>
              <div class="flex items-center space-x-4 mt-4 md:mt-0">
                <span class="text-sm text-muted-foreground">
                  🔒 100% Confidential - Aucune donnée sauvegardée
                </span>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, onUnmounted } from 'vue'
import { RouterView, useRoute } from 'vue-router'
import { Button } from '@/components/ui/button'
import { Sun, Moon, Shield, HelpCircle, Mail, FileText, Menu, X, User, LogOut } from 'lucide-vue-next'
import UserMenu from '@/components/UserMenu.vue'
import { useTheme } from '@/composables/useTheme'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const { isDark, toggleTheme } = useTheme()
const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

const showHeader = ref(true)
const isMobileMenuOpen = ref(false)
let lastScrollY = 0

const handleScroll = () => {
  const currentScrollY = window.scrollY

  if (currentScrollY < lastScrollY || currentScrollY < 100) {
    showHeader.value = true
  } else {
    showHeader.value = false
    isMobileMenuOpen.value = false
  }

  lastScrollY = currentScrollY
}

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

  window.addEventListener('scroll', handleScroll, { passive: true })
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script> 