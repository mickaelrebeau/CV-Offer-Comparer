<template>
  <!-- « Mes candidatures » : liste ou Kanban, création -->
  <div class="space-y-8">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div class="flex gap-1 rounded-lg border border-ink/15 p-1" role="group" :aria-label="t('applications.viewMode')">
        <button
          v-for="mode in viewModes"
          :key="mode.value"
          type="button"
          :aria-pressed="view === mode.value"
          class="flex items-center gap-1.5 rounded px-3 py-1.5 font-mono text-micro uppercase transition-colors"
          :class="view === mode.value ? 'bg-ink text-paper' : 'text-ink-soft hover:text-ink'"
          @click="setView(mode.value)"
        >
          <component :is="mode.icon" class="h-3.5 w-3.5" aria-hidden="true" />
          {{ mode.label }}
        </button>
      </div>
      <Button size="sm" :aria-expanded="creating" @click="creating = !creating">
        <Plus class="h-3.5 w-3.5" aria-hidden="true" />
        {{ t('applications.new') }}
      </Button>
    </div>

    <form v-if="creating" class="panel overflow-hidden" @submit.prevent="submit">
      <div class="panel-header">{{ t('applications.new') }}</div>
      <div class="grid gap-4 p-4 sm:grid-cols-2 sm:p-5">
        <label class="space-y-1.5">
          <span class="field-label">{{ t('applications.fields.title') }}</span>
          <Input v-model="form.title" maxlength="200" :placeholder="t('applications.fields.titlePlaceholder')" />
        </label>
        <label class="space-y-1.5">
          <span class="field-label">{{ t('applications.fields.company') }}</span>
          <Input v-model="form.company" maxlength="200" />
        </label>
        <label class="space-y-1.5">
          <span class="field-label">{{ t('applications.fields.url') }}</span>
          <Input v-model="form.offer_url" type="url" inputmode="url" placeholder="https://" />
        </label>
        <label class="space-y-1.5">
          <span class="field-label">{{ t('applications.fields.status') }}</span>
          <select v-model="form.status" class="status-select w-full">
            <option v-for="status in APPLICATION_STATUSES" :key="status" :value="status">{{ t(`applications.status.${status}`) }}</option>
          </select>
        </label>
        <label v-if="context.hasOffer" class="flex items-start gap-2 text-sm text-ink sm:col-span-2">
          <input v-model="withContextOffer" type="checkbox" class="mt-1" />
          <span>
            {{ t('applications.withContextOffer') }}
            <span class="block text-xs text-ink-soft line-clamp-1">{{ context.offerText }}</span>
          </span>
        </label>
        <p v-if="createError" class="text-sm text-rose-700 sm:col-span-2" role="alert">{{ createError }}</p>
      </div>
      <div class="flex justify-end gap-2 border-t border-ink/10 px-4 py-3 sm:px-5">
        <Button type="button" size="sm" variant="outline" @click="creating = false">{{ t('common.cancel') }}</Button>
        <Button type="submit" size="sm" :disabled="saving || (!form.title.trim() && !(withContextOffer && context.hasOffer))">
          <Loader2 v-if="saving" class="h-3.5 w-3.5 animate-spin" aria-hidden="true" />
          {{ t('applications.create') }}
        </Button>
      </div>
    </form>

    <AppStatus v-if="store.loading && !store.loaded" kind="loading" :message="t('applications.loading')" />
    <AppStatus
      v-else-if="store.error"
      kind="error"
      :message="store.error"
      :action-label="t('common.retry')"
      @action="store.fetch"
    />
    <AppStatus
      v-else-if="!store.items.length"
      kind="empty"
      :message="t('applications.empty')"
      :action-label="t('applications.emptyCta')"
      @action="push('/compare')"
    />

    <!-- Liste -->
    <ul v-else-if="view === 'list'" class="space-y-3">
      <li
        v-for="item in store.items"
        :key="item.id"
        class="panel flex flex-col gap-4 p-5 sm:flex-row sm:items-center sm:justify-between"
      >
        <div class="min-w-0 flex-1">
          <p class="truncate font-medium text-ink">
            <RouterLink :to="localePath(`/applications?id=${item.id}`)" class="hover:underline">{{ item.title }}</RouterLink>
          </p>
          <p class="mt-0.5 truncate text-sm text-ink-soft">{{ item.company || t('applications.noCompany') }}</p>
          <p class="mt-2 flex flex-wrap gap-3 font-mono text-micro uppercase text-ink-soft">
            <span v-if="item.last_score !== null">{{ t('applications.lastScore', { value: formatPercent(item.last_score) }) }}</span>
            <span>{{ t('applications.counts', { analyses: item.comparison_count, letters: item.cover_letter_count, interviews: item.interview_count }) }}</span>
            <span>{{ t('applications.updatedAt', { date: formatDate(item.updated_at, { dateStyle: 'medium' }) }) }}</span>
          </p>
        </div>
        <label class="flex shrink-0 items-center gap-2">
          <span class="sr-only">{{ t('applications.statusOf', { title: item.title }) }}</span>
          <select
            class="status-select"
            :value="item.status"
            :disabled="updatingId === item.id"
            @change="changeStatus(item.id, ($event.target as HTMLSelectElement).value as ApplicationStatus)"
          >
            <option v-for="status in APPLICATION_STATUSES" :key="status" :value="status">{{ t(`applications.status.${status}`) }}</option>
          </select>
        </label>
      </li>
    </ul>

    <!-- Kanban : glisser-déposer, ou liste déroulante sur chaque carte (clavier, mobile) -->
    <div v-else class="-mx-5 overflow-x-auto px-5 sm:mx-0 sm:px-0">
      <div class="grid min-w-[60rem] grid-cols-5 gap-3">
        <section
          v-for="status in APPLICATION_STATUSES"
          :key="status"
          class="flex min-h-[12rem] flex-col rounded-xl border border-ink/10 bg-paper-dim/60 transition-colors"
          :class="{ 'border-ink/40 bg-ink/5': dropTarget === status }"
          :aria-label="t(`applications.status.${status}`)"
          @dragover.prevent="dropTarget = status"
          @dragleave="dropTarget = dropTarget === status ? null : dropTarget"
          @drop.prevent="drop(status)"
        >
          <h2 class="flex items-center justify-between px-3 py-2.5 font-mono text-micro uppercase text-ink-soft">
            <span>{{ t(`applications.status.${status}`) }}</span>
            <span class="tabular-nums">{{ columns[status].length }}</span>
          </h2>
          <ul class="flex-1 space-y-2 px-2 pb-2">
            <li
              v-for="item in columns[status]"
              :key="item.id"
              draggable="true"
              class="cursor-grab rounded-lg border border-ink/10 bg-paper p-3 shadow-sm active:cursor-grabbing"
              :class="{ 'opacity-50': draggedId === item.id }"
              @dragstart="draggedId = item.id"
              @dragend="draggedId = null; dropTarget = null"
            >
              <RouterLink :to="localePath(`/applications?id=${item.id}`)" class="block text-sm font-medium text-ink hover:underline">
                {{ item.title }}
              </RouterLink>
              <p v-if="item.company" class="mt-0.5 truncate text-xs text-ink-soft">{{ item.company }}</p>
              <p v-if="item.last_score !== null" class="mt-2 font-mono text-micro uppercase text-ink-soft">
                {{ t('applications.lastScore', { value: formatPercent(item.last_score) }) }}
              </p>
              <label class="mt-2 block">
                <span class="sr-only">{{ t('applications.statusOf', { title: item.title }) }}</span>
                <select
                  class="status-select w-full"
                  :value="item.status"
                  :disabled="updatingId === item.id"
                  @change="changeStatus(item.id, ($event.target as HTMLSelectElement).value as ApplicationStatus)"
                >
                  <option v-for="option in APPLICATION_STATUSES" :key="option" :value="option">{{ t(`applications.status.${option}`) }}</option>
                </select>
              </label>
            </li>
          </ul>
        </section>
      </div>
    </div>

    <p class="sr-only" aria-live="polite">{{ liveMessage }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Kanban, List, Loader2, Plus } from 'lucide-vue-next'
