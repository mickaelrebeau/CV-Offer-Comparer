<template>
  <!-- Offre d'emploi : texte collé ou importé depuis l'URL de l'annonce (contexte partagé) -->
  <div class="panel overflow-hidden">
    <div class="panel-header justify-between">
      <span :id="labelId">{{ t('cvInput.offerHeader') }}</span>
      <div class="flex gap-1" role="group" :aria-label="t('offerInput.mode')">
        <button
          v-for="option in tabs"
          :key="option.value"
          type="button"
          :aria-pressed="tab === option.value"
          class="rounded px-2 py-0.5 transition-colors"
          :class="tab === option.value ? 'bg-ink text-paper' : 'text-ink-soft hover:text-ink'"
          @click="tab = option.value"
        >
          {{ option.label }}
        </button>
      </div>
    </div>

    <div class="p-4 sm:p-5">
      <!-- Coller le texte -->
      <template v-if="tab === 'paste'">
        <Textarea
          :id="textareaId"
          :aria-labelledby="labelId"
          :model-value="context.offerText"
          :placeholder="placeholder"
          :class="minHeightClass"
          @update:model-value="(value) => context.setOffer(String(value), { from: module })"
        />
        <p v-if="sourceUrl" class="mt-3 flex flex-wrap items-center gap-2 font-mono text-micro uppercase text-ink-soft">
          <Link2 class="h-3.5 w-3.5" aria-hidden="true" />
          {{ t('offerInput.source') }}
          <a :href="sourceUrl" target="_blank" rel="noopener noreferrer" class="normal-case text-ink underline underline-offset-4">
            {{ offerDomain(sourceUrl) }}
          </a>
          <button type="button" class="uppercase hover:text-ink" @click="detachUrl">· {{ t('offerInput.detach') }}</button>
        </p>
      </template>

      <!-- Importer depuis une URL -->
      <template v-else>
        <form v-if="!draft" class="space-y-3" @submit.prevent="importFromUrl(false)">
          <label :for="urlId" class="field-label">{{ t('offerInput.urlLabel') }}</label>
          <div class="flex flex-col gap-2 sm:flex-row">
            <Input
              :id="urlId"
              v-model="url"
              type="url"
              inputmode="url"
              autocomplete="url"
              :placeholder="t('offerInput.urlPlaceholder')"
              class="h-10 py-2"
              :disabled="importing"
              required
            />
            <Button type="submit" :disabled="importing || !url.trim() || !isOnline" class="shrink-0">
              <Loader2 v-if="importing" class="h-4 w-4 animate-spin" aria-hidden="true" />
              <Download v-else class="h-4 w-4" aria-hidden="true" />
              {{ importing ? t('offerInput.importing') : t('offerInput.import') }}
            </Button>
          </div>
          <p class="text-xs text-ink-soft">
            {{ t('offerInput.urlHint') }}
            <RouterLink :to="localePath('/import')" class="text-ink underline underline-offset-4">
              {{ t('offerInput.assisted.bookmarkletInstall') }}
            </RouterLink>
          </p>
          <p v-if="!isOnline" class="font-mono text-micro uppercase text-ink-soft">{{ t('offerInput.offline') }}</p>
        </form>

        <!-- Aperçu éditable -->
        <div v-else class="space-y-4">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <p class="flex flex-wrap items-center gap-2 font-mono text-micro uppercase text-ink-soft">
              <CheckCircle class="h-3.5 w-3.5 text-emerald-600" aria-hidden="true" />
              {{ t(`offerInput.methods.${method === 'json-ld' ? 'jsonLd' : method}`) }}
              <a :href="sourceUrl || undefined" target="_blank" rel="noopener noreferrer" class="normal-case text-ink underline underline-offset-4">
                {{ offerDomain(sourceUrl) }}
              </a>
            </p>
            <div class="flex flex-wrap gap-2">
              <Button
                v-if="method === 'html' || method === 'paste'"
                type="button"
                size="sm"
                variant="outline"
                :disabled="importing || !isOnline"
                @click="method === 'paste' ? parsePasted(true) : importFromUrl(true)"
              >
                <Loader2 v-if="importing" class="h-3.5 w-3.5 animate-spin" aria-hidden="true" />
                <Sparkles v-else class="h-3.5 w-3.5" aria-hidden="true" />
                {{ t('offerInput.aiCleanup') }}
              </Button>
              <Button type="button" size="sm" variant="ghost" :disabled="importing" @click="resetImport">
                {{ t('offerInput.another') }}
              </Button>
            </div>
          </div>
          <div class="grid grid-cols-1 gap-3 sm:grid-cols-3">
            <div v-for="field in metaFields" :key="field" class="min-w-0 space-y-1">
              <label :for="`${urlId}-${field}`" class="field-label">{{ t(`offerInput.fields.${field}`) }}</label>
              <Input
                :id="`${urlId}-${field}`"
                :model-value="draft[field]"
                class="h-9 py-1.5"
                @update:model-value="(value) => updateDraft(field, String(value))"
              />
            </div>
          </div>
          <div class="space-y-1">
            <label :for="textareaId" class="field-label">{{ t('offerInput.fields.text') }}</label>
            <Textarea
              :id="textareaId"
              :model-value="draft.text"
              :class="minHeightClass"
              @update:model-value="(value) => updateDraft('text', String(value))"
            />
          </div>
        </div>

        <!-- Site qui bloque l'import serveur : lecture depuis le navigateur de l'utilisateur -->
        <div v-if="!draft && assistedSite" class="mt-4 space-y-4 rounded-lg border border-ink/15 bg-paper-dim p-4">
          <p class="text-sm text-ink">{{ t('offerInput.assisted.intro', { site: assistedSite }) }}</p>
          <div class="space-y-1">
            <p class="field-label">{{ t('offerInput.assisted.bookmarkletTitle') }}</p>
            <p class="text-sm text-ink-soft">
              {{ t('offerInput.assisted.bookmarkletText') }}
              <RouterLink :to="localePath('/import')" class="text-ink underline underline-offset-4">
                {{ t('offerInput.assisted.bookmarkletInstall') }}
              </RouterLink>
            </p>
          </div>
          <form class="space-y-2" @submit.prevent="parsePasted(false)">
            <p class="field-label">{{ t('offerInput.assisted.pasteTitle') }}</p>
            <ol class="list-decimal space-y-1 pl-5 text-sm text-ink-soft">
              <li>
                <a :href="assistedUrl || undefined" target="_blank" rel="noopener noreferrer" class="text-ink underline underline-offset-4">
                  {{ t('offerInput.assisted.step1', { site: assistedSite }) }}
                </a>
              </li>
              <li>{{ t('offerInput.assisted.step2') }}</li>
              <li><label :for="`${urlId}-page`">{{ t('offerInput.assisted.step3') }}</label></li>
            </ol>
            <Textarea :id="`${urlId}-page`" v-model="pastedPage" class="min-h-[140px]" :disabled="importing" />
            <Button type="submit" size="sm" :disabled="importing || !pastedPage.trim() || !isOnline">
              <Loader2 v-if="importing" class="h-3.5 w-3.5 animate-spin" aria-hidden="true" />
              {{ t('offerInput.assisted.extract') }}
            </Button>
          </form>
        </div>

        <div v-if="importError" class="mt-3 space-y-2 rounded-lg border border-rose-500/25 bg-rose-500/5 p-3" role="alert">
          <p class="text-sm text-rose-700">{{ importError }}</p>
          <button
            v-if="suggestPaste && !assistedSite"
            type="button"
            class="font-mono text-micro uppercase text-ink underline underline-offset-4"
            @click="tab = 'paste'"
          >
            {{ t('offerInput.pasteInstead') }}
          </button>
        </div>
      </template>

      <p class="sr-only" aria-live="polite">{{ liveMessage }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, useId } from 'vue'
