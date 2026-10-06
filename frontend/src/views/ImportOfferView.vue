<template>
  <div class="page-shell">
    <AppPageHeader
      :label="t('importOffer.label')"
      :title="t('importOffer.title')"
      :description="t('importOffer.description')"
    />

    <div class="mx-auto max-w-3xl space-y-6">
      <!-- Offre reçue du bookmarklet -->
      <AppStatus v-if="status === 'loading'" kind="loading" :message="t('importOffer.loading')" />
      <AppStatus
        v-else-if="status === 'error'"
        kind="error"
        :message="error"
        :action-label="payload ? t('common.retry') : undefined"
        @action="receive"
      />

      <section v-else-if="status === 'done' && offer" class="panel overflow-hidden" aria-labelledby="imported-offer-title">
        <div class="panel-header justify-between">
          <span>{{ t(`offerInput.methods.${offer.method === 'json-ld' ? 'jsonLd' : offer.method}`) }} {{ offerDomain(offer.source_url) }}</span>
          <CheckCircle class="h-3.5 w-3.5 text-emerald-600" aria-hidden="true" />
        </div>
        <div class="space-y-4 p-5 sm:p-6">
          <div>
            <h2 id="imported-offer-title" class="text-lg font-medium text-ink">{{ offer.title || t('importOffer.untitled') }}</h2>
            <p v-if="offer.company || offer.location" class="mt-1 text-sm text-ink-soft">
              {{ [offer.company, offer.location].filter(Boolean).join(' · ') }}
            </p>
          </div>
          <p class="line-clamp-6 whitespace-pre-line text-sm text-ink-soft">{{ offer.text }}</p>
          <p class="text-xs text-ink-soft">{{ t('importOffer.editHint') }}</p>
          <div class="flex flex-wrap gap-2">
            <Button v-for="target in targets" :key="target.path" size="sm" :variant="target.primary ? 'default' : 'outline'" @click="push(target.path)">
              <component :is="target.icon" class="h-3.5 w-3.5" aria-hidden="true" />
              {{ target.label }}
            </Button>
            <Button v-if="offer.method === 'paste'" size="sm" variant="ghost" :disabled="cleaning" @click="cleanWithAi">
              <Loader2 v-if="cleaning" class="h-3.5 w-3.5 animate-spin" aria-hidden="true" />
              <Sparkles v-else class="h-3.5 w-3.5" aria-hidden="true" />
              {{ t('offerInput.aiCleanup') }}
            </Button>
          </div>
          <p v-if="cleanError" class="text-sm text-rose-700" role="alert">{{ cleanError }}</p>
        </div>
      </section>

      <!-- Installation -->
      <section class="panel space-y-4 p-6" aria-labelledby="bookmarklet-title">
        <h2 id="bookmarklet-title" class="border-b border-ink/10 pb-3 font-mono text-caption uppercase">
          {{ t('importOffer.install.title') }}
        </h2>
        <p class="text-sm text-ink-soft">{{ t('importOffer.install.text') }}</p>
        <div class="flex flex-col items-start gap-3 rounded-lg border border-dashed border-ink/20 p-4 sm:flex-row sm:items-center">
          <!-- Lien javascript: généré localement (bookmarklet), à glisser dans la barre de favoris -->
          <a
            :href="bookmarklet"
            class="btn-primary cursor-grab select-none"
            draggable="true"
            @click.prevent="clickedInstead = true"
          >
            <Send class="mr-2 h-4 w-4" aria-hidden="true" />
            {{ t('importOffer.install.button') }}
          </a>
          <p class="text-xs text-ink-soft">{{ t('importOffer.install.drag') }}</p>
        </div>
        <p v-if="clickedInstead" class="text-sm text-ink" role="status">{{ t('importOffer.install.clicked') }}</p>
        <ol class="list-decimal space-y-1 pl-5 text-sm text-ink-soft">
          <li>{{ t('importOffer.install.step1') }}</li>
          <li>{{ t('importOffer.install.step2') }}</li>
          <li>{{ t('importOffer.install.step3') }}</li>
        </ol>
        <p class="text-xs text-ink-soft">{{ t('importOffer.install.sites') }}</p>
        <p class="text-xs text-ink-soft">{{ t('importOffer.install.mobile') }}</p>
        <p class="text-xs text-ink-soft">{{ t('importOffer.install.privacy') }}</p>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ArrowRightLeft, CheckCircle, Loader2, MessageSquare, PenLine, Send, Sparkles } from 'lucide-vue-next'
