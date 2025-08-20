<template>
  <div class="data-table">
    <div v-if="loading" data-testid="loading-state" class="loading-state">
      <p>Loading...</p>
    </div>
    <div v-else-if="data.length === 0" data-testid="empty-state" class="empty-state">
      <p>No data available</p>
    </div>
    <table v-else>
      <thead>
        <tr>
          <th v-for="column in columns" :key="column.key">
            {{ column.label }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in data" :key="row.id">
          <td v-for="column in columns" :key="column.key">
            {{ formatCellValue(row[column.key], column.format) }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
interface Column {
  key: string;
  label: string;
  sortable?: boolean;
  format?: 'currency' | 'number' | 'text';
}

interface Props {
  data: Record<string, any>[];
  columns: Column[];
  loading?: boolean;
  clickable?: boolean;
  pageSize?: number;
  tableClass?: string;
  headerClass?: string;
}

defineProps<Props>();

function formatCellValue(value: any, format?: string): string {
  if (format === 'currency' && typeof value === 'number') {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  }
  return String(value);
}
</script>

<style scoped>
.data-table {
  width: 100%;
}

.empty-state,
.loading-state {
  text-align: center;
  padding: 2rem;
  color: #666;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  text-align: left;
  padding: 0.75rem;
  border-bottom: 1px solid #ddd;
}

th {
  font-weight: 600;
  background-color: #f5f5f5;
}
</style>
