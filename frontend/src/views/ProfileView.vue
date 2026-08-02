<template>
  <div class="page-shell">
    <AppPageHeader
      label="Compte"
      title="Mon profil"
      description="Gérez vos identifiants et préférences de compte."
    />

    <div class="mx-auto max-w-2xl space-y-6">
      <div class="panel p-6 space-y-4">
        <h2 class="border-b border-ink/10 pb-3 font-mono text-caption uppercase">Informations</h2>
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div class="space-y-1">
            <span class="field-label">Adresse email</span>
            <p class="text-sm text-ink">{{ user?.email }}</p>
          </div>
          <div class="space-y-1">
            <span class="field-label">Date d'inscription</span>
            <p class="text-sm text-ink">
              {{ user?.created_at ? new Date(user.created_at).toLocaleDateString('fr-FR') : 'N/A' }}
            </p>
          </div>
        </div>
      </div>

      <div class="panel p-6 space-y-4">
        <h2 class="border-b border-ink/10 pb-3 font-mono text-caption uppercase">Actions</h2>
        <div class="flex flex-col gap-3 pt-2 sm:flex-row">
          <Button variant="outline" @click="handleSignOut">Se déconnecter</Button>
          <Button variant="destructive" @click="showDeleteModal = true">Supprimer mon compte</Button>
        </div>
      </div>
    </div>

    <Modal
      :is-open="showDeleteModal"
      title="Confirmer la suppression"
      message="Êtes-vous sûr de vouloir supprimer votre compte ? Cette action est définitive."
      confirm-text="Supprimer définitivement"
      cancel-text="Annuler"
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
import { storeToRefs } from 'pinia'
import AppPageHeader from '@/components/AppPageHeader.vue'
import { Button } from '@/components/ui/button'
import { Modal } from '@/components/ui/modal'
import { Notification } from '@/components/ui/notification'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const { user } = storeToRefs(authStore)
const { signOut, deleteAccount } = authStore

const showDeleteModal = ref(false)
const showNotification = ref(false)
const notificationMessage = ref('')
const notificationType = ref<'info' | 'warning' | 'error' | 'success'>('info')

async function handleSignOut() {
  await signOut()
  router.push('/')
}

async function handleDeleteAccount() {
  showDeleteModal.value = false

  try {
    const { error } = await deleteAccount()
    if (error) {
      notificationMessage.value = `Erreur : ${error.message}`
      notificationType.value = 'error'
      showNotification.value = true
      return
    }

    notificationMessage.value = 'Votre compte a été supprimé.'
    notificationType.value = 'success'
    showNotification.value = true

    setTimeout(() => {
      router.push('/')
    }, 1500)
  } catch {
    notificationMessage.value = 'Une erreur est survenue lors de la suppression.'
    notificationType.value = 'error'
    showNotification.value = true
  }
}
</script>
