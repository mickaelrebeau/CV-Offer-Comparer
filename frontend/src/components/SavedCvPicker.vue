<template>
  <!-- « Mes CV » : choisir un CV enregistré, ou enregistrer le CV saisi pour le réutiliser -->
  <div class="space-y-3">
    <div v-if="savedCvs.items.length" class="flex flex-col gap-2 sm:flex-row sm:items-center">
      <label :for="selectId" class="field-label shrink-0">{{ t('savedCvs.picker.label') }}</label>
      <select
        :id="selectId"
        class="h-9 w-full min-w-0 rounded-lg border border-ink/20 bg-paper px-2 text-sm text-ink focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ink/60 disabled:opacity-50"
        :value="selectedId"
        :disabled="selecting"
        @change="onSelect"
      >
        <option value="" disabled>{{ t('savedCvs.picker.placeholder') }}</option>
        <option
          v-for="cv in savedCvs.items"
          :key="cv.id"
          :value="cv.id"
          :disabled="!isOnline && !savedCvs.isCached(cv.id)"
        >
          {{ cv.is_default ? t('savedCvs.picker.defaultOption', { label: cv.label }) : cv.label }}
        </option>
      </select>
      <Loader2 v-if="selecting" class="h-4 w-4 shrink-0 animate-spin text-ink-soft" aria-hidden="true" />
    </div>
    <p v-else-if="savedCvs.loading" class="font-mono text-micro uppercase text-ink-soft">
      {{ t('savedCvs.picker.loading') }}
    </p>
    <p v-else-if="savedCvs.error && !isOnline" class="font-mono text-micro uppercase text-ink-soft">
      {{ t('savedCvs.picker.offline') }}
    </p>
    <p v-else-if="savedCvs.error" class="flex flex-wrap items-center gap-2 font-mono text-micro uppercase text-rose-700">
      {{ savedCvs.error }}
      <button type="button" class="uppercase underline underline-offset-4" @click="savedCvs.fetch(true)">
        {{ t('common.retry') }}
      </button>
    </p>
    <p v-else-if="savedCvs.loaded && !context.hasCv" class="text-xs text-ink-soft">{{ t('savedCvs.picker.empty') }}</p>

    <!-- Enregistrer le CV courant (importé ou saisi), s'il ne vient pas déjà de « Mes CV » -->
    <template v-if="canSave">
      <p v-if="savedCvs.limitReached" class="text-xs text-ink-soft">
        {{ t('savedCvs.limitReached', { max: savedCvs.limit }) }}
        <RouterLink :to="localePath('/profile') + '#saved-cvs'" class="underline underline-offset-4">
          {{ t('savedCvs.manage') }}
        </RouterLink>
      </p>
      <form v-else-if="saving" class="flex flex-col gap-2 sm:flex-row sm:items-end" @submit.prevent="save">
        <div class="min-w-0 flex-1 space-y-1">
          <label :for="labelId" class="field-label">{{ t('savedCvs.labelField') }}</label>
          <Input :id="labelId" v-model="label" maxlength="80" required class="h-9 py-1.5" />
        </div>
        <div class="flex shrink-0 gap-2">
          <Button type="submit" size="sm" :disabled="busy || !label.trim() || !isOnline">
            <Loader2 v-if="busy" class="h-3.5 w-3.5 animate-spin" aria-hidden="true" />
            {{ t('savedCvs.save') }}
          </Button>
          <Button type="button" size="sm" variant="ghost" :disabled="busy" @click="saving = false">
            {{ t('common.cancel') }}
          </Button>
        </div>
      </form>
      <Button v-else type="button" size="sm" variant="outline" :disabled="!isOnline" @click="startSaving">
        <BookmarkPlus class="h-3.5 w-3.5" aria-hidden="true" />
        {{ t('savedCvs.saveThis') }}
      </Button>
      <p v-if="!isOnline && !savedCvs.limitReached" class="font-mono text-micro uppercase text-ink-soft">
        {{ t('savedCvs.offlineSave') }}
      </p>
    </template>

    <p v-if="actionError" class="text-xs text-rose-700" role="alert">{{ actionError }}</p>
    <p class="sr-only" aria-live="polite">{{ liveMessage }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, ref, useId } from 'vue'
import { useI18n } from 'vue-i18n'
import { BookmarkPlus, Loader2 } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useLocale } from '@/i18n/useLocale'
import { isOnline } from '@/lib/pwa'
import { useApplicationContextStore, type ContextModule } from '@/stores/applicationContext'
import { useSavedCvsStore } from '@/stores/savedCvs'

const props = defineProps<{ module: ContextModule }>()

const { t } = useI18n()
const { localePath } = useLocale()
const context = useApplicationContextStore()
const savedCvs = useSavedCvsStore()

const uid = useId()
const selectId = `saved-cv-select-${uid}`
const labelId = `saved-cv-label-${uid}`

const selecting = ref(false)
const saving = ref(false)
const busy = ref(false)
const label = ref('')
const actionError = ref('')
const liveMessage = ref('')

const selectedId = computed(() =>
  context.savedCvId && savedCvs.items.some((cv) => cv.id === context.savedCvId) ? context.savedCvId : '',
)
const canSave = computed(() => savedCvs.loaded && context.hasCv && !selectedId.value)

async function onSelect(event: Event) {
  const select = event.target as HTMLSelectElement
  const id = select.value
  if (!id) return
  selecting.value = true
  actionError.value = ''
  try {
    await savedCvs.select(id, props.module)
    const cv = savedCvs.items.find((item) => item.id === id)
    liveMessage.value = t('savedCvs.picker.selected', { label: cv?.label ?? '' })
  } catch (err: any) {
    actionError.value = err?.response?.data?.detail || t('savedCvs.errors.select')
    select.value = selectedId.value
  } finally {
    selecting.value = false
  }
}

/** Libellé proposé : nom du fichier sans extension, sinon « Mon CV » */
function suggestedLabel() {
  const fromFile = (context.cvFileName || '').replace(/\.(pdf|txt)$/i, '').trim()
  return (fromFile || t('savedCvs.defaultLabel')).slice(0, 80)
}

async function startSaving() {
  label.value = suggestedLabel()
  actionError.value = ''
  saving.value = true
  await nextTick()
  const input = document.getElementById(labelId) as HTMLInputElement | null
  input?.select()
}

async function save() {
  busy.value = true
  actionError.value = ''
  try {
    const created = await savedCvs.create(
      { label: label.value.trim(), text: context.cvText, sourceFilename: context.cvFileName },
      props.module,
    )
    // Le contexte est désormais rattaché au CV enregistré
    context.savedCvId = created.id
    saving.value = false
    liveMessage.value = t('savedCvs.saved', { label: created.label })
  } catch (err: any) {
    actionError.value = err?.response?.data?.detail || t('savedCvs.errors.save')
  } finally {
    busy.value = false
  }
}

onMounted(() => savedCvs.fetch())
</script>