import AppStatus from '@/components/AppStatus.vue'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useLocale } from '@/i18n/useLocale'
import { APPLICATION_STATUSES, type Application, type ApplicationStatus } from '@/lib/api'
import { STORAGE_KEYS, readStorage } from '@/lib/storageKeys'
import { useApplicationContextStore } from '@/stores/applicationContext'
import { useApplicationsStore } from '@/stores/applications'

const emit = defineEmits<{ created: [id: string] }>()

const { t } = useI18n()
const { push, localePath, formatDate, formatPercent } = useLocale()
const store = useApplicationsStore()
const context = useApplicationContextStore()

// --- Affichage liste / Kanban (préférence locale) ---------------------------------
type ViewMode = 'list' | 'kanban'
const view = ref<ViewMode>(readStorage(STORAGE_KEYS.applicationsView) === 'kanban' ? 'kanban' : 'list')
const viewModes = computed(() => [
  { value: 'list' as const, label: t('applications.views.list'), icon: List },
  { value: 'kanban' as const, label: t('applications.views.kanban'), icon: Kanban },
])

function setView(mode: ViewMode) {
  view.value = mode
  try {
    localStorage.setItem(STORAGE_KEYS.applicationsView, mode)
  } catch {
    // Stockage indisponible : préférence non conservée
  }
}

