<script setup lang="ts">
export interface ExtractedLabel {
  visual_evidence?: string
  item: string
  date?: string
}

defineProps<{
  results: ExtractedLabel[]
}>()
</script>

<template>
  <div class="result-container">
    <h3>Extraction Result</h3>
    <div class="table-responsive">
      <table v-if="results.length > 0" class="result-table">
        <thead>
          <tr>
            <th>Item</th>
            <th v-if="results.some((r) => r.date)">Date</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in results" :key="index">
            <td>{{ row.item }}</td>
            <td v-if="results.some((r) => r.date)">{{ row.date || 'N/A' }}</td>
          </tr>
        </tbody>
      </table>
      <p v-else class="no-results">No labels extracted.</p>
    </div>
  </div>
</template>

<style scoped>
.result-container {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid var(--color-border);
}

.result-container h3 {
  margin-bottom: 1rem;
  font-size: 1.1rem;
  color: var(--color-heading);
}

.table-responsive {
  overflow-x: auto;
}

.result-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
  background: var(--color-background-soft);
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid var(--color-border);
}

.result-table th,
.result-table td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}

.result-table th {
  background-color: var(--color-background-mute);
  font-weight: 600;
  color: var(--color-heading);
}

.result-table tr:last-child td {
  border-bottom: none;
}

.no-results {
  color: var(--color-text-light-2);
  font-style: italic;
  font-size: 0.9rem;
}
</style>
