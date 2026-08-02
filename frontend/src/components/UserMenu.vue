<template>
  <div class="flex items-center gap-2">
    <span v-if="isAuthenticated" class="hidden max-w-[180px] truncate font-mono text-micro uppercase text-ink-soft sm:inline-block">
      {{ user?.email }}
    </span>
    <Button v-if="!isAuthenticated" variant="outline" size="sm" @click="$router.push('/login')">
      Connexion
    </Button>
    <template v-else>
      <Button variant="outline" size="sm" @click="$router.push('/profile')">Profil</Button>
      <Button variant="ghost" size="sm" class="text-rose-600 hover:text-rose-700" @click="handleSignOut">
        Déconnexion
      </Button>
    </template>
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
