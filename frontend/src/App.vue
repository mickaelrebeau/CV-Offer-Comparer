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
      <header class="border-b bg-card">
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

      <main class="container mx-auto px-4 py-8">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'
import { Button } from '@/components/ui/button'
import { Sun, Moon } from 'lucide-vue-next'
import UserMenu from '@/components/UserMenu.vue'
import { useTheme } from '@/composables/useTheme'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const { isDark, toggleTheme } = useTheme()
const authStore = useAuthStore()
const router = useRouter()

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
})
</script> 