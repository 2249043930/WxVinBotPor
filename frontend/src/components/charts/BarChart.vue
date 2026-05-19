<template>
  <div ref="chartRef" class="chart-container"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'

interface DataItem {
  name: string
  value: number
}

interface Props {
  data: DataItem[]
  title?: string
  horizontal?: boolean
  color?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  horizontal: false,
  color: '#409EFF'
})

const chartRef = ref<HTMLDivElement>()
let chart: echarts.ECharts | null = null

const initChart = () => {
  if (!chartRef.value) return
  
  chart = echarts.init(chartRef.value)
  
  const names = props.data.map(item => item.name)
  const values = props.data.map(item => item.value)
  
  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: props.horizontal ? 'value' : 'category',
      data: props.horizontal ? undefined : names,
      axisLabel: {
        interval: 0,
        rotate: props.horizontal ? 0 : 30
      }
    },
    yAxis: {
      type: props.horizontal ? 'category' : 'value',
      data: props.horizontal ? names : undefined
    },
    series: [
      {
        type: 'bar',
        data: props.horizontal ? values.reverse() : values,
        itemStyle: {
          color: props.color,
          borderRadius: props.horizontal ? [0, 4, 4, 0] : [4, 4, 0, 0]
        },
        barWidth: '60%'
      }
    ]
  }
  
  chart.setOption(option)
}

const updateChart = () => {
  if (!chart) return
  
  const names = props.data.map(item => item.name)
  const values = props.data.map(item => item.value)
  
  chart.setOption({
    xAxis: {
      data: props.horizontal ? undefined : names
    },
    yAxis: {
      data: props.horizontal ? names : undefined
    },
    series: [{ data: props.horizontal ? values.reverse() : values }]
  })
}

const handleResize = () => {
  chart?.resize()
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chart?.dispose()
})

watch(() => props.data, updateChart, { deep: true })
</script>

<style scoped>
.chart-container {
  width: 100%;
  height: 100%;
}
</style>
