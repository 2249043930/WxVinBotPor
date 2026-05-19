<template>
  <div class="page-container">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-row">
      <el-col :xs="24" :sm="8">
        <div class="stat-card">
          <div class="stat-card-header">
            <span class="stat-card-title">LLM识别成功次数</span>
            <div class="stat-card-icon" style="background-color: #F0F9EB; color: #67C23A;">
              <el-icon :size="24"><SuccessFilled /></el-icon>
            </div>
          </div>
          <div class="stat-card-value">{{ formatNumber(stats.success_count) }}</div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="8">
        <div class="stat-card">
          <div class="stat-card-header">
            <span class="stat-card-title">LLM识别失败次数</span>
            <div class="stat-card-icon" style="background-color: #FEF0F0; color: #F56C6C;">
              <el-icon :size="24"><CircleCloseFilled /></el-icon>
            </div>
          </div>
          <div class="stat-card-value">{{ formatNumber(stats.fail_count) }}</div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="8">
        <div class="stat-card">
          <div class="stat-card-header">
            <span class="stat-card-title">LLM识别成功率</span>
            <div class="stat-card-icon" style="background-color: #ECF5FF; color: #409EFF;">
              <el-icon :size="24"><TrendCharts /></el-icon>
            </div>
          </div>
          <div class="stat-card-value">{{ stats.success_rate }}%</div>
          <el-progress :percentage="stats.success_rate" :color="progressColor" />
        </div>
      </el-col>
    </el-row>
    
    <!-- 消费记录 -->
    <el-card class="record-card">
      <template #header>
        <div class="card-header">
          <span>消费记录</span>
          <el-button type="primary" @click="handleExport">
            <el-icon><Download /></el-icon>导出
          </el-button>
        </div>
      </template>
      
      <el-table :data="tableData" stripe v-loading="loading">
        <el-table-column type="index" label="序号" width="80" />
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column prop="count" label="识别次数" />
        <el-table-column prop="success_count" label="成功次数">
          <template #default="{ row }">
            <span style="color: var(--success-color);">{{ row.success_count }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="fail_count" label="失败次数">
          <template #default="{ row }">
            <span style="color: var(--danger-color);">{{ row.fail_count }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="success_rate" label="成功率">
          <template #default="{ row }">
            <el-progress :percentage="row.success_rate" :show-text="true" />
          </template>
        </el-table-column>
      </el-table>
      
      <Pagination
        :total="total"
        :page="query.page"
        :limit="query.pageSize"
        @pagination="handlePagination"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import Pagination from '@/components/common/Pagination.vue'
import { formatNumber } from '@/utils/format'
import { accountApi } from '@/api/account'
import type { LLMStats, DailyStat } from '@/api/account'

const loading = ref(false)
const stats = reactive<LLMStats>({
  success_count: 0,
  fail_count: 0,
  success_rate: 0
})
const tableData = ref<DailyStat[]>([])
const total = ref(0)
const query = reactive({
  page: 1,
  pageSize: 10
})

const progressColor = [
  { color: '#F56C6C', percentage: 60 },
  { color: '#E6A23C', percentage: 80 },
  { color: '#67C23A', percentage: 100 }
]

// 加载统计数据
const loadStats = async () => {
  try {
    const res = await accountApi.getLLMStats()
    stats.success_count = res.success_count || 0
    stats.fail_count = res.fail_count || 0
    stats.success_rate = res.success_rate || 0
  } catch (error) {
    console.error('获取LLM统计数据失败', error)
    ElMessage.error('获取统计数据失败')
  }
}

// 加载每日统计
const loadData = async () => {
  loading.value = true
  try {
    const res = await accountApi.getDailyStats({
      page: query.page,
      page_size: query.pageSize
    })
    tableData.value = res.list || []
    total.value = res.total || 0
  } catch (error) {
    console.error('获取每日统计失败', error)
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

const handlePagination = ({ page, limit }: { page: number; limit: number }) => {
  query.page = page
  query.pageSize = limit
  loadData()
}

const handleExport = () => {
  // TODO: 实现导出功能
  ElMessage.success('导出成功')
}

onMounted(() => {
  loadStats()
  loadData()
})
</script>

<style scoped>
.stat-row {
  margin-bottom: var(--spacing-lg);
}

.stat-row .el-col {
  margin-bottom: var(--spacing-md);
}

.record-card {
  margin-top: var(--spacing-lg);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
