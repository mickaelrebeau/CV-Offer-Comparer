<template>
  <div class="w-full">
    <div
      @drop="handleDrop"
      @dragover="handleDragOver"
      @dragleave="handleDragLeave"
      @click="triggerFileInput"
      @keydown.enter.prevent="isIdle && triggerFileInput()"
      @keydown.space.prevent="isIdle && triggerFileInput()"
      :role="isIdle ? 'button' : undefined"
      :tabindex="isIdle ? 0 : undefined"
      :aria-label="isIdle ? t('upload.dropAria') : undefined"
      class="cursor-pointer rounded-lg border-2 border-dashed p-8 text-center transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ink/60"
      :class="{
        'border-ink/40 bg-ink/5': isDragOver,
        'border-emerald-500/40 bg-emerald-500/5': displayedFileName,
        'border-rose-500/40 bg-rose-500/5': uploadError,
        'border-ink/20 hover:border-ink/40': !isDragOver && !displayedFileName && !uploadError
      }"
    >
      <input
        ref="fileInput"
        type="file"
        :accept="CV_ACCEPT"
        @change="handleFileSelect"
        class="hidden"
        tabindex="-1"
        aria-hidden="true"
      />
      
      <div v-if="!displayedFileName && !uploading" class="space-y-3">
        <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-paper-dim text-ink-soft">
          <Upload class="h-5 w-5" aria-hidden="true" />
        </div>
        <div>
          <p class="text-sm font-medium text-ink">{{ t('upload.dropTitle') }}</p>
          <p class="mt-1 font-mono text-micro uppercase text-ink-soft">{{ t('upload.dropHint') }}</p>
        </div>
      </div>

      <div v-else-if="uploading" class="space-y-3 py-2">
        <Loader2 class="mx-auto h-8 w-8 animate-spin text-ink-soft" aria-hidden="true" />
        <p class="text-sm font-medium text-ink">{{ t('upload.extracting') }}</p>
        <p class="font-mono text-micro uppercase text-ink-soft">{{ t('upload.extractingHint') }}</p>
      </div>

      <div v-else-if="displayedFileName" class="space-y-3">
        <div class="w-10 h-10 rounded-full bg-emerald-500/10 text-emerald-500 flex items-center justify-center mx-auto">
          <CheckCircle class="h-5 w-5" aria-hidden="true" />
        </div>
        <div>
          <p class="text-sm font-semibold text-foreground">
            {{ t('upload.success') }}
          </p>
          <p class="text-xs font-mono text-muted-foreground mt-1">
            {{ t('upload.fileInfo', { name: displayedFileName, count: (extractedText || modelValue || '').length }) }}
          </p>
        </div>
        <Button variant="outline" size="sm" class="mt-2 text-xs" @click.stop="removeFile">
          {{ t('upload.replace') }}
        </Button>
      </div>

      <div v-else-if="uploadError" class="space-y-3">
        <div class="w-10 h-10 rounded-full bg-rose-500/10 text-rose-500 flex items-center justify-center mx-auto">
          <XCircle class="h-5 w-5" aria-hidden="true" />
        </div>
        <div>
          <p class="text-sm font-semibold text-rose-700">
            {{ t('upload.errorTitle') }}
          </p>
          <p class="text-xs text-muted-foreground mt-1">
            {{ uploadError }}
          </p>
        </div>
        <Button variant="outline" size="sm" class="mt-2 text-xs" @click.stop="resetUpload">
          {{ t('common.retry') }}
        </Button>
      </div>
    </div>

    <p class="sr-only" aria-live="polite">{{ liveMessage }}</p>

    <!-- Extracted Text Drawer / Preview -->
    <div v-if="extractedText && showPreview" class="mt-4 rounded-lg border border-ink/10 bg-paper-dim p-4">
      <div class="mb-2 flex items-center justify-between">
        <span class="field-label">{{ t('upload.preview') }}</span>
        <button type="button" :aria-expanded="showPreview" @click="showPreview = !showPreview" class="font-mono text-micro uppercase text-ink-soft hover:text-ink">
          {{ showPreview ? t('upload.hide') : t('upload.show') }}
        </button>
      </div>
      <pre class="max-h-36 overflow-y-auto whitespace-pre-wrap font-mono text-xs leading-relaxed text-ink-soft">{{ extractedText }}</pre>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import { Upload, CheckCircle, XCircle, Loader2 } from 'lucide-vue-next'
import { api } from '@/lib/api'
import { CV_ACCEPT, MAX_CV_FILE_SIZE, cvExtension } from '@/lib/cvFile'
import posthog from 'posthog-js'

interface Props {
  modelValue?: string
  /** Nom du fichier déjà importé (contexte partagé) : affiché tant que le texte n'a pas changé */
  fileName?: string | null
}

interface Emits {
  (e: 'update:modelValue', value: string): void
  (e: 'update:fileName', value: string | null): void
  /** Texte extrait avec le nom du fichier, en un seul événement */
  (e: 'loaded', value: { text: string; fileName: string }): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const { t } = useI18n()
const fileInput = ref<HTMLInputElement>()
const isDragOver = ref(false)
const uploading = ref(false)
const uploadedFile = ref<File | null>(null)
const uploadError = ref<string | null>(null)
const extractedText = ref('')
const showPreview = ref(false)

const displayedFileName = computed(
  () => uploadedFile.value?.name ?? (props.modelValue && props.fileName ? props.fileName : null),
)
const isIdle = computed(() => !displayedFileName.value && !uploading.value && !uploadError.value)

// Annonce l'état de l'upload aux lecteurs d'écran
const liveMessage = computed(() => {
  if (uploading.value) return t('upload.live.extracting')
  if (uploadError.value) return t('upload.live.error', { message: uploadError.value })
  if (displayedFileName.value) return t('upload.live.success', { name: displayedFileName.value })
  return ''
})

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
  const extension = cvExtension(file.name)
  if (!extension) {
    uploadError.value = t('upload.unsupportedFormat')
    return
  }

  if (file.size > MAX_CV_FILE_SIZE) {
    uploadError.value = t('upload.tooLarge')
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
      emit('update:fileName', file.name)
      emit('loaded', { text: response.data.text, fileName: file.name })
      posthog.capture('cv_uploaded', { upload_source: extension })
      showPreview.value = true
    } else {
      uploadError.value = response.data.message
      uploadedFile.value = null
    }
  } catch (error: any) {
    uploadError.value = error.response?.data?.detail || t('upload.extractError')
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
  emit('update:fileName', null)
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
