<template>
  <!-- Évolution par rapport à la version précédente : réanalyse de la même offre avec un CV mis à jour -->
  <section class="panel overflow-hidden" :aria-labelledby="headingId">
    <div class="panel-header justify-between">
      <span :id="headingId">{{ t('comparison.diff.title') }}</span>
      <span>{{ t('comparison.diff.since', { date: formatDate(diff.before.created_at, { dateStyle: 'medium' }) }) }}</span>
    </div>

    <div class="grid gap-6 p-5 sm:grid-cols-[auto_1fr] sm:items-center">
      <div class="flex items-baseline gap-3 tabular-nums">
        <span class="text-2xl text-ink-soft">{{ formatPercent(diff.before.match_percentage) }}</span>
        <span class="text-ink-soft" aria-hidden="true">→</span>
        <span class="text-3xl font-medium text-ink">{{ formatPercent(diff.after.match_percentage) }}</span>
        <span class="font-mono text-caption" :class="deltaTone">{{ deltaLabel }}</span>
      </div>
      <p class="text-sm text-ink-soft">
        {{ t('comparison.diff.counts', { improved: diff.improved.length, regressed: diff.regressed.length, unchanged: diff.unchanged }) }}
        <template v-if="diff.added.length || diff.removed.length">
          · {{ t('comparison.diff.reworded', { count: diff.added.length + diff.removed.length }) }}
        </template>
      </p>
    </div>

    <div v-if="diff.improved.length || diff.regressed.length" class="grid gap-px border-t border-ink/10 bg-ink/10 md:grid-cols-2">
      <div v-for="group in groups" :key="group.key" class="bg-paper p-5">
        <h3 class="mb-3 font-mono text-micro uppercase" :class="group.tone">
          {{ t(`comparison.diff.${group.key}`, { count: group.changes.length }) }}
        </h3>
        <p v-if="!group.changes.length" class="text-sm text-ink-soft">{{ t(`comparison.diff.${group.key}None`) }}</p>
        <ul v-else class="space-y-3">
          <li v-for="(change, idx) in group.changes" :key="idx" class="text-sm">
            <p class="text-ink">{{ change.offerText }}</p>
            <p class="mt-0.5 font-mono text-micro uppercase text-ink-soft">
              {{ change.category }} · {{ statusLabel(change.before) }} → {{ statusLabel(change.after) }}
            </p>
          </li>
        </ul>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, useId } from 'vue'
import { useI18n } from 'vue-i18n'
import { useLocale } from '@/i18n/useLocale'
import type { ComparisonDiff, ComparisonStatus } from '@/lib/api'

const props = defineProps<{ diff: ComparisonDiff }>()

const { t } = useI18n()
const { formatDate, formatNumber, formatPercent } = useLocale()
const headingId = useId()

// Écart en points de pourcentage, signé
const points = computed(() => Math.round(props.diff.score_delta * 100))
const deltaLabel = computed(() =>
  t('comparison.diff.delta', { value: `${points.value > 0 ? '+' : points.value < 0 ? '−' : '±'}${formatNumber(Math.abs(points.value))}` }),
)
const deltaTone = computed(() =>
  points.value > 0 ? 'text-emerald-600' : points.value < 0 ? 'text-rose-600' : 'text-ink-soft',
)

const groups = computed(() => [
  { key: 'improved', tone: 'text-emerald-700', changes: props.diff.improved },
  { key: 'regressed', tone: 'text-rose-700', changes: props.diff.regressed },
])

const statusLabel = (status: ComparisonStatus) =>
  t(`comparison.status.${status === 'unclear' ? 'partial' : status}`)
</script>
