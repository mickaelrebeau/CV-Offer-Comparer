<template>
  <div class="relative">
    <Button v-if="!isAuthenticated" variant="outline" size="sm" class="rounded-full" @click="$router.push('/login')">
      Connexion
    </Button>

    <div v-else class="flex items-center gap-3">
      <span class="text-xs font-medium text-muted-foreground hidden sm:inline-block">
        {{ user?.email }}
      </span>
      <Button variant="outline" size="sm" class="rounded-full text-xs" @click="$router.push('/profile')">
        Profil
      </Button>
      <Button variant="ghost" size="sm" class="rounded-full text-xs text-rose-500 hover:text-rose-600 hover:bg-rose-500/10" @click="handleSignOut">
        Déconnexion
      </Button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Button } from '@/components/ui/button'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const { user, isAuthenticated, signOut } = authStore

async function handleSignOut() {
  await signOut()
  router.push('/')
}
</script>
