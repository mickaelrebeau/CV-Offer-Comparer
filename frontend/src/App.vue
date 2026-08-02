<template>
  <div class="min-h-screen bg-[#09090b] text-[#fafafa] relative flex flex-col font-sans selection:bg-zinc-800 selection:text-white">
    
    <!-- Overlay only — never unmount RouterView (breaks /auth/callback) -->
    <div
      v-if="authStore.loading"
      class="fixed inset-0 z-[100] flex items-center justify-center bg-[#09090b]/90 backdrop-blur-sm"
    >
      <div class="text-center space-y-4 font-mono">
        <div class="w-8 h-8 border-2 border-zinc-700 border-t-white rounded-full animate-spin mx-auto"></div>
        <p class="text-xs text-zinc-400 tracking-wide">_INITIALIZING_SESSION...</p>
      </div>
    </div>

    <div class="relative z-10 flex flex-col min-h-screen">

      <!-- Navigation Header for App Dashboard & Subpages (Hidden on Landing Page '/') -->
      <header 
        v-if="route.path !== '/'" 
        class="sticky top-0 w-full z-50 bg-[#09090b]/90 backdrop-blur-md border-b border-zinc-800"
      >
        <div class="max-w-7xl mx-auto px-6 lg:px-8">
          <div class="flex items-center justify-between h-14 font-mono text-xs">
            <!-- Brand Logo -->
            <a @click="handleLogoClick" class="cursor-pointer flex items-center gap-2 group">
              <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
              <span class="font-bold tracking-tight text-white group-hover:text-zinc-300 transition-colors">
                CV OFFER COMPARER
              </span>
            </a>

            <!-- Desktop Menu Navigation -->
            <div class="hidden md:flex items-center gap-6 text-zinc-400">
              <template v-if="authStore.isAuthenticated">
                <a @click="navigateTo('/dashboard')" class="hover:text-white transition-colors cursor-pointer" :class="{ 'text-white font-bold': route.path === '/dashboard' }">
                  [dashboard]
                </a>
                <a @click="navigateTo('/compare')" class="hover:text-white transition-colors cursor-pointer" :class="{ 'text-white font-bold': route.path === '/compare' }">
                  [compare]
                </a>
                <a @click="navigateTo('/interview-simulator')" class="hover:text-white transition-colors cursor-pointer" :class="{ 'text-white font-bold': route.path === '/interview-simulator' }">
                  [simulator]
                </a>
              </template>

              <!-- Actions & Theme Toggle -->
              <div class="flex items-center gap-3 pl-4 border-l border-zinc-800">
                <button @click="toggleTheme" class="p-1.5 rounded text-zinc-400 hover:text-white transition-colors" title="Changer le thème">
                  <Sun v-if="isDark" class="w-3.5 h-3.5 text-amber-400" />
                  <Moon v-else class="w-3.5 h-3.5 text-zinc-400" />
                </button>

                <template v-if="!authStore.isAuthenticated">
                  <a @click="navigateTo('/login')" class="text-zinc-400 hover:text-white transition-colors cursor-pointer">
                    login
                  </a>
                  <a @click="navigateTo('/register')" class="cursor-pointer px-3 py-1 rounded bg-white text-zinc-950 font-bold hover:bg-zinc-200 transition-all">
                    [get started]
                  </a>
                </template>
                <template v-else>
                  <UserMenu />
                </template>
              </div>
            </div>

            <!-- Mobile Menu Toggle Button -->
            <div class="md:hidden flex items-center gap-2">
              <button @click="toggleTheme" class="p-1.5 rounded text-zinc-400 hover:text-white">
                <Sun v-if="isDark" class="w-4 h-4 text-amber-400" />
                <Moon v-else class="w-4 h-4 text-zinc-400" />
              </button>

              <button @click="toggleMobileMenu" class="p-1.5 text-white">
                <Menu v-if="!isMobileMenuOpen" class="h-5 w-5" />
                <X v-else class="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>

        <!-- Mobile Drawer -->
        <div v-if="isMobileMenuOpen" class="md:hidden bg-[#0c0c0e] border-b border-zinc-800 px-6 py-4 flex flex-col gap-3 font-mono text-xs">
          <template v-if="!authStore.isAuthenticated">
            <a @click="navigateTo('/login')" class="text-zinc-400 py-1">login</a>
            <a @click="navigateTo('/register')" class="text-white font-bold py-1">[get started]</a>
          </template>
          <template v-else>
            <a @click="navigateTo('/dashboard')" class="text-zinc-300 py-1">[dashboard]</a>
            <a @click="navigateTo('/compare')" class="text-zinc-300 py-1">[compare]</a>
            <a @click="navigateTo('/interview-simulator')" class="text-zinc-300 py-1">[simulator]</a>
            <a @click="handleSignOut" class="text-rose-400 py-1">[sign out]</a>
          </template>
        </div>
      </header>

      <!-- Main Router Outlet -->
      <main class="flex-grow">
        <RouterView />
      </main>

      <!-- Minimalist Architectural Footer (Hidden on Landing Page '/') -->
      <footer v-if="route.path !== '/'" class="border-t border-zinc-800 bg-[#09090b] py-8 relative z-10 font-mono text-xs">
        <div class="max-w-7xl mx-auto px-6 lg:px-8 flex flex-col sm:flex-row justify-between items-center gap-4 text-zinc-500">
          <div class="flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
            <span>CV OFFER COMPARER — ATS PRECISION STUDIO</span>
          </div>

          <div>
            © 2026. ALL RIGHTS RESERVED.
          </div>

          <div class="flex items-center gap-4">
            <a href="mailto:rebeau.mickael@gmail.com" class="hover:text-white transition-colors">CONTACT</a>
            <a href="https://github.com/mickaelrebeau" target="_blank" rel="noopener" class="hover:text-white transition-colors">GITHUB</a>
          </div>
        </div>
      </footer>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
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