import posthog from 'posthog-js'
import AppPageHeader from '@/components/AppPageHeader.vue'
import AppStatus from '@/components/AppStatus.vue'
import { Button } from '@/components/ui/button'
import { useLocale } from '@/i18n/useLocale'
import { parseJobOffer, type ImportedOffer } from '@/lib/api'
import {
  BOOKMARKLET_HASH_KEY,
  bookmarkletSource,
  composeOfferText,
  decodeOfferPayload,
  offerDomain,
  type BookmarkletPayload,
} from '@/lib/jobOffer'
import { useApplicationContextStore } from '@/stores/applicationContext'

const { t } = useI18n()
const { push, localePath } = useLocale()
const context = useApplicationContextStore()

const status = ref<'idle' | 'loading' | 'done' | 'error'>('idle')
const error = ref('')
const payload = ref<BookmarkletPayload | null>(null)
const offer = ref<ImportedOffer | null>(null)
const cleaning = ref(false)
const cleanError = ref('')
const clickedInstead = ref(false)

// Le favori ouvre cette page (dans la langue de l'utilisateur au moment de l'installation)
const bookmarklet = computed(() =>
  typeof window === 'undefined' ? '#' : bookmarkletSource(`${window.location.origin}${localePath('/import')}`),
)

const targets = computed(() => [
  { path: '/compare', label: t('importOffer.toCompare'), icon: ArrowRightLeft, primary: true },
  { path: '/interview-simulator', label: t('comparison.next.interview'), icon: MessageSquare, primary: false },
  { path: '/cover-letter', label: t('comparison.next.coverLetter'), icon: PenLine, primary: false },
])

function apply(result: ImportedOffer) {
  offer.value = result
  context.setOffer(composeOfferText(result), { url: result.source_url, from: 'compare' })
}

async function receive() {
  if (!payload.value) return
  status.value = 'loading'
  error.value = ''
  try {
    const result = await parseJobOffer({
      url: payload.value.u,
      title: payload.value.t,
      json_ld: payload.value.j,
      text: payload.value.x,
    })
    apply(result)
    status.value = 'done'
    posthog.capture('offer_imported', {
      module: 'bookmarklet',
      domain: offerDomain(payload.value.u),
      success: true,
      method: result.method,
      source: 'bookmarklet',
    })
  } catch (err: any) {
    error.value = err?.response?.data?.detail || t('offerInput.errors.generic')
    status.value = 'error'
    posthog.capture('offer_imported', {
      module: 'bookmarklet',
      domain: offerDomain(payload.value.u),
      success: false,
      error_code: err?.response?.data?.code ?? null,
      source: 'bookmarklet',
    })
  }
}

async function cleanWithAi() {
  if (!offer.value) return
  cleaning.value = true
  cleanError.value = ''
  try {
    apply(await parseJobOffer({ url: offer.value.source_url, text: composeOfferText(offer.value), ai_cleanup: true }))
  } catch (err: any) {
    cleanError.value = err?.response?.data?.detail || t('offerInput.errors.generic')
  } finally {
    cleaning.value = false
  }
}

onMounted(() => {
  const hash = new URLSearchParams(window.location.hash.slice(1)).get(BOOKMARKLET_HASH_KEY)
  if (!hash) return
  // L'offre ne reste ni dans la barre d'adresse ni dans l'historique du navigateur
  window.history.replaceState(window.history.state, '', window.location.pathname)
  payload.value = decodeOfferPayload(hash)
  if (!payload.value) {
    error.value = t('importOffer.invalid')
    status.value = 'error'
    return
  }
  receive()
})
</script>
