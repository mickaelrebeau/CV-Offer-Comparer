<template>
  <Button variant="outline" size="sm" class="print:hidden" @click="printReport(type, fileTitle)">
    <FileDown class="h-3.5 w-3.5" aria-hidden="true" />
    {{ t('report.export') }}
  </Button>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { FileDown } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { printReport, type ReportType } from '@/lib/report'

defineProps<{ type: ReportType; fileTitle: string }>()

const { t } = useI18n()
</script>
