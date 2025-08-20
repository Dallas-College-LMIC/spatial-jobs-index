<template>
  <div class="data-table-wrapper">
    <table :class="tableClass">
      <thead>
        <tr>
          <th v-for="column in columns" :key="column.key">
            <button v-if="column.sortable" class="sort-button" @click="handleSort(column)">
              {{ column.label }}
            </button>
            <span v-else>{{ column.label }}</span>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="data.length === 0">
          <td :colspan="columns.length" class="empty-state">
            No data available
          </td>
        </tr>
        <tr v-else v-for="(row, index) in paginatedData" :key="row.id || index">
          <td v-for="column in columns" :key="column.key">
            {{ formatValue(row[column.key], column.format) }}
          </td>
        </tr>
      </tbody>
    </table>

    <div v-if="pageSize" class="pagination">
      <button class="prev-page">Previous</button>
      <span class="page-info">Page 1</span>
      <button class="next-page">Next</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';

interface Column {
  key: string;
  label: string;
  sortable?: boolean;
  format?: 'currency' | 'percentage' | 'number';
}

interface Props {
  data: Record<string, any>[];
  columns: Column[];
  tableClass?: string;
  pageSize?: number;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  sort: [{ column: string; direction: 'asc' | 'desc' | null }];
}>();

const currentPage = ref(1);

const paginatedData = computed(() => {
  if (!props.pageSize) {
    return props.data;
  }

  const start = (currentPage.value - 1) * props.pageSize;
  const end = start + props.pageSize;
  return props.data.slice(start, end);
});

const handleSort = (column: Column) => {
  emit('sort', { column: column.key, direction: 'asc' });
};

const formatValue = (value: any, format?: string) => {
  if (format === 'currency') {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  }
  return value;
};
</script>
