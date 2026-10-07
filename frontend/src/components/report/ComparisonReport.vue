<template>
  <PrintReport :title="t('report.comparison.title')" :meta="meta">
    <section class="print-report-section">
      <h2>{{ t('report.summary') }}</h2>
      <dl class="print-report-stats">
        <div>
          <dt>{{ t('comparison.stats.score') }}</dt>
          <dd>{{ formatPercent(result.summary.matchPercentage) }}</dd>
        </div>
        <div>
          <dt>{{ t('comparison.stats.matches') }}</dt>
          <dd>{{ result.summary.matches }}</dd>
        </div>
        <div>
          <dt>{{ t('comparison.stats.missing') }}</dt>
          <dd>{{ result.summary.missing }}</dd>
        </div>
        <div>
          <dt>{{ t('comparison.stats.unclear') }}</dt>
          <dd>{{ result.summary.unclear }}</dd>
        </div>
      </dl>
    </section>

    <section v-for="group in groups" :key="group.status" class="print-report-section">
      <h2>{{ t(`report.comparison.groups.${group.status}`) }} ({{ group.items.length }})</h2>
      <div v-for="item in group.items" :key="item.id" class="print-report-item" :data-status="group.status">
        <p class="print-report-meta">
          {{ item.category }} · {{ t('comparison.confidence', { value: formatPercent(item.confidence) }) }}
        </p>
        <p class="print-report-strong">{{ item.offerText }}</p>
        <p v-if="item.cvText"><span class="print-report-muted">{{ t('comparison.cvExcerpt') }}</span> {{ item.cvText }}</p>
        <template v-if="item.suggestions?.length">
          <p class="print-report-meta">{{ t('comparison.rewrites') }}</p>
          <ul>
            <li v-for="suggestion in item.suggestions" :key="suggestion">{{ suggestion }}</li>
          </ul>
        </template>
      </div>
    </section>
  </PrintReport>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useLocale } from '@/i18n/useLocale'
import { groupByStatus, type ReportMeta } from '@/lib/report'
import type { ComparisonResult } from '@/stores/compare'
import PrintReport from './PrintReport.vue'

const props = defineProps<{ result: ComparisonResult; meta: ReportMeta }>()

const { t } = useI18n()
const { formatPercent } = useLocale()
const groups = computed(() => groupByStatus(props.result.items))
</script>
