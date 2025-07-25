<template>
  <div class="max-w-4xl mx-auto">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-primary mb-2">
        Mon Profil
      </h1>
      <p class="text-muted-foreground">
        Gérez vos informations et vos préférences
      </p>
    </div>

    <div class="grid grid-cols-1 gap-6">
      <!-- Informations utilisateur -->
      <Card>
        <CardHeader>
          <CardTitle>Informations personnelles</CardTitle>
        </CardHeader>
        <CardContent>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium mb-2">Email</label>
              <p class="text-muted-foreground">{{ user?.email }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium mb-2">Date d'inscription</label>
              <p class="text-muted-foreground">
                {{ user?.created_at ? new Date(user.created_at).toLocaleDateString('fr-FR') : 'N/A' }}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- Actions -->
      <Card class="mt-6">
        <CardHeader>
          <CardTitle>Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div class="mb-10 border-b border-gray-800" />
          <div class="space-y-4 flex flex-col">
            <Button variant="destructive" @click="handleSignOut">
              Se déconnecter
            </Button>
            <Button variant="outline" @click="showDeleteModal = true">
              Supprimer mon compte
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- Modal de confirmation de suppression -->
    <Modal :is-open="showDeleteModal" title="Confirmer la suppression"
      message="Êtes-vous sûr de vouloir supprimer votre compte ? Cette action est irréversible, vous ne pourrez plus accéder à votre compte."
      confirm-text="Supprimer le compte" cancel-text="Annuler" type="error" @confirm="handleDeleteAccount"
      @cancel="showDeleteModal = false" @close="showDeleteModal = false" />

    <!-- Notification -->
    <Notification :is-open="showNotification" :message="notificationMessage" :type="notificationType"
      @close="showNotification = false" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card/index'
import { Button } from '../components/ui/button/index'
import { Modal } from '../components/ui/modal/index'
import { Notification } from '../components/ui/notification/index'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const { user, signOut, deleteAccount } = authStore

// État des modals et notifications
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
      notificationMessage.value = `Erreur lors de la suppression du compte : ${error.message}`
      notificationType.value = 'error'
      showNotification.value = true
      return
    }

    notificationMessage.value = 'Votre compte a été supprimé avec succès.'
    notificationType.value = 'success'
    showNotification.value = true

    // Redirection après un délai pour permettre à l'utilisateur de voir le message
    setTimeout(() => {
      router.push('/')
    }, 2000)
  } catch (error) {
    console.error('Erreur lors de la suppression du compte:', error)
    notificationMessage.value = 'Une erreur inattendue s\'est produite lors de la suppression du compte.'
    notificationType.value = 'error'
    showNotification.value = true
  }
}
</script> 