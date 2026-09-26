<template>
  <button
    v-if="canInstall"
    type="button"
    class="inline-flex items-center gap-1.5 font-mono text-micro uppercase text-ink-soft transition-colors hover:text-ink"
    :title="t('pwa.installHint')"
    @click="install"
  >
    <Download class="h-3.5 w-3.5" aria-hidden="true" />
    {{ t('pwa.install') }}
  </button>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { Download } from 'lucide-vue-next'
import posthog from 'posthog-js'
import { canInstall, promptInstall } from '@/lib/pwa'

const { t } = useI18n()

async function install() {
  const accepted = await promptInstall()
  posthog.capture('pwa_install_prompt', { outcome: accepted ? 'accepted' : 'dismissed' })
}
</script>
