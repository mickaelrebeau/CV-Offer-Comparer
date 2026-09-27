<template>
  <section id="llm-providers" class="panel scroll-mt-24 space-y-5 p-6" aria-labelledby="llm-providers-title">
    <div class="space-y-2 border-b border-ink/10 pb-3">
      <h2 id="llm-providers-title" class="font-mono text-caption uppercase">{{ t('llmProviders.title') }}</h2>
      <p class="text-sm text-ink-soft">{{ t('llmProviders.description') }}</p>
    </div>

    <AppStatus v-if="loading" kind="loading" :message="t('llmProviders.loading')" />
    <AppStatus
      v-else-if="loadError"
      kind="error"
      :message="loadError"
      :action-label="t('common.retry')"
      @action="load"
    />
    <p v-else-if="!byokEnabled" class="text-sm text-ink-soft" role="status">{{ t('llmProviders.disabled') }}</p>

    <template v-else>
      <!-- Configuration utilisée pour les analyses -->
      <div class="flex flex-wrap items-center justify-between gap-3 rounded-lg bg-paper-dim p-4">
        <div>
          <p class="field-label">{{ t('llmProviders.current') }}</p>
          <p class="mt-1 text-sm text-ink">
            {{ active ? t('llmProviders.currentUser', { provider: active.provider_label, model: active.model }) : t('llmProviders.currentPlatform') }}
          </p>
        </div>
        <Button v-if="active" variant="outline" size="sm" :disabled="busyId !== null" @click="usePlatform">
          {{ t('llmProviders.usePlatform') }}
        </Button>
      </div>

      <ul v-if="credentials.length" class="space-y-3" :aria-label="t('llmProviders.savedList')">
        <li
          v-for="credential in credentials"
          :key="credential.id"
          class="flex flex-col gap-3 rounded-lg border p-4 sm:flex-row sm:items-center sm:justify-between"
          :class="credential.is_active ? 'border-ink/40' : 'border-ink/15'"
        >
          <div class="min-w-0">
            <div class="flex flex-wrap items-center gap-2">
              <span class="text-sm font-medium text-ink">{{ credential.provider_label }}</span>
              <span v-if="credential.is_active" class="rounded bg-ink px-1.5 py-0.5 font-mono text-micro uppercase text-paper">
                {{ t('llmProviders.active') }}
              </span>
            </div>
            <p class="mt-1 truncate font-mono text-micro text-ink-soft">
              {{ credential.model }} · {{ credential.key_hint }}<template v-if="credential.base_url"> · {{ credential.base_url }}</template>
            </p>
          </div>
          <div class="flex shrink-0 flex-wrap gap-2">
            <Button
              v-if="!credential.is_active"
              variant="outline"
              size="sm"
              :disabled="busyId !== null"
              :aria-label="t('llmProviders.activateAria', { provider: credential.provider_label })"
              @click="activate(credential)"
            >
              {{ t('llmProviders.activate') }}
            </Button>
            <Button
              variant="outline"
              size="sm"
              :aria-label="t('llmProviders.editAria', { provider: credential.provider_label })"
              @click="edit(credential)"
            >
              {{ t('llmProviders.edit') }}
            </Button>
            <button
              type="button"
              class="h-9 rounded-lg px-3 font-mono text-micro uppercase text-rose-700 transition-colors hover:bg-rose-500/10"
              :disabled="busyId !== null"
              :aria-label="t('llmProviders.removeAria', { provider: credential.provider_label })"
              @click="remove(credential)"
            >
              {{ t('llmProviders.remove') }}
            </button>
          </div>
        </li>
      </ul>

      <!-- Ajout / remplacement d'une clé -->
      <form class="space-y-4 border-t border-ink/10 pt-5" autocomplete="off" @submit.prevent="save">
        <h3 class="font-mono text-micro uppercase text-ink">
          {{ existing ? t('llmProviders.form.editTitle', { provider: selected?.label }) : t('llmProviders.form.addTitle') }}
        </h3>

        <div class="space-y-1.5">
          <label for="llm-provider" class="field-label">{{ t('llmProviders.form.provider') }}</label>
          <select
            id="llm-provider"
            v-model="form.provider"
            :disabled="editing"
            class="w-full rounded-lg border border-ink/20 bg-paper px-3 py-2.5 text-sm text-ink focus:outline-none focus:ring-2 focus:ring-ink/60 disabled:opacity-60"
          >
            <option v-for="provider in providers" :key="provider.id" :value="provider.id">
              {{ provider.id === 'openai_compatible' ? t('llmProviders.form.compatible') : provider.label }}
            </option>
          </select>
          <a
            v-if="selected?.key_console_url"
            :href="selected.key_console_url"
            target="_blank"
            rel="noopener noreferrer"
            class="inline-block font-mono text-micro uppercase text-ink-soft underline-offset-4 hover:text-ink hover:underline"
          >
            {{ t('llmProviders.form.getKey', { provider: selected.label }) }}
            <span class="sr-only">{{ t('llmProviders.form.newTab') }}</span>
          </a>
          <p v-else-if="selected?.base_url_required" class="text-xs text-ink-soft">{{ t('llmProviders.form.compatibleHint') }}</p>
        </div>

        <div class="space-y-1.5">
          <label for="llm-api-key" class="field-label">{{ t('llmProviders.form.apiKey') }}</label>
          <Input
            id="llm-api-key"
            v-model="form.apiKey"
            class="pr-10"
            type="password"
            autocomplete="new-password"
            spellcheck="false"
            :show-password-toggle="true"
            :placeholder="existing ? t('llmProviders.form.keepKey', { hint: existing.key_hint }) : ''"
          />
        </div>

        <div class="space-y-1.5">
          <label for="llm-model" class="field-label">{{ t('llmProviders.form.model') }}</label>
          <Input id="llm-model" v-model="form.model" list="llm-model-suggestions" spellcheck="false" :placeholder="selected?.default_model || 'model-id'" />
          <datalist id="llm-model-suggestions">
            <option v-for="model in selected?.models || []" :key="model" :value="model" />
          </datalist>
        </div>

        <div v-if="selected?.base_url_editable" class="space-y-1.5">
          <button
            v-if="!selected.base_url_required && !showBaseUrl"
            type="button"
            class="font-mono text-micro uppercase text-ink-soft underline-offset-4 hover:text-ink hover:underline"
            @click="showBaseUrl = true"
          >
            {{ t('llmProviders.form.customUrl') }}
          </button>
          <template v-else>
            <label for="llm-base-url" class="field-label">{{ t('llmProviders.form.baseUrl') }}</label>
            <Input
              id="llm-base-url"
              v-model="form.baseUrl"
              type="url"
              inputmode="url"
              spellcheck="false"
              :placeholder="selected.default_base_url || 'https://api.example.com/v1'"
            />
            <p class="text-xs text-ink-soft">{{ t('llmProviders.form.baseUrlHint') }}</p>
          </template>
        </div>

        <div class="space-y-2">
          <label class="flex items-center gap-2 text-sm text-ink">
            <input v-model="form.verify" type="checkbox" class="h-4 w-4 accent-ink" />
            {{ t('llmProviders.form.verify') }}
          </label>
          <label class="flex items-center gap-2 text-sm text-ink">
            <input v-model="form.activate" type="checkbox" class="h-4 w-4 accent-ink" />
            {{ t('llmProviders.form.activate') }}
          </label>
        </div>

        <p v-if="formError" role="alert" class="rounded-lg border border-rose-500/25 bg-rose-500/5 p-3 font-mono text-micro text-rose-700">
          {{ formError }}
        </p>
        <p v-if="formSuccess" role="status" class="rounded-lg border border-emerald-500/25 bg-emerald-500/5 p-3 font-mono text-micro text-emerald-800">
          {{ formSuccess }}
        </p>

        <div class="flex flex-wrap gap-2">
          <Button type="submit" :disabled="saving || !canSubmit">
            <Loader2 v-if="saving" class="h-4 w-4 animate-spin" aria-hidden="true" />
            {{ saving && form.verify ? t('llmProviders.form.verifying') : t('llmProviders.form.save') }}
          </Button>
          <Button v-if="editing" type="button" variant="outline" @click="resetForm()">{{ t('common.cancel') }}</Button>
        </div>
      </form>

      <p class="border-t border-ink/10 pt-4 text-xs leading-relaxed text-ink-soft">{{ t('llmProviders.securityNote') }}</p>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Loader2 } from 'lucide-vue-next'
