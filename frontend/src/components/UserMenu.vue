<template>
  <div class="relative">
    <!-- Utilisateur non connecté -->
    <Button v-if="!isAuthenticated" variant="outline" @click="$router.push('/login')">
      Se connecter
    </Button>

    <!-- Utilisateur connecté -->
    <div v-else class="flex items-center space-x-4">
      <span class="text-sm text-muted-foreground">
        {{ user?.email }}
      </span>
      <Button variant="outline" @click="$router.push('/profile')">
        Profile
      </Button>
      <Button variant="outline" @click="handleSignOut">
        Se déconnecter
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