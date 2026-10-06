<template>
  <section id="saved-cvs" class="panel scroll-mt-24 space-y-5 p-6" aria-labelledby="saved-cvs-title">
    <div class="flex flex-wrap items-start justify-between gap-3 border-b border-ink/10 pb-3">
      <div class="space-y-2">
        <h2 id="saved-cvs-title" class="font-mono text-caption uppercase">{{ t('savedCvs.title') }}</h2>
        <p class="text-sm text-ink-soft">{{ t('savedCvs.description') }}</p>
      </div>
      <span v-if="savedCvs.loaded" class="font-mono text-micro uppercase text-ink-soft">
        {{ t('savedCvs.count', { count: savedCvs.items.length, max: savedCvs.limit }) }}
      </span>
    </div>

    <AppStatus v-if="savedCvs.loading && !savedCvs.loaded" kind="loading" :message="t('savedCvs.loading')" />
    <AppStatus
      v-else-if="savedCvs.error && !savedCvs.loaded"
      kind="error"
      :message="savedCvs.error"
      :action-label="t('common.retry')"
      @action="savedCvs.fetch(true)"
    />

    <template v-else-if="savedCvs.loaded">
      <p v-if="!savedCvs.items.length" class="text-sm text-ink-soft" role="status">{{ t('savedCvs.empty') }}</p>

      <ul v-else class="space-y-3" :aria-label="t('savedCvs.listAria')">
        <li
          v-for="cv in savedCvs.items"
          :key="cv.id"
          class="space-y-3 rounded-lg border p-4"
          :class="cv.is_default ? 'border-ink/40' : 'border-ink/15'"
        >
          <!-- Renommer -->
          <form
            v-if="editing?.id === cv.id && editing.mode === 'rename'"
            class="flex flex-col gap-2 sm:flex-row sm:items-end"
            @submit.prevent="rename(cv.id)"
          >
            <div class="min-w-0 flex-1 space-y-1">
              <label :for="`saved-cv-rename-${cv.id}`" class="field-label">{{ t('savedCvs.labelField') }}</label>
              <Input :id="`saved-cv-rename-${cv.id}`" v-model="draftLabel" maxlength="80" required class="h-9 py-1.5" />
            </div>
            <div class="flex shrink-0 gap-2">
              <Button type="submit" size="sm" :disabled="busyId !== null || !draftLabel.trim()">{{ t('savedCvs.save') }}</Button>
              <Button type="button" size="sm" variant="ghost" @click="editing = null">{{ t('common.cancel') }}</Button>
            </div>
          </form>

          <div v-else class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div class="min-w-0">
              <div class="flex flex-wrap items-center gap-2">
                <span class="text-sm font-medium text-ink">{{ cv.label }}</span>
                <span v-if="cv.is_default" class="rounded bg-ink px-1.5 py-0.5 font-mono text-micro uppercase text-paper">
                  {{ t('savedCvs.default') }}
                </span>
              </div>
              <p class="mt-1 truncate font-mono text-micro text-ink-soft">
                <template v-if="cv.source_filename">{{ cv.source_filename }} · </template>
                {{ t('savedCvs.chars', { count: cv.char_count }) }}
                <template v-if="cv.updated_at"> · {{ t('savedCvs.updatedAt', { date: formatDate(cv.updated_at, { dateStyle: 'medium' }) }) }}</template>
              </p>
              <p class="mt-2 line-clamp-2 text-xs text-ink-soft">{{ cv.excerpt }}</p>
            </div>
            <div class="flex shrink-0 flex-wrap gap-2">
              <Button
                v-if="!cv.is_default"
                variant="outline"
                size="sm"
                :disabled="busyId !== null || !isOnline"
                :aria-label="t('savedCvs.makeDefaultAria', { label: cv.label })"
                @click="makeDefault(cv.id)"
              >
                {{ t('savedCvs.makeDefault') }}
              </Button>
              <Button
                variant="outline"
                size="sm"
                :disabled="busyId !== null || !isOnline"
                :aria-label="t('savedCvs.renameAria', { label: cv.label })"
                @click="startEditing(cv.id, 'rename', cv.label)"
              >
                {{ t('savedCvs.rename') }}
              </Button>
              <Button
                variant="outline"
                size="sm"
                :disabled="busyId !== null || !isOnline"
                :aria-label="t('savedCvs.replaceAria', { label: cv.label })"
                @click="startEditing(cv.id, 'replace')"
              >
                {{ t('savedCvs.replace') }}
              </Button>
              <Button
                variant="ghost"
                size="sm"
                class="text-rose-700"
                :disabled="busyId !== null || !isOnline"
                :aria-label="t('savedCvs.deleteAria', { label: cv.label })"
                @click="remove(cv.id, cv.label)"
              >
                {{ t('savedCvs.delete') }}
              </Button>
            </div>
          </div>

          <!-- Remplacer : nouveau fichier, le nom et le statut par défaut sont conservés -->
          <div v-if="editing?.id === cv.id && editing.mode === 'replace'" class="space-y-2 border-t border-ink/10 pt-3">
            <p class="text-xs text-ink-soft">{{ t('savedCvs.replaceHint') }}</p>
            <PDFUpload allow-txt @loaded="(file) => replace(cv.id, file)" />
            <Button type="button" size="sm" variant="ghost" @click="editing = null">{{ t('common.cancel') }}</Button>
          </div>
        </li>
      </ul>

      <!-- Ajouter -->
      <p v-if="savedCvs.limitReached" class="text-sm text-ink-soft">{{ t('savedCvs.limitReached', { max: savedCvs.limit }) }}</p>
      <div v-else-if="adding" class="space-y-3 rounded-lg border border-dashed border-ink/20 p-4">
        <PDFUpload allow-txt @loaded="onNewFile" />
        <form v-if="newCv" class="flex flex-col gap-2 sm:flex-row sm:items-end" @submit.prevent="add">
          <div class="min-w-0 flex-1 space-y-1">
            <label for="saved-cv-new-label" class="field-label">{{ t('savedCvs.labelField') }}</label>
            <Input id="saved-cv-new-label" v-model="draftLabel" maxlength="80" required class="h-9 py-1.5" />
          </div>
          <Button type="submit" size="sm" :disabled="busyId !== null || !draftLabel.trim()">{{ t('savedCvs.save') }}</Button>
        </form>
        <Button type="button" size="sm" variant="ghost" @click="cancelAdd">{{ t('common.cancel') }}</Button>
      </div>
      <Button v-else variant="outline" size="sm" :disabled="!isOnline" @click="adding = true">
        <Plus class="h-3.5 w-3.5" aria-hidden="true" />
        {{ t('savedCvs.add') }}
      </Button>

      <p v-if="!isOnline" class="font-mono text-micro uppercase text-ink-soft">{{ t('savedCvs.offlineManage') }}</p>
      <p v-if="actionError" class="text-sm text-rose-700" role="alert">{{ actionError }}</p>
      <p class="sr-only" aria-live="polite">{{ liveMessage }}</p>
    </template>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Plus } from 'lucide-vue-next'
