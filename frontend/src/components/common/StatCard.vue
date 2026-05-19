<template>
  <div class="stat-card">
    <div class="stat-card-header">
      <span class="stat-card-title">{{ title }}</span>
      <div
        class="stat-card-icon"
        :style="{ backgroundColor: iconBgColor, color: iconColor }"
      >
        <el-icon :size="24">
          <component :is="icon" />
        </el-icon>
      </div>
    </div>
    <div class="stat-card-value">
      {{ formattedValue }}
      <span v-if="suffix" class="stat-card-suffix">{{ suffix }}</span>
    </div>
    <div v-if="trend !== undefined" class="stat-card-footer">
      <span class="stat-card-trend" :class="trendUp ? 'up' : 'down'">
        <el-icon>
          <ArrowUp v-if="trendUp" />
          <ArrowDown v-else />
        </el-icon>
        {{ Math.abs(trend) }}%
      </span>
      <span>较上期</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { formatNumber } from '@/utils/format'

interface Props {
  title: string
  value: number | string
  trend?: number
  trendUp?: boolean
  icon: string
  iconColor: string
  iconBgColor: string
  suffix?: string
  decimals?: number
}

const props = withDefaults(defineProps<Props>(), {
  decimals: 0
})

const formattedValue = computed(() => {
  if (typeof props.value === 'number') {
    return formatNumber(props.value, props.decimals)
  }
  return props.value
})
</script>

<style scoped>
.stat-card {
  background: var(--bg-white);
  border-radius: var(--border-radius-large);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-base);
}

.stat-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
}

.stat-card-title {
  font-size: 14px;
  color: var(--text-secondary);
}

.stat-card-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--border-radius-base);
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-card-value {
  font-size: 28px;
  font-weight: bold;
  color: var(--text-primary);
  margin-bottom: var(--spacing-sm);
}

.stat-card-suffix {
  font-size: 14px;
  font-weight: normal;
  color: var(--text-secondary);
  margin-left: 4px;
}

.stat-card-footer {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: 12px;
  color: var(--text-secondary);
}

.stat-card-trend {
  display: flex;
  align-items: center;
  gap: 4px;
}

.stat-card-trend.up {
  color: var(--success-color);
}

.stat-card-trend.down {
  color: var(--danger-color);
}
</style>
