<template>
  <div class="page-shell">
    <div class="mx-auto max-w-md">
      <AppPageHeader
        :label="t('auth.label')"
        :title="t('auth.register.title')"
        :description="t('auth.register.description')"
      />

      <div class="panel p-6 sm:p-8 space-y-6">
        <form @submit.prevent="handleRegister" class="space-y-4">
          <div class="space-y-1.5">
            <label for="email" class="field-label">{{ t('common.emailLabel') }}</label>
            <Input id="email" v-model="email" type="email" required :placeholder="t('common.emailPlaceholder')" />
          </div>

          <div class="space-y-1.5">
            <label for="password" class="field-label">{{ t('common.passwordLabel') }}</label>
            <Input id="password" v-model="password" type="password" required minlength="8" :placeholder="t('auth.register.passwordPlaceholder')" :show-password-toggle="true" />
          </div>

          <div class="space-y-1.5">
            <label for="confirmPassword" class="field-label">{{ t('auth.register.confirmLabel') }}</label>
            <Input id="confirmPassword" v-model="confirmPassword" type="password" required :placeholder="t('auth.register.confirmPlaceholder')" :show-password-toggle="true" />
          </div>

          <div role="alert" v-if="error" class="rounded-lg border border-rose-500/25 bg-rose-500/5 p-3 font-mono text-micro text-rose-700">
            {{ error }}
          </div>

          <div role="status" v-if="success" class="rounded-lg border border-emerald-500/25 bg-emerald-500/5 p-3 font-mono text-micro text-emerald-700">
            {{ success }}
          </div>

          <label class="flex items-start gap-3 text-sm leading-snug text-ink-soft">
            <input
              v-model="acceptTerms"
              type="checkbox"
              required
              class="mt-1 h-4 w-4 shrink-0 rounded border-ink/30 text-ink focus:ring-ink"
            />
            <i18n-t keypath="auth.register.terms" tag="span" scope="global">
              <template #terms>
                <RouterLink :to="localePath('/cgv')" class="text-ink underline underline-offset-2" target="_blank">{{ t('auth.register.termsLink') }}</RouterLink>
              </template>
              <template #privacy>
                <RouterLink :to="localePath('/confidentialite')" class="text-ink underline underline-offset-2" target="_blank">{{ t('auth.register.privacyLink') }}</RouterLink>
              </template>
            </i18n-t>
          </label>

          <Button type="submit" variant="full" size="lg" :disabled="loading || !acceptTerms">
            <Loader2 v-if="loading" class="mr-2 h-4 w-4 animate-spin" aria-hidden="true" />
            {{ t('auth.register.submit') }}
          </Button>
        </form>

        <div class="relative">
          <div class="absolute inset-0 flex items-center"><span class="w-full border-t border-ink/10" /></div>
          <div class="relative flex justify-center font-mono text-micro uppercase">
            <span class="bg-paper px-2 text-ink-soft">{{ t('common.orContinueWith') }}</span>
          </div>
        </div>

        <Button type="button" variant="full-outline" size="lg" :disabled="loading || !acceptTerms" @click="handleGoogleRegister">
          <svg v-if="!loading" class="mr-2 h-4 w-4 shrink-0" viewBox="0 0 24 24">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
          </svg>
          <Loader2 v-if="loading" class="mr-2 h-4 w-4 animate-spin" aria-hidden="true" />
          {{ t('common.continueWithGoogle') }}
        </Button>

        <p class="text-center font-mono text-micro uppercase text-ink-soft">
          {{ t('auth.register.hasAccount') }}
          <router-link :to="localePath('/login')" class="text-ink underline underline-offset-2">{{ t('auth.register.signIn') }}</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'
import AppPageHeader from '@/components/AppPageHeader.vue'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Loader2 } from 'lucide-vue-next'
import { useLocale } from '@/i18n/useLocale'
import { useAuthStore } from '@/stores/auth'
import posthog from 'posthog-js'

const { t } = useI18n()
const { localePath, push } = useLocale()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const acceptTerms = ref(false)
const error = ref('')
const success = ref('')
const loading = ref(false)

async function handleRegister() {
  if (!acceptTerms.value) {
    error.value = t('auth.register.errors.acceptTerms')
    return
  }

  if (password.value !== confirmPassword.value) {
    error.value = t('auth.register.errors.passwordMismatch')
    return
  }

  if (password.value.length < 8) {
    error.value = t('auth.register.errors.passwordTooShort')
    return
  }

  loading.value = true
  error.value = ''
  success.value = ''

  const { error: registerError } = await authStore.signUp(email.value, password.value)

  if (registerError) {
    error.value = registerError.message || t('auth.register.errors.generic')
  } else {
    posthog.capture('account_registered', { registration_method: 'password' })
    success.value = t('auth.register.success')
    setTimeout(() => {
      push('/dashboard')
    }, 1500)
  }

  loading.value = false
}

async function handleGoogleRegister() {
  if (!acceptTerms.value) {
    error.value = t('auth.register.errors.acceptTerms')
    return
  }

  loading.value = true
  error.value = ''
  success.value = ''

  const { error: googleError } = await authStore.signInWithGoogle()

  if (googleError) {
    error.value = t('auth.register.errors.google')
    loading.value = false
  }
}
</script>
