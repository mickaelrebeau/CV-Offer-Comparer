<template>
  <div class="w-full">
    <div
      @drop="handleDrop"
      @dragover="handleDragOver"
      @dragleave="handleDragLeave"
      @click="triggerFileInput"
      class="cursor-pointer rounded-lg border-2 border-dashed p-8 text-center transition-all"
      :class="{
        'border-ink/40 bg-ink/5': isDragOver,
        'border-emerald-500/40 bg-emerald-500/5': uploadedFile,
        'border-rose-500/40 bg-rose-500/5': uploadError,
        'border-ink/20 hover:border-ink/40': !isDragOver && !uploadedFile && !uploadError
      }"
    >
      <input
        ref="fileInput"
        type="file"
        accept=".pdf"
        @change="handleFileSelect"
        class="hidden"
      />
      
      <div v-if="!uploadedFile && !uploading" class="space-y-3">
        <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-paper-dim text-ink-soft">
          <Upload class="h-5 w-5" />
        </div>
        <div>
          <p class="text-sm font-medium text-ink">Glissez votre CV (PDF) ici</p>
          <p class="mt-1 font-mono text-micro uppercase text-ink-soft">ou cliquez · max 10 Mo</p>
        </div>
      </div>

      <div v-else-if="uploading" class="space-y-3 py-2">
        <Loader2 class="mx-auto h-8 w-8 animate-spin text-ink-soft" />
        <p class="text-sm font-medium text-ink">Extraction du PDF...</p>
        <p class="font-mono text-micro uppercase text-ink-soft">Analyse en cours</p>
      </div>

      <div v-else-if="uploadedFile" class="space-y-3">
        <div class="w-10 h-10 rounded-full bg-emerald-500/10 text-emerald-500 flex items-center justify-center mx-auto">
          <CheckCircle class="h-5 w-5" />
        </div>
        <div>
          <p class="text-sm font-semibold text-foreground">
            CV extrait avec succès !
          </p>
          <p class="text-xs font-mono text-muted-foreground mt-1">
            {{ uploadedFile.name }} ({{ extractedText.length }} caractères)
          </p>
        </div>
        <Button variant="outline" size="sm" class="mt-2 text-xs" @click.stop="removeFile">
          Remplacer le fichier
        </Button>
      </div>

      <div v-else-if="uploadError" class="space-y-3">
        <div class="w-10 h-10 rounded-full bg-rose-500/10 text-rose-500 flex items-center justify-center mx-auto">
          <XCircle class="h-5 w-5" />
        </div>
        <div>
          <p class="text-sm font-semibold text-rose-500">
            Erreur lors de l'extraction
          </p>
          <p class="text-xs text-muted-foreground mt-1">
            {{ uploadError }}
          </p>
        </div>
        <Button variant="outline" size="sm" class="mt-2 text-xs" @click.stop="resetUpload">
          Réessayer
        </Button>
      </div>
    </div>

    <!-- Extracted Text Drawer / Preview -->
    <div v-if="extractedText && showPreview" class="mt-4 rounded-lg border border-ink/10 bg-paper-dim p-4">
      <div class="mb-2 flex items-center justify-between">
        <span class="field-label">Aperçu extrait</span>
        <button @click="showPreview = !showPreview" class="font-mono text-micro uppercase text-ink-soft hover:text-ink">
          {{ showPreview ? 'Masquer' : 'Afficher' }}
        </button>
      </div>
      <pre class="max-h-36 overflow-y-auto whitespace-pre-wrap font-mono text-xs leading-relaxed text-ink-soft">{{ extractedText }}</pre>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Button } from '@/components/ui/button'
import { Upload, CheckCircle, XCircle, Loader2 } from 'lucide-vue-next'
import { api } from '@/lib/api'
import posthog from 'posthog-js'

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
  if (!file.name.toLowerCase().endsWith('.pdf')) {
    uploadError.value = 'Seuls les fichiers PDF sont acceptés'
    return
  }

  if (file.size > 10 * 1024 * 1024) {
    uploadError.value = 'Le fichier dépasse la limite de 10MB'
    return
  }

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
      emit('update:modelValue', response.data.text)
      posthog.capture('cv_uploaded', { upload_source: 'pdf' })
      showPreview.value = true
    } else {
      uploadError.value = response.data.message
      uploadedFile.value = null
    }
  } catch (error: any) {
    uploadError.value = error.response?.data?.detail || 'Erreur lors de l\'extraction PDF'
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
