<template>
  <div class="space-y-6">
    <!-- Zone de saisie -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Offre d'emploi -->
      <Card>
        <CardHeader>
          <CardTitle class="flex items-center space-x-2">
            <FileText class="h-5 w-5" />
            <span>Offre d'emploi</span>
          </CardTitle>
          <CardDescription>
            Collez le texte de l'offre d'emploi ici
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Textarea :model-value="compareStore.offerText" placeholder="Collez le texte de l'offre d'emploi..."
            class="min-h-[300px] w-full border-2 border-gray-300 rounded-md p-2" 
            @input="handleOfferInput" />
        </CardContent>
      </Card>

      <!-- CV avec onglets -->
      <Card>
        <CardHeader>
          <CardTitle class="flex items-center space-x-2">
            <User class="h-5 w-5" />
            <span>Mon CV</span>
          </CardTitle>
          <CardDescription>
            Uploadez votre CV PDF ou saisissez le texte manuellement
          </CardDescription>
        </CardHeader>
        <CardContent>
          <!-- Onglets -->
          <div class="flex space-x-1 mb-4">
            <Button variant="outline" size="sm"
              :class="activeTab === 'upload' ? 'bg-primary text-primary-foreground p-2 flex items-center justify-center rounded-md' : 'p-2 flex items-center justify-center rounded-md'"
              @click="activeTab = 'upload'">
              <Upload class="h-4 w-4 mr-2" />
              Upload PDF
            </Button>
            <Button variant="outline" size="sm"
              :class="activeTab === 'manual' ? 'bg-primary text-primary-foreground p-2 flex items-center justify-center rounded-md' : 'p-2 flex items-center justify-center'"
              @click="activeTab = 'manual'">
              <Edit class="h-4 w-4 mr-2" />
              Saisie manuelle
            </Button>
          </div>

          <!-- Contenu des onglets -->
          <div v-if="activeTab === 'upload'">
            <PDFUpload :model-value="compareStore.cvText"
              @update:model-value="(value) => { console.log('PDFUpload event:', value.length); compareStore.updateCVText(value); }" />
          </div>

          <div v-else-if="activeTab === 'manual'">
            <Textarea :model-value="compareStore.cvText" placeholder="Collez le texte de votre CV..."
              class="min-h-[300px] w-full border-2 border-gray-300 rounded-md p-2" 
              @input="handleCVInput" />
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- Bouton de comparaison -->
    <div class="flex justify-center items-center flex-col">
      <!-- Indicateur de progression -->
      <div v-if="compareStore.loading" class="mb-4 w-full max-w-md">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm text-muted-foreground">{{ compareStore.status }}</span>
          <span class="text-sm font-medium">{{ Math.round(compareStore.progress) }}%</span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2">
          <div class="bg-primary h-2 rounded-full transition-all duration-300" 
               :style="{ width: compareStore.progress + '%' }"></div>
        </div>
      </div>
      
      <Button :disabled="!compareStore.hasData || compareStore.loading" @click="compareStore.compareCVWithOfferStream"
        class="px-8 py-3 p-2 flex items-center justify-center rounded-md border-2 border-primary disabled:opacity-50">
        <Loader2 v-if="compareStore.loading" class="mr-2 h-4 w-4 animate-spin" />
        <ArrowRightLeft class="mr-2 h-4 w-4" />
        Comparer CV et Offre
      </Button>
    </div>

    <!-- Message d'erreur -->
    <div v-if="compareStore.error" class="bg-destructive/10 border border-destructive text-destructive px-4 py-3 rounded-md">
      {{ compareStore.error }}
    </div>

    <!-- Résultats de comparaison -->
    <div v-if="compareStore.comparisonResult" class="space-y-6">
      <!-- Résumé -->
      <Card>
        <CardHeader>
          <CardTitle>Résumé de la comparaison</CardTitle>
        </CardHeader>
        <CardContent>
          <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <div class="text-center">
              <div class="text-2xl font-bold text-match">{{ compareStore.comparisonResult.summary.matches }}</div>
              <div class="text-sm text-muted-foreground">Correspondances</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-missing">{{ compareStore.comparisonResult.summary.missing }}</div>
              <div class="text-sm text-muted-foreground">Manquants</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-unclear">{{ compareStore.comparisonResult.summary.unclear }}</div>
              <div class="text-sm text-muted-foreground">Confus</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-primary">
                {{ formatPercentage(compareStore.comparisonResult.summary.matchPercentage) }}
              </div>
              <div class="text-sm text-muted-foreground">Score global</div>
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- Détails de comparaison -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Offre d'emploi avec highlights -->
        <Card>
          <CardHeader>
            <CardTitle>Offre d'emploi analysée</CardTitle>
          </CardHeader>
          <CardContent>
            <div class="space-y-3">
              <div v-for="item in compareStore.comparisonResult.items" :key="item.id" class="p-3 rounded-md border"
                :class="getStatusColor(item.status)">
                <div class="flex items-start justify-between">
                  <div class="flex-1">
                    <div class="font-medium">{{ item.category }}</div>
                    <div class="text-sm mt-1">{{ item.offerText }}</div>
                  </div>
                  <div class="ml-2">
                    <CheckCircle v-if="item.status === 'match'" class="h-4 w-4" />
                    <XCircle v-else-if="item.status === 'missing'" class="h-4 w-4" />
                    <AlertCircle v-else class="h-4 w-4" />
                  </div>
                </div>
                <div v-if="item.confidence < 0.8" class="text-xs mt-2 opacity-75">
                  Confiance: {{ formatPercentage(item.confidence) }}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- CV avec correspondances -->
        <Card>
          <CardHeader>
            <CardTitle>Correspondances dans votre CV</CardTitle>
          </CardHeader>
          <CardContent>
            <div class="space-y-3">
              <div v-for="item in compareStore.comparisonResult.items" :key="item.id" class="p-3 rounded-md border"
                :class="item.cvText ? getStatusColor(item.status) : 'bg-gray-100'">
                <div class="flex items-start justify-between">
                  <div class="flex-1">
                    <div class="font-medium">{{ item.category }}</div>
                    <div v-if="item.cvText" class="text-sm mt-1">{{ item.cvText }}</div>
                    <div v-else class="text-sm mt-1 text-muted-foreground italic">
                      Aucune correspondance trouvée
                    </div>
                  </div>
                  <div class="ml-2">
                    <CheckCircle v-if="item.status === 'match'" class="h-4 w-4" />
                    <XCircle v-else-if="item.status === 'missing'" class="h-4 w-4" />
                    <AlertCircle v-else class="h-4 w-4" />
                  </div>
                </div>
                <div v-if="item.suggestions?.length" class="mt-2">
                  <div class="text-xs font-medium mb-1">Suggestions :</div>
                  <ul class="text-xs space-y-1">
                    <li v-for="suggestion in item.suggestions" :key="suggestion" class="pl-2">
                      • {{ suggestion }}
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { FileText, User, ArrowRightLeft, Loader2, CheckCircle, XCircle, AlertCircle, Upload, Edit } from 'lucide-vue-next'
import { useCompareStore } from '@/stores/compare'
import { formatPercentage, getStatusColor } from '@/lib/utils'
import PDFUpload from './PDFUpload.vue'

const compareStore = useCompareStore()

// Onglet actif pour le CV
const activeTab = ref<'upload' | 'manual'>('upload')

const handleOfferInput = (event: Event) => {
  const target = event.target as HTMLTextAreaElement;
  console.log('handleOfferInput called with length:', target.value.length);
  console.log('Before updateOfferText - offerText from store:', compareStore.offerText.length);
  compareStore.updateOfferText(target.value);
  console.log('After updateOfferText - offerText from store:', compareStore.offerText.length);
};

const handleCVInput = (event: Event) => {
  const target = event.target as HTMLTextAreaElement;
  console.log('handleCVInput called with length:', target.value.length);
  compareStore.updateCVText(target.value);
};
</script>