import { useI18n } from 'vue-i18n'
import { CheckCircle, Download, Link2, Loader2, Sparkles } from 'lucide-vue-next'
import posthog from 'posthog-js'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { useLocale } from '@/i18n/useLocale'
import { errorCode, importJobOffer, parseJobOffer, type ImportedOffer } from '@/lib/api'
import { browserAssistedSite, composeOfferText, offerDomain, safeHttpUrl, type OfferDraft } from '@/lib/jobOffer'
import { isOnline } from '@/lib/pwa'
import { useApplicationContextStore, type ContextModule } from '@/stores/applicationContext'

const props = withDefaults(
  defineProps<{
    module: ContextModule
    /** id du champ texte (cible de « Modifier » dans l'encart de contexte) */
    textareaId: string
    placeholder: string
    minHeightClass?: string
  }>(),
  { minHeightClass: 'min-h-[220px]' },
)

const { t } = useI18n()
const { localePath } = useLocale()
const context = useApplicationContextStore()

const uid = useId()
const labelId = `offer-label-${uid}`
const urlId = `offer-url-${uid}`

type Tab = 'paste' | 'url'
const tab = ref<Tab>('paste')
const tabs = computed(() => [
  { value: 'paste' as const, label: t('offerInput.paste') },
  { value: 'url' as const, label: t('offerInput.fromUrl') },
])

const url = ref(context.offerUrl ?? '')
const importing = ref(false)
const importError = ref('')
const importErrorCode = ref<string | null>(null)
const draft = ref<OfferDraft | null>(null)
const method = ref<ImportedOffer['method']>('html')
const liveMessage = ref('')
// Site bloquant (Indeed, LinkedIn, WTTJ…) : bookmarklet ou copier-coller de la page
const assistedSite = ref<string | null>(null)
const assistedUrl = ref<string | null>(null)
const pastedPage = ref('')

