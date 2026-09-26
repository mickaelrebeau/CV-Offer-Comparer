<template>
  <div class="flex items-center gap-2">
    <span v-if="isAuthenticated" class="hidden max-w-[180px] truncate font-mono text-micro uppercase text-ink-soft sm:inline-block">
      {{ user?.email }}
    </span>
    <Button v-if="!isAuthenticated" variant="outline" size="sm" @click="push('/login')">
      {{ t('nav.login') }}
    </Button>
    <template v-else>
      <Button variant="outline" size="sm" @click="push('/profile')">{{ t('nav.profile') }}</Button>
      <Button variant="ghost" size="sm" class="text-rose-700 hover:text-rose-800" @click="handleSignOut">
        {{ t('nav.signOut') }}
      </Button>
    </template>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import { useLocale } from '@/i18n/useLocale'
import { useAuthStore } from '@/stores/auth'

const { t } = useI18n()
const { push } = useLocale()
const authStore = useAuthStore()

const { user, isAuthenticated, signOut } = authStore

async function handleSignOut() {
  await signOut()
  push('/')
}
</script>
