<template>
  <!-- Erreur d'une fonction IA, avec l'action utile selon sa cause (quota plateforme, clé personnelle…) -->
  <div role="alert" class="space-y-3 rounded-lg border border-rose-500/25 bg-rose-500/5 p-4">
    <p class="font-mono text-micro text-rose-700">{{ message }}</p>

    <template v-if="isPlatformError">
      <p class="text-sm text-ink-soft">
        {{ authStore.isAuthenticated ? t('llmNotice.platformHint') : t('llmNotice.anonymousHint') }}
      </p>
      <div class="flex flex-wrap gap-2">
        <RouterLink v-if="authStore.isAuthenticated" :to="localePath(LLM_PROVIDERS_PATH)" class="btn-primary !h-9 !px-4 !text-micro">
          {{ t('llmNotice.addKey') }}
        </RouterLink>
        <RouterLink v-else :to="localePath('/login')" class="btn-secondary !h-9 !px-4 !text-micro">
          {{ t('llmNotice.signIn') }}
        </RouterLink>
      </div>
    </template>

    <template v-else-if="isUserError">
      <p v-if="switchedTo" class="text-sm text-ink" role="status">{{ switchedTo }}</p>
      <template v-else>
        <p v-if="alternatives.length" class="text-sm text-ink-soft">{{ t('llmNotice.switchHint') }}</p>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="credential in alternatives"
            :key="credential.id"
            type="button"
            class="btn-secondary !h-9 !px-4 !text-micro"
            :disabled="switching"
            @click="useCredential(credential)"
          >
            {{ t('llmNotice.useProvider', { provider: credential.provider_label }) }}
          </button>
          <button type="button" class="btn-secondary !h-9 !px-4 !text-micro" :disabled="switching" @click="usePlatform">
            {{ t('llmNotice.usePlatform') }}
          </button>
          <RouterLink :to="localePath(LLM_PROVIDERS_PATH)" class="inline-flex h-9 items-center px-2 font-mono text-micro uppercase text-ink underline-offset-4 hover:underline">
            {{ t('llmNotice.manage') }}
          </RouterLink>
        </div>
      </template>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import posthog from 'posthog-js'
import { useLocale } from '@/i18n/useLocale'
import {
  activateLlmCredential,
  deactivateLlmCredentials,
  listLlmCredentials,
  type LlmCredential,
} from '@/lib/api'
import { LLM_PROVIDERS_PATH, PLATFORM_LLM_ERRORS, USER_LLM_ERRORS } from '@/lib/llmErrors'
import { useAuthStore } from '@/stores/auth'

const props = defineProps<{ message: string; code?: string | null }>()
const emit = defineEmits<{ switched: [] }>()

const { t } = useI18n()
const { localePath } = useLocale()
const authStore = useAuthStore()

const isPlatformError = computed(() => Boolean(props.code && PLATFORM_LLM_ERRORS.has(props.code)))
const isUserError = computed(() => Boolean(props.code && USER_LLM_ERRORS.has(props.code)))

const alternatives = ref<LlmCredential[]>([])
const switching = ref(false)
const switchedTo = ref('')

onMounted(async () => {
  if (!isUserError.value || !authStore.isAuthenticated) return
  try {
    const { items } = await listLlmCredentials()
    alternatives.value = items.filter((item) => !item.is_active)
  } catch {
    // Liste indisponible : les liens vers le profil suffisent
  }
})

async function useCredential(credential: LlmCredential) {
  switching.value = true
  try {
    await activateLlmCredential(credential.id)
    posthog.capture('llm_credential_activated', { provider: credential.provider, source: 'error_notice' })
    switchedTo.value = t('llmNotice.switched', { provider: credential.provider_label })
    emit('switched')
  } finally {
    switching.value = false
  }
}

async function usePlatform() {
  switching.value = true
  try {
    await deactivateLlmCredentials()
    posthog.capture('llm_credential_deactivated', { source: 'error_notice' })
    switchedTo.value = t('llmNotice.switchedPlatform')
    emit('switched')
  } finally {
    switching.value = false
  }
}
</script>
