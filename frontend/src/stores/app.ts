import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  // State
  const sidebarCollapsed = ref(false)
  const device = ref<'desktop' | 'mobile'>('desktop')

  // Actions
  const toggleSidebar = () => {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  const setSidebarCollapsed = (collapsed: boolean) => {
    sidebarCollapsed.value = collapsed
  }

  const setDevice = (type: 'desktop' | 'mobile') => {
    device.value = type
  }

  return {
    sidebarCollapsed,
    device,
    toggleSidebar,
    setSidebarCollapsed,
    setDevice
  }
})
