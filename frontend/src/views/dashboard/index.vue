<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-row">
      <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="card in statCards" :key="card.title">
        <StatCard
          :title="card.title"
          :value="card.value"
          :trend="card.trend"
          :trend-up="card.trendUp"
          :icon="card.icon"
          :icon-color="card.iconColor"
          :icon-bg-color="card.iconBgColor"
          :suffix="card.suffix"
        />
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :xs="24" :lg="12">
        <div class="chart-card">
          <div class="chart-card-header">
            <span class="chart-card-title">车辆类型统计</span>
          </div>
          <div class="chart-card-body">
            <PieChart :data="vehicleTypeData" />
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :lg="12">
        <div class="chart-card">
          <div class="chart-card-header">
            <span class="chart-card-title">热门车型排行</span>
          </div>
          <div class="chart-card-body">
            <BarChart :data="hotModelsData" horizontal />
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-row">
      <el-col :xs="24" :lg="12">
        <div class="chart-card">
          <div class="chart-card-header">
            <span class="chart-card-title">排量分布统计</span>
          </div>
          <div class="chart-card-body">
            <PieChart :data="displacementData" :color="['#67C23A', '#E6A23C', '#F56C6C', '#409EFF', '#909399']" />
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :lg="12">
        <div class="chart-card">
          <div class="chart-card-header">
            <span class="chart-card-title">新增趋势（近30天）</span>
          </div>
          <div class="chart-card-body">
            <LineChart :data="trendData" area />
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 数据列表 -->
    <el-row :gutter="20" class="table-row">
      <el-col :xs="24" :lg="12">
        <div class="card">
          <div class="card-header">
            <span class="card-title">热门车型排行</span>
          </div>
          <el-table :data="hotModelsTable" stripe v-loading="loading">
            <el-table-column type="index" label="排名" width="80" />
            <el-table-column prop="modelName" label="车型" />
            <el-table-column prop="count" label="查询次数" width="100" />
            <el-table-column label="趋势" width="100">
              <template #default="{ row }">
                <span :class="row.trend > 0 ? 'text-success' : row.trend < 0 ? 'text-danger' : 'text-gray'">
                  <el-icon><ArrowUp v-if="row.trend > 0" /><ArrowDown v-else-if="row.trend < 0" /><Minus v-else /></el-icon>
                  {{ row.trend ? Math.abs(row.trend) + '%' : '-' }}
                </span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>
      <el-col :xs="24" :lg="12">
        <div class="card">
          <div class="card-header">
            <span class="card-title">最近识别记录</span>
          </div>
          <el-table :data="recentRecords" stripe v-loading="loading">
            <el-table-column prop="vin" label="车架号" show-overflow-tooltip />
            <el-table-column prop="model" label="车型" show-overflow-tooltip />
            <el-table-column prop="createTime" label="时间" width="160">
              <template #default="{ row }">
                {{ formatDate(row.createTime, 'MM-DD HH:mm') }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.status === 1 ? 'success' : 'danger'" size="small">
                  {{ row.status === 1 ? '成功' : '失败' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>
    </el-row>

    <!-- 群活跃度统计 - 图表展示 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :xs="24" :lg="12">
        <div class="chart-card">
          <div class="chart-card-header">
            <span class="chart-card-title">群活跃度排行（近30天含车架号图片消息）</span>
            <span class="chart-card-subtitle">共 {{ groupActivityStats.total_vin_images }} 条VIN图片消息</span>
          </div>
          <div class="chart-card-body">
            <BarChart :data="groupActivityChartData" horizontal />
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :lg="12">
        <div class="chart-card">
          <div class="chart-card-header">
            <span class="chart-card-title">群活跃度占比分布</span>
          </div>
          <div class="chart-card-body">
            <PieChart :data="groupActivityPieData" />
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import StatCard from '@/components/common/StatCard.vue'
import PieChart from '@/components/charts/PieChart.vue'
import BarChart from '@/components/charts/BarChart.vue'
import LineChart from '@/components/charts/LineChart.vue'
import { dashboardApi } from '@/api/dashboard'
import { formatDate } from '@/utils/format'
import type { StatCardData, HotModelRank, RecentRecord, GroupActivityStats } from '@/types/dashboard'

const loading = ref(false)
const groupActivityLoading = ref(false)

// 统计卡片数据
const statCards = ref<StatCardData[]>([
  { title: '数据库车辆总数', value: 0, trend: 0, trendUp: true, icon: 'Van', iconColor: '#409EFF', iconBgColor: '#ECF5FF' },
  { title: '本月新增', value: 0, trend: 0, trendUp: true, icon: 'Calendar', iconColor: '#67C23A', iconBgColor: '#F0F9EB' },
  { title: '本周新增', value: 0, trend: 0, trendUp: true, icon: 'Date', iconColor: '#E6A23C', iconBgColor: '#FDF6EC' },
  { title: '今日新增', value: 0, icon: 'Sunny', iconColor: '#F56C6C', iconBgColor: '#FEF0F0' },
  { title: '群聊数量', value: 0, icon: 'ChatDotSquare', iconColor: '#909399', iconBgColor: '#F4F4F5' },
  { title: 'LLM识别成功率', value: 0, trend: 0, trendUp: true, icon: 'CircleCheck', iconColor: '#409EFF', iconBgColor: '#ECF5FF', suffix: '%' }
])

// 群活跃度统计数据
const groupActivityStats = ref<GroupActivityStats>({
  total_vin_images: 0,
  period_days: 30,
  group_stats: []
})

// 群活跃度图表数据（计算属性）
const groupActivityChartData = computed(() => {
  return groupActivityStats.value.group_stats.map(item => ({
    name: item.group_name.length > 15 ? item.group_name.substring(0, 15) + '...' : item.group_name,
    value: item.message_count
  }))
})

const groupActivityPieData = computed(() => {
  return groupActivityStats.value.group_stats.map(item => ({
    name: item.group_name.length > 10 ? item.group_name.substring(0, 10) + '...' : item.group_name,
    value: item.message_count
  }))
})

// 图表数据
const vehicleTypeData = ref<{name: string, value: number}[]>([])
const hotModelsData = ref<{name: string, value: number}[]>([])
const displacementData = ref<{name: string, value: number}[]>([])
const trendData = ref<{date: string, value: number}[]>([])

// 表格数据
const hotModelsTable = ref<HotModelRank[]>([])
const recentRecords = ref<RecentRecord[]>([])

// 加载统计数据
const loadStats = async () => {
  try {
    const stats = await dashboardApi.getStats()
    statCards.value[0].value = stats.totalVehicles || 0
    statCards.value[1].value = stats.monthNew || 0
    statCards.value[1].trend = stats.monthGrowth || 0
    statCards.value[1].trendUp = (stats.monthGrowth || 0) >= 0
    statCards.value[2].value = stats.weekNew || 0
    statCards.value[2].trend = stats.weekGrowth || 0
    statCards.value[2].trendUp = (stats.weekGrowth || 0) >= 0
    statCards.value[3].value = stats.todayNew || 0
    statCards.value[4].value = stats.groupCount || 0
    statCards.value[5].value = stats.llmSuccessRate || 0
    statCards.value[5].trend = 0
  } catch (error) {
    console.error('获取统计数据失败', error)
    ElMessage.error('获取统计数据失败')
  }
}

// 加载图表数据
const loadCharts = async () => {
  try {
    const chartData = await dashboardApi.getCharts()
    vehicleTypeData.value = chartData.vehicleTypePie || []
    hotModelsData.value = chartData.topModelsBar || []
    displacementData.value = chartData.displacementStats || []
    trendData.value = chartData.trendLine || []
  } catch (error) {
    console.error('获取图表数据失败', error)
  }
}

// 加载热门车型排行
const loadHotModels = async () => {
  try {
    const data = await dashboardApi.getHotModels()
    hotModelsTable.value = data || []
  } catch (error) {
    console.error('获取热门车型失败', error)
  }
}

// 加载最近记录
const loadRecentRecords = async () => {
  try {
    const data = await dashboardApi.getRecentRecords()
    recentRecords.value = data || []
  } catch (error) {
    console.error('获取最近记录失败', error)
  }
}

// 加载群活跃度统计
const loadGroupActivityStats = async () => {
  groupActivityLoading.value = true
  try {
    const result = await dashboardApi.getGroupActivityStats(30, 10)
    if (result) {
      groupActivityStats.value = result
    }
  } catch (error) {
    console.error('获取群活跃度统计失败', error)
  } finally {
    groupActivityLoading.value = false
  }
}

// 加载所有数据
const loadAllData = async () => {
  loading.value = true
  try {
    await Promise.all([
      loadStats(),
      loadCharts(),
      loadHotModels(),
      loadRecentRecords(),
      loadGroupActivityStats()
    ])
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadAllData()
})
</script>

<style scoped>
.dashboard {
  padding-bottom: var(--spacing-lg);
}

.stat-row {
  margin-bottom: var(--spacing-lg);
}

.stat-row .el-col {
  margin-bottom: var(--spacing-md);
}

.chart-row {
  margin-bottom: var(--spacing-lg);
}

.chart-row .el-col {
  margin-bottom: var(--spacing-md);
}

.chart-card {
  background: var(--bg-white);
  border-radius: var(--border-radius-large);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-base);
}

.chart-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
}

.chart-card-title {
  font-size: 16px;
  font-weight: 500;
  color: var(--text-primary);
}

.chart-card-body {
  height: 300px;
}

.table-row .el-col {
  margin-bottom: var(--spacing-md);
}

.card {
  background: var(--bg-white);
  border-radius: var(--border-radius-large);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-base);
}

.card-header {
  margin-bottom: var(--spacing-md);
}

.card-title {
  font-size: 16px;
  font-weight: 500;
  color: var(--text-primary);
}

.card-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
  margin-left: var(--spacing-sm);
}

.percentage-bar {
  width: 100%;
  padding: 0 10px;
}

.text-success {
  color: var(--success-color);
}

.text-danger {
  color: var(--danger-color);
}

.text-gray {
  color: #909399;
}
</style>
