<template>
  <div class="w-full">
    <div
      @drop="handleDrop"
      @dragover="handleDragOver"
      @dragleave="handleDragLeave"
      @click="triggerFileInput"
      class="border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all relative overflow-hidden"
      :class="{
        'border-brand-500 bg-brand-500/5': isDragOver,
        'border-emerald-500/50 bg-emerald-500/5': uploadedFile,
        'border-rose-500/50 bg-rose-500/5': uploadError,
        'border-zinc-300 dark:border-zinc-700 hover:border-zinc-400 dark:hover:border-zinc-600 bg-card': !isDragOver && !uploadedFile && !uploadError
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
        <div class="w-12 h-12 rounded-full bg-zinc-100 dark:bg-zinc-800 text-muted-foreground flex items-center justify-center mx-auto">
          <Upload class="h-5 w-5" />
        </div>
        <div>
          <p class="text-sm font-semibold text-foreground">
            Glissez votre CV (PDF) ici
          </p>
          <p class="text-xs text-muted-foreground mt-1">
            ou cliquez pour parcourir vos fichiers (Max 10MB)
          </p>
        </div>
      </div>

      <div v-else-if="uploading" class="space-y-3 py-2">
        <Loader2 class="h-8 w-8 mx-auto animate-spin text-brand-500" />
        <p class="text-sm font-semibold text-foreground">
          Extraction du contenu PDF...
        </p>
        <p class="text-xs text-muted-foreground">
          Analyse sémantique du document en cours
        </p>
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
    <div v-if="extractedText && showPreview" class="mt-4 p-4 rounded-xl bg-zinc-100/50 dark:bg-zinc-900/50 border border-border">
      <div class="flex items-center justify-between mb-2">
        <span class="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Aperçu du texte extrait</span>
        <button @click="showPreview = !showPreview" class="text-xs text-muted-foreground hover:text-foreground">
          {{ showPreview ? 'Masquer' : 'Afficher' }}
        </button>
      </div>
      <pre class="text-xs text-muted-foreground whitespace-pre-wrap max-h-36 overflow-y-auto font-mono leading-relaxed">{{ extractedText }}</pre>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Button } from '@/components/ui/button'
import { Upload, CheckCircle, XCircle, Loader2 } from 'lucide-vue-next'
import { uploadFreeCV } from '@/lib/api'

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
    const result = await uploadFreeCV(file)

    if (result.success) {
      extractedText.value = result.text
      emit('update:modelValue', result.text)
      showPreview.value = true
    } else {
      uploadError.value = result.message
      uploadedFile.value = null
    }
  } catch (error: any) {
    uploadError.value = error.message || 'Erreur lors de l\'upload'
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
