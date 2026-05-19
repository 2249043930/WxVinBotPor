<template>
  <div class="pagination-container">
    <el-pagination
      :current-page="page"
      :page-size="limit"
      :page-sizes="[10, 20, 50, 100]"
      :total="total"
      layout="total, sizes, prev, pager, next, jumper"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
    />
  </div>
</template>

<script setup lang="ts">
interface Props {
  total: number
  page: number
  limit: number
}

const props = defineProps<Props>()
const emit = defineEmits<{
  pagination: [{ page: number; limit: number }]
}>()

const handleSizeChange = (val: number) => {
  emit('pagination', { page: 1, limit: val })
}

const handleCurrentChange = (val: number) => {
  emit('pagination', { page: val, limit: props.limit })
}
</script>

<style scoped>
.pagination-container {
  display: flex;
  justify-content: flex-end;
  padding: var(--spacing-md) 0;
}
</style>