import AppStatus from '@/components/AppStatus.vue'
import PDFUpload from '@/components/PDFUpload.vue'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useLocale } from '@/i18n/useLocale'
import { isOnline } from '@/lib/pwa'
import { useSavedCvsStore } from '@/stores/savedCvs'

const { t } = useI18n()
const { formatDate } = useLocale()
const savedCvs = useSavedCvsStore()

const editing = ref<{ id: string; mode: 'rename' | 'replace' } | null>(null)
const draftLabel = ref('')
const busyId = ref<string | null>(null)
const actionError = ref('')
const liveMessage = ref('')
const adding = ref(false)
const newCv = ref<{ text: string; fileName: string } | null>(null)

function startEditing(id: string, mode: 'rename' | 'replace', label = '') {
  editing.value = { id, mode }
  draftLabel.value = label
  actionError.value = ''
}

/** Exécute une action sur un CV en affichant l'erreur traduite renvoyée par l'API */
async function run(id: string, action: () => Promise<unknown>, success: string) {
  busyId.value = id
  actionError.value = ''
  try {
    await action()
    liveMessage.value = success
    return true
  } catch (err: any) {
    actionError.value = err?.response?.data?.detail || t('savedCvs.errors.action')
    return false
  } finally {
    busyId.value = null
  }
}

async function rename(id: string) {
  const label = draftLabel.value.trim()
  if (await run(id, () => savedCvs.rename(id, label), t('savedCvs.renamed', { label }))) editing.value = null
}

async function replace(id: string, file: { text: string; fileName: string }) {
  if (await run(id, () => savedCvs.replace(id, file.text, file.fileName), t('savedCvs.replaced'))) {
    editing.value = null
  }
}

async function makeDefault(id: string) {
  await run(id, () => savedCvs.setDefault(id), t('savedCvs.defaultChanged'))
}

async function remove(id: string, label: string) {
  if (!window.confirm(t('savedCvs.deleteConfirm', { label }))) return
  await run(id, () => savedCvs.remove(id), t('savedCvs.deleted', { label }))
}

function onNewFile(file: { text: string; fileName: string }) {
  newCv.value = file
  draftLabel.value = file.fileName.replace(/\.(pdf|txt)$/i, '').trim().slice(0, 80) || t('savedCvs.defaultLabel')
}

function cancelAdd() {
  adding.value = false
  newCv.value = null
}

async function add() {
  const file = newCv.value
  if (!file) return
  const label = draftLabel.value.trim()
  const ok = await run(
    'new',
    () => savedCvs.create({ label, text: file.text, sourceFilename: file.fileName }, 'profile'),
    t('savedCvs.saved', { label }),
  )
  if (ok) cancelAdd()
}

onMounted(() => savedCvs.fetch(true))
</script>