const columns = computed(() =>
  Object.fromEntries(
    APPLICATION_STATUSES.map((status) => [status, store.items.filter((item) => item.status === status)]),
  ) as Record<ApplicationStatus, Application[]>,
)

// --- Changement de statut --------------------------------------------------------
const updatingId = ref<string | null>(null)
const draggedId = ref<string | null>(null)
const dropTarget = ref<ApplicationStatus | null>(null)
const liveMessage = ref('')

async function changeStatus(id: string, status: ApplicationStatus) {
  const item = store.items.find((application) => application.id === id)
  if (!item || item.status === status) return
  updatingId.value = id
  try {
    await store.setStatus(id, status)
    liveMessage.value = t('applications.statusChanged', { title: item.title, status: t(`applications.status.${status}`) })
  } catch (err: any) {
    store.error = err?.response?.data?.detail || t('applications.errors.update')
  } finally {
    updatingId.value = null
  }
}

function drop(status: ApplicationStatus) {
  if (draggedId.value) changeStatus(draggedId.value, status)
  draggedId.value = null
  dropTarget.value = null
}

// --- Création --------------------------------------------------------------------
const creating = ref(false)
const saving = ref(false)
const createError = ref('')
const withContextOffer = ref(true)
const form = reactive({ title: '', company: '', offer_url: '', status: 'to_apply' as ApplicationStatus })

async function submit() {
  saving.value = true
  createError.value = ''
  const useOffer = withContextOffer.value && context.hasOffer
  try {
    const created = await store.create(
      {
        title: form.title,
        company: form.company,
        offer_url: form.offer_url || (useOffer ? context.offerUrl : null),
        offer_text: useOffer ? context.offerText : '',
        status: form.status,
      },
      'manual',
    )
    // L'offre du contexte devient celle de la candidature : analyses et lettres suivantes rattachées
    if (useOffer) context.setApplication({ id: created.id, title: created.title })
    Object.assign(form, { title: '', company: '', offer_url: '', status: 'to_apply' })
    creating.value = false
    emit('created', created.id)
  } catch (err: any) {
    createError.value = err?.response?.data?.detail || t('applications.errors.create')
  } finally {
    saving.value = false
  }
}
</script>
