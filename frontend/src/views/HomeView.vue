<template>
  <div class="max-w-4xl mx-auto">
    <!-- Hero Section -->
    <div class="text-center space-y-6 py-12">
      <h1 class="text-4xl font-bold text-primary">
        Comparateur CV ↔ Offre d'emploi
      </h1>
      <p class="text-xl text-muted-foreground max-w-2xl mx-auto">
        Analysez intelligemment la correspondance entre votre CV et les offres d'emploi 
        grâce à l'intelligence artificielle
      </p>
      <div class="flex justify-center space-x-4">
        <Button size="lg" @click="$router.push('/compare')">
          Commencer la comparaison
        </Button>
        <Button variant="outline" size="lg" @click="$router.push('/login')">
          Se connecter
        </Button>
      </div>
    </div>

    <!-- Fonctionnalités -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 py-12">
      <Card>
        <CardHeader>
          <div class="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
            <FileText class="h-6 w-6 text-primary" />
          </div>
          <CardTitle>Analyse intelligente</CardTitle>
        </CardHeader>
        <CardContent>
          <p class="text-muted-foreground">
            Notre IA analyse automatiquement les compétences, expériences et exigences 
            pour identifier les correspondances et les lacunes.
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div class="w-12 h-12 bg-match/10 rounded-lg flex items-center justify-center mb-4">
            <CheckCircle class="h-6 w-6 text-match" />
          </div>
          <CardTitle>Mise en évidence colorée</CardTitle>
        </CardHeader>
        <CardContent>
          <p class="text-muted-foreground">
            Code couleur intuitif : vert pour les correspondances, rouge pour les 
            éléments manquants, jaune pour les points confus.
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div class="w-12 h-12 bg-unclear/10 rounded-lg flex items-center justify-center mb-4">
            <Lightbulb class="h-6 w-6 text-unclear" />
          </div>
          <CardTitle>Suggestions personnalisées</CardTitle>
        </CardHeader>
        <CardContent>
          <p class="text-muted-foreground">
            Recevez des suggestions pour améliorer votre CV et maximiser vos chances 
            de décrocher l'emploi de vos rêves.
          </p>
        </CardContent>
      </Card>
    </div>

    <!-- Comment ça marche -->
    <Card class="mt-12">
      <CardHeader>
        <CardTitle>Comment ça marche ?</CardTitle>
      </CardHeader>
      <CardContent>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="text-center">
            <div class="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <span class="text-2xl font-bold text-primary">1</span>
            </div>
            <h3 class="font-semibold mb-2">Collez vos textes</h3>
            <p class="text-sm text-muted-foreground">
              Copiez le texte de l'offre d'emploi et votre CV dans les zones dédiées.
            </p>
          </div>
          <div class="text-center">
            <div class="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <span class="text-2xl font-bold text-primary">2</span>
            </div>
            <h3 class="font-semibold mb-2">Lancez l'analyse</h3>
            <p class="text-sm text-muted-foreground">
              Cliquez sur "Comparer" et laissez notre IA analyser les correspondances.
            </p>
          </div>
          <div class="text-center">
            <div class="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <span class="text-2xl font-bold text-primary">3</span>
            </div>
            <h3 class="font-semibold mb-2">Consultez les résultats</h3>
            <p class="text-sm text-muted-foreground">
              Visualisez les résultats avec notre interface intuitive et colorée.
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { FileText, CheckCircle, Lightbulb } from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()

// Rediriger automatiquement les utilisateurs connectés vers la page de comparaison
onMounted(() => {
  // Attendre que l'authentification soit initialisée
  if (!authStore.loading && authStore.isAuthenticated) {
    router.push('/compare')
  }
})

// Surveiller les changements d'état d'authentification
authStore.$subscribe(() => {
  if (!authStore.loading && authStore.isAuthenticated) {
    router.push('/compare')
  }
})
</script> 