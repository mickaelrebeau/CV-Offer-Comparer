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
        <Button size="lg" @click="startFreeTrial">
          🎁 Essai offert
        </Button>
        <Button variant="outline" size="lg" @click="startComparison">
          S'incrire
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
            <div class="w-16 h-16 bg-green-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <span class="text-2xl font-bold text-green-500">1</span>
            </div>
            <h3 class="font-semibold mb-2">Collez vos textes</h3>
            <p class="text-sm text-muted-foreground">
              Copiez le texte de l'offre d'emploi et votre CV dans les zones dédiées.
            </p>
          </div>
          <div class="text-center">
            <div class="w-16 h-16 bg-blue-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <span class="text-2xl font-bold text-blue-500">2</span>
            </div>
            <h3 class="font-semibold mb-2">Lancez l'analyse</h3>
            <p class="text-sm text-muted-foreground">
              Cliquez sur "Comparer" et laissez notre IA analyser les correspondances.
            </p>
          </div>
          <div class="text-center">
            <div class="w-16 h-16 bg-purple-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <span class="text-2xl font-bold text-purple-500">3</span>
            </div>
            <h3 class="font-semibold mb-2">Consultez les résultats</h3>
            <p class="text-sm text-muted-foreground">
              Visualisez les résultats avec notre interface intuitive et colorée.
            </p>
          </div>
        </div>

        <!-- Information sur l'analyse gratuite -->
        <div class="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div class="flex items-center gap-2 mb-2">
            <Gift class="h-5 w-5 text-blue-600" />
            <h4 class="font-semibold text-blue-800">Essai offert disponible</h4>
          </div>
          <p class="text-sm text-blue-700">
            Testez notre outil gratuitement avec une première analyse. Une seule analyse offerte par utilisateur.
            Créez un compte pour des analyses illimitées !
          </p>
          <div class="mt-3">
            <Button size="sm" @click="startFreeTrial"
              class="py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-md">
              Commencer l'essai gratuit
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>

    <!-- Simulateur d'entretien -->
    <Card class="mt-12 border border-primary-200 bg-primary-100/30 rounded-xl">
      <CardHeader>
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
            <MessageSquare class="h-6 w-6 text-primary-600" />
          </div>
          <div>
            <CardTitle>
              🎯 Simulateur d'entretien IA
            </CardTitle>
            <p class="text-sm mt-1">
              Préparez-vous aux entretiens avec notre simulateur intelligent
            </p>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div class="space-y-6">
          <!-- Avantages du simulateur -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="flex items-start gap-3 p-4 bg-white rounded-lg border border-primary-100">
              <div class="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
                <Target class="h-4 w-4 text-green-600" />
              </div>
              <div>
                <h4 class="font-semibold text-green-800 mb-1">Questions ciblées</h4>
                <p class="text-sm text-green-700">
                  L'IA analyse votre CV et l'offre pour poser des questions pertinentes
                </p>
              </div>
            </div>

            <div class="flex items-start gap-3 p-4 bg-white rounded-lg border border-primary-100">
              <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                <TrendingUp class="h-4 w-4 text-blue-600" />
              </div>
              <div>
                <h4 class="font-semibold text-blue-800 mb-1">Amélioration continue</h4>
                <p class="text-sm text-blue-700">
                  Recevez des conseils pour améliorer vos réponses
                </p>
              </div>
            </div>

            <div class="flex items-start gap-3 p-4 bg-white rounded-lg border border-primary-100">
              <div class="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0">
                <Award class="h-4 w-4 text-purple-600" />
              </div>
              <div>
                <h4 class="font-semibold text-purple-800 mb-1">Confiance en soi</h4>
                <p class="text-sm text-purple-700">
                  Entraînez-vous pour aborder vos entretiens avec sérénité
                </p>
              </div>
            </div>
          </div>

          <!-- Accès réservé aux membres -->
          <div class="bg-gradient-to-r from-primary-50 to-amber-50 border border-primary-200 rounded-lg p-6">
            <div class="flex items-center gap-3 mb-4">
              <div class="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                <UserCheck class="h-5 w-5 text-primary-600" />
              </div>
              <div>
                <h4 class="font-bold text-lg text-primary-800">
                  🔐 Accès réservé aux membres
                </h4>
                <p class="text-primary-700 text-sm">
                  Le simulateur d'entretien est exclusivement disponible pour les utilisateurs inscrits
                </p>
              </div>
            </div>

            <div class="text-center">
              <p class="text-primary-700 mb-3">
                <strong>Créez votre compte gratuitement</strong> pour accéder au simulateur d'entretien et à toutes nos
                fonctionnalités avancées !
              </p>
              <Button @click="startComparison" variant="full">
                Créer mon compte gratuit
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>

    <!-- Confidentialité renforcée -->
    <Card class="mt-12 border bg-card/10 rounded-xl">
      <CardHeader>
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
            <Shield class="h-6 w-6 text-primary" />
          </div>
          <div>
            <CardTitle>
              <p class="text-primary">🔒 Confidentialité garantie</p>
            </CardTitle>
            <p class="text-sm text-primary/70 mt-1">
              Vos données personnelles sont protégées et ne sont jamais stockées
            </p>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div class="space-y-6">
          <!-- Point principal sur la non-sauvegarde -->
          <div class="bg-card border rounded-lg p-6">
            <div class="flex items-start gap-4">
              <div class="w-10 h-10 bg-primary/20 rounded-full flex items-center justify-center flex-shrink-0">
                <Trash2 class="h-5 w-5 text-primary" />
              </div>
              <div>
                <h4 class="font-bold text-lg text-primary mb-2">
                  ⚡ Suppression automatique des données
                </h4>
                <p class="text-primary/80 mb-3">
                  <strong>Aucune de vos données n'est sauvegardée sur nos serveurs.</strong> Vos CV et offres d'emploi
                  sont :
                </p>
                <ul class="text-sm text-primary/80 space-y-1 ml-4">
                  <li>• Analysés en temps réel par notre IA</li>
                  <li>• Supprimés automatiquement après l'analyse</li>
                  <li>• Jamais stockés dans une base de données</li>
                  <li>• Inaccessibles après fermeture de la session</li>
                </ul>
              </div>
            </div>
          </div>

          <!-- Autres points de sécurité -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="flex items-start gap-3 p-4 bg-white rounded-lg border">
              <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                <Lock class="h-4 w-4 text-blue-600" />
              </div>
              <div>
                <h4 class="font-semibold text-blue-800 mb-1">Connexion sécurisée</h4>
                <p class="text-sm text-blue-700">
                  Toutes les communications sont chiffrées via HTTPS. Vos données transitent de manière sécurisée.
                </p>
              </div>
            </div>

            <div class="flex items-start gap-3 p-4 bg-white rounded-lg border">
              <div class="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0">
                <EyeOff class="h-4 w-4 text-purple-600" />
              </div>
              <div>
                <h4 class="font-semibold text-purple-800 mb-1">Aucun accès humain</h4>
                <p class="text-sm text-purple-700">
                  Seule notre IA accède à vos données. Aucun employé ne peut voir le contenu de vos documents.
                </p>
              </div>
            </div>

            <div class="flex items-start gap-3 p-4 bg-white rounded-lg border">
              <div class="w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center flex-shrink-0">
                <Clock class="h-4 w-4 text-orange-600" />
              </div>
              <div>
                <h4 class="font-semibold text-orange-800 mb-1">Traitement instantané</h4>
                <p class="text-sm text-orange-700">
                  L'analyse se fait en quelques secondes. Vos données ne restent que le temps nécessaire.
                </p>
              </div>
            </div>

            <div class="flex items-start gap-3 p-4 bg-white rounded-lg border">
              <div class="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center flex-shrink-0">
                <XCircle class="h-4 w-4 text-red-600" />
              </div>
              <div>
                <h4 class="font-semibold text-red-800 mb-1">Pas de cookies de suivi</h4>
                <p class="text-sm text-red-700">
                  Nous n'utilisons pas de cookies de suivi. Votre navigation reste privée.
                </p>
              </div>
            </div>
          </div>

          <!-- Message de confiance -->
          <div class="text-center p-6 bg-card rounded-lg border">
            <h4 class="font-bold text-primary mb-2">
              🛡️ Votre confidentialité est notre priorité
            </h4>
            <p class="text-primary/80">
              Vous pouvez utiliser notre outil en toute confiance. Vos données personnelles et professionnelles
              ne quittent jamais votre navigateur de manière permanente.
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
import { FileText, CheckCircle, Lightbulb, Shield, Lock, EyeOff, Gift, Trash2, Clock, XCircle, MessageSquare, Brain, UserCheck, Target, TrendingUp, Award } from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()

// Fonction pour commencer l'essai gratuit
const startFreeTrial = () => {
  router.push('/free-trial')
}

// Fonction pour commencer la comparaison (analyse gratuite ou connectée)
const startComparison = () => {
  router.push('/register')
}

// Rediriger automatiquement les utilisateurs connectés vers le dashboard
onMounted(() => {
  // Attendre que l'authentification soit initialisée
  if (!authStore.loading && authStore.isAuthenticated) {
    router.push('/dashboard')
  }
})

// Surveiller les changements d'état d'authentification
authStore.$subscribe(() => {
  if (!authStore.loading && authStore.isAuthenticated) {
    router.push('/dashboard')
  }
})
</script> 