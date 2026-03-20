<script setup lang="ts">
import { ref } from 'vue'
import LabelReaderForm from '@/components/LabelReaderForm.vue'
import ResultsTable from '@/components/ResultsTable.vue'
import type { ExtractedLabel } from '@/components/ResultsTable.vue'

const rawResult = ref<ExtractedLabel[] | null>(null)

const handleResult = (data: ExtractedLabel[] | null) => {
  rawResult.value = data
}
</script>

<template>
  <div class="card">
    <h1 class="title">Inventory Label Reader</h1>
    <LabelReaderForm @result="handleResult" />
    <ResultsTable v-if="rawResult" :results="rawResult" />
  </div>
</template>

<style scoped>
.card {
  background: var(--color-background);
  border-radius: 12px;
  box-shadow:
    0 4px 12px rgba(0, 0, 0, 0.05),
    0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 2.5rem;
  margin-top: 2rem;
}

.title {
  text-align: center;
  font-size: 2rem;
  font-weight: 500;
  margin-bottom: 2rem;
  color: var(--color-heading);
}
</style>
