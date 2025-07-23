<template>
  <div class="max-w-4xl mx-auto">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-primary mb-2">
        Mon Profil
      </h1>
      <p class="text-muted-foreground">
        Gérez vos informations et vos préférences
      </p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Informations utilisateur -->
      <Card>
        <CardHeader>
          <CardTitle>Informations personnelles</CardTitle>
        </CardHeader>
        <CardContent>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium mb-2">Email</label>
              <p class="text-muted-foreground">{{ user?.email }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium mb-2">ID utilisateur</label>
              <p class="text-muted-foreground text-sm">{{ user?.id }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium mb-2">Date d'inscription</label>
              <p class="text-muted-foreground">
                {{ user?.created_at ? new Date(user.created_at).toLocaleDateString('fr-FR') : 'N/A' }}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- Statistiques -->
      <Card>
        <CardHeader>
          <CardTitle>Statistiques</CardTitle>
        </CardHeader>
        <CardContent>
          <div class="space-y-4">
            <div class="flex justify-between items-center">
              <span class="text-sm font-medium">Comparaisons effectuées</span>
              <span class="text-2xl font-bold text-primary">0</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-sm font-medium">Score moyen</span>
              <span class="text-2xl font-bold text-match">0%</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-sm font-medium">Dernière activité</span>
              <span class="text-sm text-muted-foreground">Aujourd'hui</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- Actions -->
    <Card class="mt-6">
      <CardHeader>
        <CardTitle>Actions</CardTitle>
      </CardHeader>
      <CardContent>
        <div class="space-y-4">
          <Button variant="outline" @click="$router.push('/compare')">
            Nouvelle comparaison
          </Button>
          <Button variant="destructive" @click="handleSignOut">
            Se déconnecter
          </Button>
        </div>
      </CardContent>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const { user, signOut } = authStore

async function handleSignOut() {
  await signOut()
  router.push('/')
}
</script> 