<template>
  <!-- Fiche candidature : informations, statut, notes, offre et éléments rattachés -->
  <div class="space-y-8">
    <RouterLink :to="localePath('/applications')" class="inline-flex items-center gap-1.5 font-mono text-micro uppercase text-ink-soft hover:text-ink">
      <ArrowLeft class="h-3.5 w-3.5" aria-hidden="true" />
      {{ t('applications.back') }}
    </RouterLink>

    <AppStatus v-if="loading" kind="loading" :message="t('applications.detailLoading')" />
    <AppStatus
      v-else-if="loadError"
      kind="error"
      :message="loadError"
      :action-label="t('common.retry')"
      @action="load"
    />

    <template v-else-if="application">
      <!-- Utiliser la candidature dans les modules -->
      <div class="panel flex flex-col gap-4 p-5 sm:flex-row sm:items-center sm:justify-between">
        <div class="min-w-0">
          <p class="font-mono text-micro uppercase text-ink-soft">
            {{ isCurrent ? t('applications.current') : t('applications.useLabel') }}
          </p>
          <p class="mt-1 text-sm text-ink">{{ t('applications.useText') }}</p>
        </div>
        <div class="flex shrink-0 flex-wrap gap-2">
          <Button
            v-for="action in moduleActions"
            :key="action.path"
            size="sm"
            :variant="action.primary ? 'default' : 'outline'"
            :disabled="!application.offer_text.trim()"
            @click="openModule(action.path)"
          >
            <component :is="action.icon" class="h-3.5 w-3.5" aria-hidden="true" />
            {{ action.label }}
          </Button>
        </div>
      </div>

      <form class="panel overflow-hidden" @submit.prevent="save">
        <div class="panel-header justify-between">
          <span>{{ t('applications.detailTitle') }}</span>
          <span v-if="application.applied_at">{{ t('applications.appliedOn', { date: formatDate(application.applied_at, { dateStyle: 'medium' }) }) }}</span>
        </div>
        <div class="grid gap-4 p-4 sm:grid-cols-2 sm:p-5">
          <label class="space-y-1.5">
            <span class="field-label">{{ t('applications.fields.title') }}</span>
            <Input v-model="form.title" maxlength="200" required />
          </label>
          <label class="space-y-1.5">
            <span class="field-label">{{ t('applications.fields.company') }}</span>
            <Input v-model="form.company" maxlength="200" />
          </label>
          <label class="space-y-1.5">
            <span class="field-label">{{ t('applications.fields.url') }}</span>
            <Input v-model="form.offer_url" type="url" inputmode="url" placeholder="https://" />
            <a
              v-if="safeHttpUrl(application.offer_url)"
              :href="safeHttpUrl(application.offer_url) || undefined"
              target="_blank"
              rel="noopener noreferrer"
              class="inline-block font-mono text-micro text-ink-soft underline underline-offset-4 hover:text-ink"
            >{{ t('applications.openOffer', { domain: offerDomain(application.offer_url) }) }}</a>
          </label>
          <label class="space-y-1.5">
            <span class="field-label">{{ t('applications.fields.status') }}</span>
            <select v-model="form.status" class="status-select w-full">
              <option v-for="status in APPLICATION_STATUSES" :key="status" :value="status">{{ t(`applications.status.${status}`) }}</option>
            </select>
          </label>
          <label class="space-y-1.5 sm:col-span-2">
            <span class="field-label">{{ t('applications.fields.notes') }}</span>
            <Textarea v-model="form.notes" class="min-h-[96px]" maxlength="10000" :placeholder="t('applications.fields.notesPlaceholder')" />
          </label>
          <details class="sm:col-span-2" :open="!application.offer_text.trim()">
            <summary class="field-label cursor-pointer">{{ t('applications.fields.offer') }}</summary>
            <Textarea v-model="form.offer_text" class="mt-2 min-h-[160px]" maxlength="50000" :placeholder="t('applications.fields.offerPlaceholder')" />
          </details>
          <p v-if="saveError" class="text-sm text-rose-700 sm:col-span-2" role="alert">{{ saveError }}</p>
        </div>
        <div class="flex flex-wrap items-center justify-between gap-2 border-t border-ink/10 px-4 py-3 sm:px-5">
          <button
            type="button"
            class="h-9 rounded-lg px-3 font-mono text-micro uppercase text-rose-700 transition-colors hover:bg-rose-500/10"
            :disabled="deleting"
            @click="remove"
          >
            {{ t('applications.delete') }}
          </button>
          <div class="flex items-center gap-3">
            <span v-if="savedMessage" class="font-mono text-micro uppercase text-emerald-700" role="status">{{ savedMessage }}</span>
            <Button type="submit" size="sm" :disabled="saving || !dirty || !form.title.trim()">
              <Loader2 v-if="saving" class="h-3.5 w-3.5 animate-spin" aria-hidden="true" />
              {{ t('applications.save') }}
            </Button>
          </div>
        </div>
      </form>

      <!-- Analyses, lettres et simulations rattachées -->
      <section class="grid gap-4 lg:grid-cols-3" :aria-label="t('applications.linked')">
        <div v-for="group in linkedGroups" :key="group.key" class="panel overflow-hidden">
          <div class="panel-header justify-between">
            <span>{{ group.title }}</span>
            <span class="tabular-nums">{{ group.items.length }}</span>
          </div>
          <p v-if="!group.items.length" class="p-4 text-sm text-ink-soft sm:p-5">{{ group.empty }}</p>
          <ul v-else class="divide-y divide-ink/10">
            <li v-for="item in group.items" :key="item.id">
              <RouterLink
                :to="localePath(`${group.path}?history=${item.id}`)"
                class="flex items-center justify-between gap-3 px-4 py-3 text-sm hover:bg-ink/5 sm:px-5"
              >
                <span class="min-w-0 truncate text-ink">{{ item.label }}</span>
                <span class="shrink-0 font-mono text-micro uppercase text-ink-soft">{{ formatDate(item.created_at, { dateStyle: 'short' }) }}</span>
              </RouterLink>
            </li>
          </ul>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ArrowLeft, ArrowRightLeft, Loader2, MessageSquare, PenLine, Sparkles } from 'lucide-vue-next'
