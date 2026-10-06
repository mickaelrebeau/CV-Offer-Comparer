<template>
  <div class="page-shell">
    <AppPageHeader
      :label="t('profile.label')"
      :title="t('profile.title')"
      :description="t('profile.description')"
    />

    <div class="mx-auto max-w-2xl space-y-6">
      <div class="panel p-6 space-y-4">
        <h2 class="border-b border-ink/10 pb-3 font-mono text-caption uppercase">{{ t('profile.info') }}</h2>
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div class="space-y-1">
            <span class="field-label">{{ t('common.emailLabel') }}</span>
            <p class="text-sm text-ink">{{ user?.email }}</p>
          </div>
          <div class="space-y-1">
            <span class="field-label">{{ t('profile.signupDate') }}</span>
            <p class="text-sm text-ink">
              {{ user?.created_at ? formatDate(user.created_at, { dateStyle: 'long' }) : t('common.notAvailable') }}
            </p>
          </div>
          <div class="space-y-1">
            <span class="field-label">{{ t('profile.language') }}</span>
            <LanguageSwitcher />
          </div>
          <div v-if="canInstall" class="space-y-1">
            <span class="field-label">{{ t('profile.app') }}</span>
            <InstallAppButton />
          </div>
        </div>
      </div>

      <SavedCvsSection />

      <!-- Bouton « Envoyer vers Talento » : offres Indeed, LinkedIn, Welcome to the Jungle -->
      <section class="panel space-y-4 p-6" aria-labelledby="send-to-talento-title">
        <div class="space-y-2 border-b border-ink/10 pb-3">
          <h2 id="send-to-talento-title" class="font-mono text-caption uppercase">{{ t('profile.sendToTalento.title') }}</h2>
          <p class="text-sm text-ink-soft">{{ t('profile.sendToTalento.text') }}</p>
        </div>
        <RouterLink :to="localePath('/import')" class="btn-secondary inline-flex h-9 items-center gap-2 px-4 text-micro">
          <Send class="h-3.5 w-3.5" aria-hidden="true" />
          {{ t('profile.sendToTalento.action') }}
        </RouterLink>
      </section>

      <LlmProvidersSection />

      <div class="panel p-6 space-y-4">
        <h2 class="border-b border-ink/10 pb-3 font-mono text-caption uppercase">{{ t('profile.actions') }}</h2>
        <div class="flex flex-col gap-3 pt-2 sm:flex-row">
          <Button variant="outline" @click="handleSignOut">{{ t('profile.signOut') }}</Button>
          <Button variant="destructive" @click="showDeleteModal = true">{{ t('profile.deleteAccount') }}</Button>
        </div>
      </div>
    </div>

    <Modal
      :is-open="showDeleteModal"
      :title="t('profile.modal.title')"
      :message="t('profile.modal.message')"
      :confirm-text="t('profile.modal.confirm')"
      :cancel-text="t('common.cancel')"
      type="error"
      @confirm="handleDeleteAccount"
      @cancel="showDeleteModal = false"
      @close="showDeleteModal = false"
    />

    <Notification
      :is-open="showNotification"
      :message="notificationMessage"
      :type="notificationType"
      @close="showNotification = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Send } from 'lucide-vue-next'
import { storeToRefs } from 'pinia'
import AppPageHeader from '@/components/AppPageHeader.vue'
import InstallAppButton from '@/components/InstallAppButton.vue'
import LanguageSwitcher from '@/components/LanguageSwitcher.vue'
import LlmProvidersSection from '@/components/LlmProvidersSection.vue'
import SavedCvsSection from '@/components/SavedCvsSection.vue'
import { Button } from '@/components/ui/button'
import { Modal } from '@/components/ui/modal'
import { Notification } from '@/components/ui/notification'
import { useLocale } from '@/i18n/useLocale'
import { canInstall } from '@/lib/pwa'
import { useAuthStore } from '@/stores/auth'

const { t } = useI18n()
const { push, formatDate, localePath } = useLocale()
const authStore = useAuthStore()

const { user } = storeToRefs(authStore)
const { signOut, deleteAccount } = authStore

const showDeleteModal = ref(false)
const showNotification = ref(false)
const notificationMessage = ref('')
const notificationType = ref<'info' | 'warning' | 'error' | 'success'>('info')

async function handleSignOut() {
  await signOut()
  push('/')
}

async function handleDeleteAccount() {
  showDeleteModal.value = false

  try {
    const { error } = await deleteAccount()
    if (error) {
      notificationMessage.value = t('profile.deleteError', { message: error.message })
      notificationType.value = 'error'
      showNotification.value = true
      return
    }

    notificationMessage.value = t('profile.deleted')
    notificationType.value = 'success'
    showNotification.value = true

    setTimeout(() => {
      push('/')
    }, 1500)
  } catch {
    notificationMessage.value = t('profile.deleteFailed')
    notificationType.value = 'error'
    showNotification.value = true
  }
}
</script>
