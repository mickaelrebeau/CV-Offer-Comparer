<template>
  <div class="max-w-3xl mx-auto px-6 py-10 sm:py-16 space-y-8">
    <div class="space-y-2">
      <h1 class="text-3xl font-extrabold tracking-tight text-foreground">Mon Profil</h1>
      <p class="text-sm text-muted-foreground">
        Gérez vos identifiants et préférencs de compte.
      </p>
    </div>

    <div class="space-y-6">
      <Card class="glass-card p-6 rounded-2xl border border-border space-y-4">
        <h2 class="text-base font-bold text-foreground border-b border-border pb-3">Informations Personnelles</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div class="space-y-1">
            <span class="text-muted-foreground font-medium uppercase tracking-wider">Adresse Email</span>
            <p class="text-sm font-semibold text-foreground">{{ user?.email }}</p>
          </div>
          <div class="space-y-1">
            <span class="text-muted-foreground font-medium uppercase tracking-wider">Date d'inscription</span>
            <p class="text-sm font-semibold text-foreground">
              {{ user?.created_at ? new Date(user.created_at).toLocaleDateString('fr-FR') : 'N/A' }}
            </p>
          </div>
        </div>
      </Card>

      <Card class="glass-card p-6 rounded-2xl border border-border space-y-4">
        <h2 class="text-base font-bold text-foreground border-b border-border pb-3">Actions de Compte</h2>
        <div class="flex flex-col sm:flex-row gap-4 pt-2">
          <Button variant="outline" @click="handleSignOut" class="rounded-full">
            Se déconnecter
          </Button>
          <Button variant="destructive" @click="showDeleteModal = true" class="rounded-full">
            Supprimer mon compte
          </Button>
        </div>
      </Card>
    </div>

    <Modal :is-open="showDeleteModal" title="Confirmer la suppression"
      message="Êtes-vous sûr de vouloir supprimer votre compte ? Cette action est définitive."
      confirm-text="Supprimer définitivement" cancel-text="Annuler" type="error" @confirm="handleDeleteAccount"
      @cancel="showDeleteModal = false" @close="showDeleteModal = false" />

    <Notification :is-open="showNotification" :message="notificationMessage" :type="notificationType"
      @close="showNotification = false" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { storeToRefs } from 'pinia'
import { Card } from '@/components/ui/card'
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
  } catch (err) {
    notificationMessage.value = 'Une erreur est survenue lors de la suppression.'
    notificationType.value = 'error'
    showNotification.value = true
  }
}
</script>