import AppStatus from '@/components/AppStatus.vue'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { useLocale } from '@/i18n/useLocale'
import { APPLICATION_STATUSES, getApplication, type ApplicationDetail, type ApplicationStatus } from '@/lib/api'
import { offerDomain, safeHttpUrl } from '@/lib/jobOffer'
import { useApplicationContextStore } from '@/stores/applicationContext'
import { useApplicationsStore } from '@/stores/applications'

const props = defineProps<{ id: string }>()

const { t } = useI18n()
const { push, localePath, formatDate, formatPercent, formatNumber } = useLocale()
const store = useApplicationsStore()
const context = useApplicationContextStore()

const application = ref<ApplicationDetail | null>(null)
const loading = ref(false)
const loadError = ref('')
const form = reactive({ title: '', company: '', offer_url: '', status: 'to_apply' as ApplicationStatus, notes: '', offer_text: '' })

function fill(detail: ApplicationDetail) {
  application.value = detail
  Object.assign(form, {
    title: detail.title,
    company: detail.company,
    offer_url: detail.offer_url || '',
    status: detail.status,
    notes: detail.notes,
    offer_text: detail.offer_text,
  })
}

async function load() {
  loading.value = true
  loadError.value = ''
  try {
    fill(await getApplication(props.id))
  } catch (err: any) {
    loadError.value = err?.response?.data?.detail || t('applications.errors.loadOne')
  } finally {
    loading.value = false
  }
}

watch(() => props.id, load, { immediate: true })

const isCurrent = computed(() => context.applicationId === props.id)

const dirty = computed(() => {
  const current = application.value
  if (!current) return false
  return (
    form.title !== current.title ||
    form.company !== current.company ||
    form.offer_url !== (current.offer_url || '') ||
    form.status !== current.status ||
    form.notes !== current.notes ||
    form.offer_text !== current.offer_text
  )
})

// --- Enregistrement ----------------------------------------------------------------
const saving = ref(false)
const saveError = ref('')
const savedMessage = ref('')

async function save() {
  if (!application.value) return
  saving.value = true
  saveError.value = ''
  savedMessage.value = ''
  try {
    const offerChanged = form.offer_text !== application.value.offer_text
    fill(
      await store.update(props.id, {
        title: form.title,
        company: form.company,
        offer_url: form.offer_url || null,
        status: form.status,
        notes: form.notes,
        offer_text: form.offer_text,
      }),
    )
    // Offre modifiée d'une candidature en cours d'utilisation : le contexte suit
    if (offerChanged && isCurrent.value) store.select(application.value!)
    savedMessage.value = t('applications.saved')
  } catch (err: any) {
    saveError.value = err?.response?.data?.detail || t('applications.errors.update')
  } finally {
    saving.value = false
  }
}

// --- Suppression ------------------------------------------------------------------
const deleting = ref(false)

async function remove() {
  if (!application.value || !window.confirm(t('applications.deleteConfirm', { title: application.value.title }))) return
  deleting.value = true
  try {
    await store.remove(props.id)
    push('/applications')
  } catch (err: any) {
    saveError.value = err?.response?.data?.detail || t('applications.errors.delete')
    deleting.value = false
  }
}

// --- Modules : l'offre de la candidature devient celle du contexte ----------------------
const moduleActions = computed(() => [
  { path: '/compare', label: t('applications.actions.analyze'), icon: ArrowRightLeft, primary: true },
  { path: '/cv-optimizer', label: t('applications.actions.optimize'), icon: Sparkles, primary: false },
  { path: '/cover-letter', label: t('applications.actions.letter'), icon: PenLine, primary: false },
  { path: '/interview-simulator', label: t('applications.actions.interview'), icon: MessageSquare, primary: false },
])

function openModule(path: string) {
  if (!application.value) return
  store.select(application.value)
  push(path)
}

const linkedGroups = computed(() => {
  const detail = application.value
  if (!detail) return []
  return [
    {
      key: 'comparisons',
      title: t('applications.linkedAnalyses'),
      empty: t('applications.noAnalyses'),
      path: '/compare',
      items: detail.comparisons.map((item) => ({
        id: item.id,
        created_at: item.created_at,
        label: t('applications.analysisLabel', { value: formatPercent(item.match_percentage), matches: item.matches, total: item.total_items }),
      })),
    },
    {
      key: 'cover_letters',
      title: t('applications.linkedLetters'),
      empty: t('applications.noLetters'),
      path: '/cover-letter',
      items: detail.cover_letters.map((item) => ({
        id: item.id,
        created_at: item.created_at,
        label: item.subject || t('applications.letterLabel', { count: item.word_count }),
      })),
    },
    {
      key: 'interviews',
      title: t('applications.linkedInterviews'),
      empty: t('applications.noInterviews'),
      path: '/interview-results',
      items: detail.interviews.map((item) => ({
        id: item.id,
        created_at: item.created_at,
        label: t('applications.interviewLabel', { score: formatNumber(item.score_global, { maximumFractionDigits: 1 }), count: item.num_questions }),
      })),
    },
  ]
})
</script>