import posthog from 'posthog-js'
import AppStatus from '@/components/AppStatus.vue'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  activateLlmCredential,
  deactivateLlmCredentials,
  deleteLlmCredential,
  getLlmProviders,
  listLlmCredentials,
  saveLlmCredential,
  type LlmCredential,
  type LlmCredentialListing,
  type LlmProvider,
} from '@/lib/api'

const { t } = useI18n()

const loading = ref(true)
const loadError = ref('')
const byokEnabled = ref(false)
const providers = ref<LlmProvider[]>([])
const credentials = ref<LlmCredential[]>([])
const busyId = ref<string | null>(null)

// La clé saisie ne vit que dans ce formulaire : jamais stockée côté navigateur, vidée après envoi
const form = reactive({ provider: 'gemini', apiKey: '', model: '', baseUrl: '', verify: true, activate: true })
const editing = ref(false)
const showBaseUrl = ref(false)
const saving = ref(false)
const formError = ref('')
const formSuccess = ref('')

const active = computed(() => credentials.value.find((item) => item.is_active) || null)
const selected = computed(() => providers.value.find((provider) => provider.id === form.provider))
const existing = computed(() => credentials.value.find((item) => item.provider === form.provider) || null)
const canSubmit = computed(() => {
  if (!selected.value) return false
  if (!existing.value && !form.apiKey.trim()) return false
  if (selected.value.base_url_required && !form.baseUrl.trim()) return false
  return Boolean(form.model.trim() || selected.value.default_model)
})