const metaFields = ['title', 'company', 'location'] as const
const sourceUrl = computed(() => safeHttpUrl(context.offerUrl))
// Erreurs pour lesquelles réessayer ne sert à rien : on propose de coller le texte
const suggestPaste = computed(() =>
  ['job_offer.site_blocked', 'job_offer.no_content', 'job_offer.not_html', 'job_offer.too_large', 'job_offer.forbidden_url']
    .includes(importErrorCode.value ?? ''),
)

function applyOffer(offer: ImportedOffer) {
  draft.value = { title: offer.title, company: offer.company, location: offer.location, text: offer.text }
  method.value = offer.method
  context.setOffer(composeOfferText(draft.value), { url: offer.source_url, from: props.module })
}

function updateDraft(field: keyof OfferDraft, value: string) {
  if (!draft.value) return
  draft.value = { ...draft.value, [field]: value }
  context.setOffer(composeOfferText(draft.value), { from: props.module })
}

function withScheme(value: string) {
  return /^https?:\/\//i.test(value) ? value : `https://${value}`
}

function showAssisted(target: string, site: string) {
  assistedSite.value = site
  assistedUrl.value = safeHttpUrl(withScheme(target.trim()))
}

async function importFromUrl(aiCleanup: boolean) {
  const target = aiCleanup ? context.offerUrl || url.value : url.value
  if (!target.trim()) return
  importError.value = ''
  importErrorCode.value = null
  const domain = offerDomain(withScheme(target))
  // Connu pour bloquer les serveurs : inutile de l'appeler, lecture depuis le navigateur
  const site = aiCleanup ? null : browserAssistedSite(target)
  if (site) {
    showAssisted(target, site)
    posthog.capture('offer_imported', { module: props.module, domain, success: false, error_code: 'browser_assisted' })
    return
  }
  assistedSite.value = null
  importing.value = true
  try {
    const offer = await importJobOffer(target.trim(), aiCleanup)
    applyOffer(offer)
    url.value = offer.source_url
    liveMessage.value = t('offerInput.imported', { domain: offerDomain(offer.source_url) })
    posthog.capture('offer_imported', {
      module: props.module,
      domain,
      success: true,
      method: offer.method,
      cached: Boolean(offer.cached),
      ai_cleanup: aiCleanup,
    })
  } catch (err: any) {
    importErrorCode.value = errorCode(err) ?? null
    importError.value = err?.response?.data?.detail || t('offerInput.errors.generic')
    liveMessage.value = importError.value
    // Refus du site (403…) : même parcours que les sites bloquants connus
    if (importErrorCode.value === 'job_offer.site_blocked' && !aiCleanup) showAssisted(target, domain)
    posthog.capture('offer_imported', {
      module: props.module,
      domain,
      success: false,
      error_code: importErrorCode.value,
      ai_cleanup: aiCleanup,
    })
  } finally {
    importing.value = false
  }
}

/** Page copiée-collée depuis un site bloquant : analysée côté serveur sans requête au site. */
async function parsePasted(aiCleanup: boolean) {
  const sourceUrl = aiCleanup ? context.offerUrl : assistedUrl.value
  importing.value = true
  importError.value = ''
  importErrorCode.value = null
  try {
    const offer = await parseJobOffer({
      url: sourceUrl,
      // Nettoyage IA : sur l'offre affichée (éventuellement retouchée), sinon sur la page collée
      text: aiCleanup && draft.value ? composeOfferText(draft.value) : pastedPage.value,
      ai_cleanup: aiCleanup,
    })
    applyOffer(offer)
    assistedSite.value = null
    liveMessage.value = t('offerInput.extracted')
    posthog.capture('offer_imported', {
      module: props.module,
      domain: offerDomain(sourceUrl),
      success: true,
      method: offer.method,
      source: 'paste',
      ai_cleanup: aiCleanup,
    })
  } catch (err: any) {
    importErrorCode.value = errorCode(err) ?? null
    importError.value = err?.response?.data?.detail || t('offerInput.errors.generic')
    liveMessage.value = importError.value
    posthog.capture('offer_imported', {
      module: props.module,
      domain: offerDomain(sourceUrl),
      success: false,
      error_code: importErrorCode.value,
      source: 'paste',
      ai_cleanup: aiCleanup,
    })
  } finally {
    importing.value = false
  }
}

function resetImport() {
  draft.value = null
  assistedSite.value = null
  pastedPage.value = ''
  importError.value = ''
  importErrorCode.value = null
  url.value = ''
}

function detachUrl() {
  context.offerUrl = null
}
</script>
