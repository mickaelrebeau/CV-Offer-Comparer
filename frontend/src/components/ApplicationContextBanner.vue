<template>
  <!-- Contexte de candidature partagé (CV + offre) : rappel en haut de chaque module -->
  <section
    v-if="context.hasContext || proposal"
    class="panel mb-6 overflow-hidden"
    :aria-label="t('context.regionAria')"
  >
    <div class="panel-header justify-between">
      <span>{{ t('context.title') }}</span>
      <div v-if="context.hasContext" class="flex gap-3">
        <button v-if="editTarget" type="button" class="uppercase text-ink-soft hover:text-ink" @click="edit">
          {{ t('context.edit') }}
        </button>
        <button type="button" class="uppercase text-rose-700 hover:text-rose-800" @click="clear">
          {{ t('context.clear') }}
        </button>
      </div>
    </div>

    <dl v-if="context.hasContext" class="grid grid-cols-1 gap-4 p-4 text-sm sm:grid-cols-2 sm:p-5">
      <div class="flex min-w-0 items-start gap-3">
        <FileText class="mt-0.5 h-4 w-4 shrink-0 text-ink-soft" aria-hidden="true" />
        <div class="min-w-0">
          <dt class="field-label">{{ t('context.cv') }}</dt>
          <dd class="truncate text-ink" :class="{ 'text-ink-soft': !context.hasCv }">{{ cvSummary }}</dd>
        </div>
      </div>
      <div class="flex min-w-0 items-start gap-3">
        <Briefcase class="mt-0.5 h-4 w-4 shrink-0 text-ink-soft" aria-hidden="true" />
        <div class="min-w-0">
          <dt class="field-label">{{ t('context.offer') }}</dt>
          <dd class="line-clamp-2 text-ink" :class="{ 'text-ink-soft': !context.hasOffer }">
            <a
              v-if="context.offerUrl"
              :href="context.offerUrl"
              target="_blank"
              rel="noopener noreferrer"
              class="underline underline-offset-4"
            >{{ context.offerUrl }}</a>
            <template v-else>{{ offerSummary }}</template>
          </dd>
        </div>
      </div>
    </dl>

    <div
      v-if="proposal"
      class="flex flex-col gap-3 border-t border-ink/10 p-4 sm:flex-row sm:items-center sm:justify-between sm:p-5"
      :class="{ 'border-t-0': !context.hasContext }"
    >
      <p class="text-sm text-ink-soft">{{ t('context.historyPrompt') }}</p>
      <div class="flex shrink-0 flex-wrap gap-2">
        <Button size="sm" @click="emit('adopt')">{{ t('context.historyAdopt') }}</Button>
        <Button size="sm" variant="outline" @click="emit('dismiss')">{{ t('context.historyDismiss') }}</Button>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { Briefcase, FileText } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { useApplicationContextStore } from '@/stores/applicationContext'

const props = withDefaults(
  defineProps<{
    /** id du champ à focaliser sur « Modifier » */
    editTarget?: string
    /** CV + offre d'un élément d'historique proposés comme contexte courant */
    proposal?: { cvText: string; offerText: string } | null
  }>(),
  { editTarget: undefined, proposal: null },
)

const emit = defineEmits<{ edit: []; adopt: []; dismiss: [] }>()

const { t } = useI18n()
const context = useApplicationContextStore()

const EXCERPT_LENGTH = 160

const cvSummary = computed(() => {
  if (!context.hasCv) return t('context.noCv')
  return context.cvFileName || t('context.cvManual', { count: context.cvText.trim().length })
})

const offerSummary = computed(() => {
  if (!context.hasOffer) return t('context.noOffer')
  const excerpt = context.offerText.replace(/\s+/g, ' ').trim()
  return excerpt.length > EXCERPT_LENGTH ? `${excerpt.slice(0, EXCERPT_LENGTH)}…` : excerpt
})

async function edit() {
  // Le module peut d'abord revenir à l'étape de saisie (simulateur d'entretien)
  emit('edit')
  await nextTick()
  const field = props.editTarget ? document.getElementById(props.editTarget) : null
  field?.scrollIntoView({ behavior: 'smooth', block: 'center' })
  field?.focus({ preventScroll: true })
}

function clear() {
  if (window.confirm(t('context.clearConfirm'))) context.clear()
}
</script>