function errorMessage(err: any, fallback: string) {
  return err?.response?.data?.detail || fallback
}

function applyListing(listing: LlmCredentialListing) {
  credentials.value = listing.items
}

async function load() {
  loading.value = true
  loadError.value = ''
  try {
    const [catalog, listing] = await Promise.all([getLlmProviders(), listLlmCredentials()])
    byokEnabled.value = catalog.byok_enabled
    providers.value = catalog.providers
    applyListing(listing)
    resetForm()
  } catch (err) {
    loadError.value = errorMessage(err, t('llmProviders.errors.load'))
  } finally {
    loading.value = false
  }
}

function resetForm(provider = form.provider) {
  editing.value = false
  Object.assign(form, { provider, apiKey: '', verify: true, activate: true })
  prefill()
}

/** Modèle / URL du provider choisi : ceux déjà enregistrés, sinon les valeurs par défaut. */
function prefill() {
  const current = existing.value
  form.model = current?.model || selected.value?.default_model || ''
  form.baseUrl = current?.base_url || ''
  showBaseUrl.value = Boolean(current?.base_url)
}

watch(
  () => form.provider,
  () => {
    form.apiKey = ''
    formError.value = ''
    formSuccess.value = ''
    prefill()
  },
)

function edit(credential: LlmCredential) {
  form.provider = credential.provider
  editing.value = true
  form.activate = credential.is_active
  prefill()
  document.getElementById('llm-api-key')?.focus()
}

async function save() {
  if (!canSubmit.value || !selected.value) return
  saving.value = true
  formError.value = ''
  formSuccess.value = ''
  const isUpdate = Boolean(existing.value)
  try {
    const saved = await saveLlmCredential({
      provider: form.provider,
      api_key: form.apiKey.trim() || undefined,
      model: form.model.trim() || selected.value.default_model,
      base_url: form.baseUrl.trim() || null,
      activate: form.activate,
      verify: form.verify,
    })
    posthog.capture('llm_credential_saved', {
      provider: saved.provider,
      is_update: isUpdate,
      verified: form.verify,
      activated: saved.is_active,
    })
    applyListing(await listLlmCredentials())
    formSuccess.value = saved.is_active
      ? t('llmProviders.savedActive', { provider: saved.provider_label })
      : t('llmProviders.savedInactive', { provider: saved.provider_label })
    resetForm(saved.provider)
  } catch (err) {
    formError.value = errorMessage(err, t('llmProviders.errors.save'))
  } finally {
    // Même en cas d'erreur, la clé n'est pas conservée dans le champ
    form.apiKey = ''
    saving.value = false
  }
}

async function activate(credential: LlmCredential) {
  busyId.value = credential.id
  try {
    applyListing(await activateLlmCredential(credential.id))
    posthog.capture('llm_credential_activated', { provider: credential.provider, source: 'profile' })
  } catch (err) {
    formError.value = errorMessage(err, t('llmProviders.errors.action'))
  } finally {
    busyId.value = null
  }
}

async function usePlatform() {
  busyId.value = 'platform'
  try {
    applyListing(await deactivateLlmCredentials())
    posthog.capture('llm_credential_deactivated', { source: 'profile' })
  } catch (err) {
    formError.value = errorMessage(err, t('llmProviders.errors.action'))
  } finally {
    busyId.value = null
  }
}

async function remove(credential: LlmCredential) {
  if (!window.confirm(t('llmProviders.removeConfirm', { provider: credential.provider_label }))) return
  busyId.value = credential.id
  try {
    applyListing(await deleteLlmCredential(credential.id))
    posthog.capture('llm_credential_removed', { provider: credential.provider })
    if (form.provider === credential.provider) resetForm()
  } catch (err) {
    formError.value = errorMessage(err, t('llmProviders.errors.action'))
  } finally {
    busyId.value = null
  }
}

onMounted(load)
</script>
