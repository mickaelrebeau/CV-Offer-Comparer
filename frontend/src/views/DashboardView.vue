<template>
    <div class="max-w-6xl mx-auto">
        <div class="text-center space-y-6 py-8">
            <h1 class="text-3xl font-bold text-primary">Tableau de bord</h1>
            <p class="text-lg text-muted-foreground">Choisissez l'outil qui vous aidera à préparer votre recherche d'emploi</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-8 py-8">
            <!-- Comparateur CV ↔ Offre Card -->
            <Card class="hover:shadow-lg transition-shadow cursor-pointer border rounded-lg" @click="goToComparator">
                <CardHeader>
                    <CardTitle class="flex items-center space-x-2">
                        <FileText class="h-6 w-6" />
                        <span>Comparateur CV ↔ Offre</span>
                    </CardTitle>
                    <CardDescription>
                        Analysez la correspondance entre votre CV et une offre d'emploi avec notre IA avancée
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <div class="space-y-2 text-sm text-muted-foreground">
                        <div class="flex items-center gap-2">
                            <CheckCircle class="h-4 w-4 text-green-500" />
                            <span>Analyse sémantique intelligente</span>
                        </div>
                        <div class="flex items-center gap-2">
                            <CheckCircle class="h-4 w-4 text-green-500" />
                            <span>Extraction automatique des compétences</span>
                        </div>
                        <div class="flex items-center gap-2">
                            <CheckCircle class="h-4 w-4 text-green-500" />
                            <span>Rapport détaillé avec suggestions</span>
                        </div>
                    </div>
                </CardContent>
                <CardFooter>
                    <Button variant="full" @click="goToComparator">
                        Commencer l'analyse
                    </Button>
                </CardFooter>
            </Card>

            <!-- Simulateur d'entretien Card -->
            <Card class="hover:shadow-lg transition-shadow cursor-pointer border rounded-lg" @click="goToInterviewSimulator">
                <CardHeader>
                    <CardTitle class="flex items-center space-x-2">
                        <MessageSquare class="h-6 w-6" />
                        <span>Simulateur d'entretien</span>
                    </CardTitle>
                    <CardDescription>
                        Préparez-vous aux entretiens avec des questions personnalisées basées sur votre profil
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <div class="space-y-2 text-sm text-muted-foreground">
                        <div class="flex items-center gap-2">
                            <CheckCircle class="h-4 w-4 text-green-500" />
                            <span>Questions générées par IA</span>
                        </div>
                        <div class="flex items-center gap-2">
                            <CheckCircle class="h-4 w-4 text-green-500" />
                            <span>Simulation en temps réel</span>
                        </div>
                        <div class="flex items-center gap-2">
                            <CheckCircle class="h-4 w-4 text-green-500" />
                            <span>Analyse IA de vos réponses</span>
                        </div>
                    </div>
                </CardContent>
                <CardFooter>
                    <Button variant="full" @click="goToInterviewSimulator">
                        Commencer l'entraînement
                    </Button>
                </CardFooter>
            </Card>
        </div>
    </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { FileText, MessageSquare, CheckCircle } from 'lucide-vue-next'

const router = useRouter()

const goToComparator = () => {
    router.push('/compare')
}

const goToInterviewSimulator = () => {
    router.push('/interview-simulator')
}
</script>