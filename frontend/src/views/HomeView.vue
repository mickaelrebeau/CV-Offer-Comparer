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
        <div class="py-12 grid grid-cols-1 md:grid-cols-3 gap-6">
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

    <!-- Confidentialité -->
    <Card class="mt-12">
      <CardHeader>
        <div class="flex items-center gap-4">
          <Shield class="h-6 w-6 text-primary" />
          <CardTitle>
            Confidentialité et sécurité
          </CardTitle>
        </div>
      </CardHeader>
      <CardContent>
        <div class="p-8 space-y-4 flex flex-col items-center gap-8">
          <div class="flex items-start gap-3">
            <div class="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center mt-0.5">
              <CheckCircle class="h-4 w-4 text-green-600" />
            </div>
            <div>
              <h4 class="font-semibold text-green-700">Vos données ne sont pas sauvegardées</h4>
              <p class="text-sm text-muted-foreground mt-1">
                Vos CV et offres d'emploi sont analysés en temps réel et ne sont jamais stockés sur nos serveurs.
                Une fois l'analyse terminée, toutes les données sont automatiquement supprimées.
              </p>
            </div>
          </div>
          <div class="flex items-start gap-3">
            <div class="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center mt-0.5">
              <Lock class="h-4 w-4 text-blue-600" />
            </div>
            <div>
              <h4 class="font-semibold text-blue-700">Analyse sécurisée</h4>
              <p class="text-sm text-muted-foreground mt-1">
                L'analyse est effectuée via des connexions sécurisées et vos données ne sont utilisées
                que pour générer les résultats de comparaison.
              </p>
            </div>
          </div>
          <div class="flex items-start gap-3">
            <div class="w-6 h-6 bg-purple-100 rounded-full flex items-center justify-center mt-0.5">
              <EyeOff class="h-4 w-4 text-purple-600" />
            </div>
            <div>
              <h4 class="font-semibold text-purple-700">Aucun accès humain</h4>
              <p class="text-sm text-muted-foreground mt-1">
                Seule notre IA accède à vos données pour l'analyse. Aucun être humain ne peut voir
                le contenu de vos CV ou offres d'emploi.
              </p>
            </div>
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
import { FileText, CheckCircle, Lightbulb, Shield, Lock, EyeOff } from 'lucide-vue-next'

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