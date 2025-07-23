<template>
  <div class="w-full">
    <Card>
      <CardHeader>
        <CardTitle class="flex items-center gap-2">
          <Upload class="h-5 w-5" />
          Upload de votre CV (PDF)
        </CardTitle>
        <CardDescription>
          Glissez-déposez votre CV au format PDF ou cliquez pour sélectionner un fichier
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div
          @drop="handleDrop"
          @dragover="handleDragOver"
          @dragleave="handleDragLeave"
          @click="triggerFileInput"
          class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-primary transition-colors"
          :class="{
            'border-primary bg-primary/5': isDragOver,
            'border-green-500 bg-green-50': uploadedFile,
            'border-red-500 bg-red-50': uploadError
          }"
        >
          <input
            ref="fileInput"
            type="file"
            accept=".pdf"
            @change="handleFileSelect"
            class="hidden"
          />
          
          <div v-if="!uploadedFile && !uploading">
            <Upload class="h-12 w-12 mx-auto text-gray-400 mb-4" />
            <p class="text-lg font-medium text-gray-700 mb-2">
              Glissez votre CV PDF ici
            </p>
            <p class="text-sm text-gray-500">
              ou cliquez pour sélectionner un fichier
            </p>
            <p class="text-xs text-gray-400 mt-2">
              Taille maximale : 10MB
            </p>
          </div>

          <div v-else-if="uploading" class="space-y-4">
            <Loader2 class="h-12 w-12 mx-auto animate-spin text-primary" />
            <p class="text-lg font-medium text-gray-700">
              Extraction du texte en cours...
            </p>
            <p class="text-sm text-gray-500">
              Veuillez patienter pendant que nous analysons votre CV
            </p>
          </div>

          <div v-else-if="uploadedFile" class="space-y-4">
            <CheckCircle class="h-12 w-12 mx-auto text-green-500" />
            <div>
              <p class="text-lg font-medium text-gray-700">
                CV uploadé avec succès !
              </p>
              <p class="text-sm text-gray-500">
                {{ uploadedFile.name }}
              </p>
              <p class="text-xs text-gray-400 mt-1">
                {{ extractedText.length }} caractères extraits
              </p>
            </div>
            <Button variant="outline" size="sm" @click="removeFile">
              Changer de fichier
            </Button>
          </div>

          <div v-else-if="uploadError" class="space-y-4">
            <XCircle class="h-12 w-12 mx-auto text-red-500" />
            <div>
              <p class="text-lg font-medium text-red-700">
                Erreur lors de l'upload
              </p>
              <p class="text-sm text-red-500">
                {{ uploadError }}
              </p>
            </div>
            <Button variant="outline" size="sm" @click="resetUpload">
              Réessayer
            </Button>
          </div>
        </div>

        <!-- Aperçu du texte extrait -->
        <div v-if="extractedText && showPreview" class="mt-6">
          <div class="flex items-center justify-between mb-2">
            <h4 class="font-medium">Aperçu du texte extrait :</h4>
            <Button variant="ghost" size="sm" @click="showPreview = !showPreview">
              {{ showPreview ? 'Masquer' : 'Afficher' }}
            </Button>
          </div>
          <div class="bg-gray-50 rounded-md p-4 max-h-40 overflow-y-auto">
            <pre class="text-sm text-gray-700 whitespace-pre-wrap">{{ extractedText }}</pre>
          </div>
        </div>
      </CardContent>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Upload, CheckCircle, XCircle, Loader2 } from 'lucide-vue-next'
import { api } from '@/lib/api'

interface Props {
  modelValue?: string
}

interface Emits {
  (e: 'update:modelValue', value: string): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const fileInput = ref<HTMLInputElement>()
const isDragOver = ref(false)
const uploading = ref(false)
const uploadedFile = ref<File | null>(null)
const uploadError = ref<string | null>(null)
const extractedText = ref('')
const showPreview = ref(false)

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleDragOver = (e: DragEvent) => {
  e.preventDefault()
  isDragOver.value = true
}

const handleDragLeave = (e: DragEvent) => {
  e.preventDefault()
  isDragOver.value = false
}

const handleDrop = (e: DragEvent) => {
  e.preventDefault()
  isDragOver.value = false
  
  const files = e.dataTransfer?.files
  if (files && files.length > 0) {
    handleFile(files[0])
  }
}

const handleFileSelect = (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    handleFile(target.files[0])
  }
}

const handleFile = async (file: File) => {
  // Vérifications
  if (!file.name.toLowerCase().endsWith('.pdf')) {
    uploadError.value = 'Seuls les fichiers PDF sont acceptés'
    return
  }

  if (file.size > 10 * 1024 * 1024) {
    uploadError.value = 'Le fichier est trop volumineux (max 10MB)'
    return
  }

  // Reset states
  uploadError.value = null
  uploading.value = true
  uploadedFile.value = file

  try {
    const formData = new FormData()
    formData.append('file', file)

    const response = await api.post('/upload-cv', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    if (response.data.success) {
      extractedText.value = response.data.text
      console.log('PDFUpload: emitting update:modelValue with text length:', response.data.text.length)
      emit('update:modelValue', response.data.text)
      showPreview.value = true
    } else {
      uploadError.value = response.data.message
      uploadedFile.value = null
    }
  } catch (error: any) {
    uploadError.value = error.response?.data?.detail || 'Erreur lors de l\'upload'
    uploadedFile.value = null
  } finally {
    uploading.value = false
  }
}

const removeFile = () => {
  uploadedFile.value = null
  extractedText.value = ''
  uploadError.value = null
  emit('update:modelValue', '')
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const resetUpload = () => {
  uploadError.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}
</script> 