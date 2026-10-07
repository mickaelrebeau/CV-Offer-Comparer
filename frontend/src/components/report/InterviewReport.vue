<template>
  <PrintReport :title="t('report.interview.title')" :meta="meta">
    <section class="print-report-section">
      <h2>{{ t('report.summary') }}</h2>
      <dl class="print-report-stats">
        <div>
          <dt>{{ t('results.globalScore') }}</dt>
          <dd>{{ analysis?.score_global ?? t('common.notAvailable') }}/10</dd>
        </div>
        <div>
          <dt>{{ t('results.questions') }}</dt>
          <dd>{{ numQuestions }}</dd>
        </div>
        <div>
          <dt>{{ t('results.duration') }}</dt>
          <dd>{{ duration }}</dd>
        </div>
      </dl>
      <p v-if="scoreMessage" class="print-report-strong">{{ scoreMessage }}</p>
    </section>

    <section v-if="analysis?.points_forts?.length" class="print-report-section">
      <h2>{{ t('results.strengths') }}</h2>
      <ul>
        <li v-for="(point, idx) in analysis.points_forts" :key="idx">{{ point }}</li>
      </ul>
    </section>

    <section v-if="analysis?.points_amelioration?.length" class="print-report-section">
      <h2>{{ t('results.improvements') }}</h2>
      <ul>
        <li v-for="(point, idx) in analysis.points_amelioration" :key="idx">{{ point }}</li>
      </ul>
    </section>

    <section v-if="suggestions.length" class="print-report-section">
      <h2>{{ t('report.interview.suggestions') }}</h2>
      <div v-for="(suggestion, idx) in suggestions" :key="idx" class="print-report-item">
        <p class="print-report-strong">
          {{ suggestion.titre }}
          <span v-if="priorityLabel(suggestion.priorite)" class="print-report-muted">· {{ priorityLabel(suggestion.priorite) }}</span>
        </p>
        <p v-if="suggestion.description">{{ suggestion.description }}</p>
      </div>
    </section>

    <section v-if="answers.length" class="print-report-section">
      <h2>{{ t('results.answersDetail') }}</h2>
      <div v-for="(answer, idx) in answers" :key="idx" class="print-report-item">
        <p class="print-report-meta">{{ t('results.questionN', { n: idx + 1, category: answer.category }) }}</p>
        <p class="print-report-strong">{{ answer.question }}</p>
        <p>{{ answer.answer || t('results.noAnswer') }}</p>
        <p v-if="adviceFor(answer.question)" class="print-report-advice">
          <span class="print-report-muted">{{ t('report.interview.advice') }}</span> {{ adviceFor(answer.question) }}
        </p>
      </div>
    </section>
  </PrintReport>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ReportMeta } from '@/lib/report'
import PrintReport from './PrintReport.vue'

interface InterviewAnswer {
  question: string
  answer: string
  category: string
}

interface InterviewAnalysis {
  score_global?: number
  points_forts?: string[]
  points_amelioration?: string[]
  suggestions?: { titre?: string; description?: string; priorite?: string }[]
  conseils_specifiques?: { question?: string; conseil?: string }[]
}

const props = defineProps<{
  analysis: InterviewAnalysis | null
  answers: InterviewAnswer[]
  numQuestions: number
  duration: string
  scoreMessage: string
  meta: ReportMeta
}>()

const { t } = useI18n()

const suggestions = computed(() => (props.analysis?.suggestions ?? []).filter((suggestion) => suggestion?.titre))

const priorityLabel = (priority?: string) =>
  priority && ['haute', 'moyenne', 'basse'].includes(priority) ? t(`report.interview.priority.${priority}`) : ''

// Conseil de l'IA rattaché à la question (même intitulé)
const adviceFor = (question: string) =>
  props.analysis?.conseils_specifiques?.find((advice) => advice?.question?.trim() === question.trim())?.conseil ?? ''
</script>
