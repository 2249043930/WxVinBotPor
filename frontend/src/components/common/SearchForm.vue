<template>
  <div class="search-form-container">
    <el-form :model="form" inline>
      <el-form-item
        v-for="field in fields"
        :key="field.prop"
        :label="field.label"
      >
        <!-- 输入框 -->
        <el-input
          v-if="field.type === 'input'"
          v-model="form[field.prop]"
          :placeholder="field.placeholder"
          clearable
          @keyup.enter="handleSearch"
        />
        
        <!-- 选择框 -->
        <el-select
          v-else-if="field.type === 'select'"
          v-model="form[field.prop]"
          :placeholder="field.placeholder"
          clearable
        >
          <el-option
            v-for="opt in field.options"
            :key="opt.value"
            :label="opt.label"
            :value="opt.value"
          />
        </el-select>
        
        <!-- 日期范围 -->
        <el-date-picker
          v-else-if="field.type === 'daterange'"
          v-model="form[field.prop]"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
        />
      </el-form-item>
      
      <el-form-item>
        <el-button type="primary" @click="handleSearch">
          <el-icon><Search /></el-icon>搜索
        </el-button>
        <el-button @click="handleReset">
          <el-icon><Refresh /></el-icon>重置
        </el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'

interface Field {
  prop: string
  label: string
  type: 'input' | 'select' | 'daterange'
  placeholder?: string
  options?: { label: string; value: string | number }[]
}

interface Props {
  fields: Field[]
}

const props = defineProps<Props>()
const emit = defineEmits<{
  search: [data: Record<string, any>]
  reset: []
}>()

const form = reactive<Record<string, any>>({})

// 初始化表单
props.fields.forEach(field => {
  form[field.prop] = ''
})

const handleSearch = () => {
  emit('search', { ...form })
}

const handleReset = () => {
  props.fields.forEach(field => {
    form[field.prop] = ''
  })
  emit('reset')
}
</script>

<style scoped>
.search-form-container {
  background: var(--bg-white);
  padding: var(--spacing-md);
  border-radius: var(--border-radius-base);
  margin-bottom: var(--spacing-md);
}

.search-form-container :deep(.el-form-item) {
  margin-bottom: 0;
  margin-right: var(--spacing-md);
}
</style>
