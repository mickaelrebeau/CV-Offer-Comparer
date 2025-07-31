<template>
  <div class="min-h-screen bg-background">
    <!-- État de chargement initial -->
    <div v-if="authStore.loading" class="flex items-center justify-center min-h-screen">
      <div class="text-center space-y-4">
        <div class="h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent mx-auto"></div>
        <p class="text-muted-foreground">Initialisation...</p>
      </div>
    </div>

    <!-- Application principale -->
    <div v-else>
      <!-- Header fixe avec animation -->
      <header class="fixed top-0 left-0 right-0 z-50 border-b bg-card/95 backdrop-blur-sm transition-all duration-300"
        :class="{
          'translate-y-0 opacity-100': showHeader,
          '-translate-y-full opacity-0': !showHeader
        }">
        <div class="container mx-auto px-4 py-4">
          <nav class="flex items-center justify-between">
            <div class="flex items-center space-x-4">
              <h1 class="text-2xl font-bold text-primary cursor-pointer" @click="handleLogoClick">
                Comparateur CV ↔ Offre
              </h1>
            </div>
            <div class="flex items-center space-x-4">
              <Button variant="outline" @click="toggleTheme">
                <Sun v-if="isDark" class="h-4 w-4" />
                <Moon v-else class="h-4 w-4" />
              </Button>
              <UserMenu />
            </div>
          </nav>
        </div>
      </header>

      <!-- Espace pour compenser le header fixe -->
      <div class="h-20"></div>

      <main class="container mb-12 mx-auto px-4 py-8 min-h-[calc(100vh-20rem)]">
        <RouterView />
      </main>

      <!-- Footer -->
      <footer class="bg-card border-t mt-auto">
        <div class="container mx-auto px-4 py-12">
          <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
            <!-- Logo et description -->
            <div class="col-span-1 md:col-span-2">
              <h3 class="text-xl font-bold text-primary mb-4">
                Comparateur CV ↔ Offre d'emploi
              </h3>
              <p class="text-muted-foreground mb-4 max-w-md">
                Analysez intelligemment la correspondance entre votre CV et les offres d'emploi
                grâce à l'intelligence artificielle. Votre confidentialité est notre priorité.
              </p>
            </div>

            <!-- Fonctionnalités -->
            <div>
              <h4 class="font-semibold mb-4">Fonctionnalités</h4>
              <ul class="space-y-2 text-sm text-muted-foreground">
                <li>• Comparaison CV ↔ Offre</li>
                <li>• Simulateur d'entretien IA</li>
                <li>• Analyse intelligente</li>
                <li>• Suggestions personnalisées</li>
              </ul>
            </div>

            <!-- Contact et liens -->
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

          <!-- Ligne de séparation -->
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
import { RouterView } from 'vue-router'
import { Button } from '@/components/ui/button'
import { Sun, Moon, Shield, HelpCircle, Mail, FileText } from 'lucide-vue-next'
import UserMenu from '@/components/UserMenu.vue'
import { useTheme } from '@/composables/useTheme'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const { isDark, toggleTheme } = useTheme()
const authStore = useAuthStore()
const router = useRouter()

// État pour l'animation du header
const showHeader = ref(false)
let lastScrollY = 0

// Gestion du scroll pour l'animation du header
const handleScroll = () => {
  const currentScrollY = window.scrollY

  // Afficher le header si on scroll vers le haut ou si on est en haut de page
  if (currentScrollY < lastScrollY || currentScrollY < 100) {
    showHeader.value = true
  } else {
    showHeader.value = false
  }

  lastScrollY = currentScrollY
}

// Gestion du clic sur le logo
const handleLogoClick = () => {
  if (authStore.isAuthenticated) {
    router.push('/dashboard')
  } else {
    router.push('/')
  }
}

// Initialiser l'authentification au démarrage
onMounted(async () => {
  await authStore.initializeAuth()

  // Ajouter l'écouteur de scroll
  window.addEventListener('scroll', handleScroll, { passive: true })
})

// Nettoyer l'écouteur de scroll
onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script> 