<template>
  <aside class="sidebar" :class="{ collapsed: appStore.sidebarCollapsed }">
    <div class="sidebar-header">
      <template v-if="!appStore.sidebarCollapsed">
        WxVinBot
      </template>
      <template v-else>
        WB
      </template>
    </div>
    <el-menu
      :default-active="activeMenu"
      :collapse="appStore.sidebarCollapsed"
      :collapse-transition="false"
      router
      class="sidebar-menu"
      background-color="#304156"
      text-color="#bfcbd9"
      active-text-color="#409EFF"
    >
      <template v-for="route in menuRoutes" :key="route.path">
        <!-- 无子菜单 -->
        <el-menu-item v-if="!route.children" :index="route.path">
          <el-icon v-if="route.meta?.icon">
            <component :is="route.meta.icon" />
          </el-icon>
          <template #title>{{ route.meta?.title }}</template>
        </el-menu-item>
        
        <!-- 有子菜单 -->
        <el-sub-menu v-else :index="route.path">
          <template #title>
            <el-icon v-if="route.meta?.icon">
              <component :is="route.meta.icon" />
            </el-icon>
            <span>{{ route.meta?.title }}</span>
          </template>
          <el-menu-item
            v-for="child in route.children"
            :key="resolvePath(route.path, child.path)"
            :index="resolvePath(route.path, child.path)"
            class="sub-menu-item"
          >
            <span class="sub-menu-title">{{ child.meta?.title }}</span>
          </el-menu-item>
        </el-sub-menu>
      </template>
    </el-menu>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { routes } from '@/router/menu'

const route = useRoute()
const appStore = useAppStore()

const menuRoutes = computed(() => routes)

const activeMenu = computed(() => {
  const { path } = route
  return path
})

// 解析完整路径
const resolvePath = (parentPath: string, childPath: string) => {
  if (childPath.startsWith('/')) {
    return childPath
  }
  return parentPath + '/' + childPath
}
</script>

<style scoped>
.sidebar {
  width: var(--sidebar-width);
  height: 100%;
  background-color: #304156;
  transition: width 0.3s;
  flex-shrink: 0;
  overflow: hidden;
}

.sidebar.collapsed {
  width: var(--sidebar-collapsed-width);
}

.sidebar-header {
  height: var(--header-height);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  white-space: nowrap;
}

.sidebar-menu {
  border-right: none;
}

.sidebar-menu :deep(.el-menu) {
  background-color: transparent;
  border-right: none;
}

.sidebar-menu :deep(.el-menu-item),
.sidebar-menu :deep(.el-sub-menu__title) {
  color: #bfcbd9;
}

.sidebar-menu :deep(.el-menu-item:hover),
.sidebar-menu :deep(.el-sub-menu__title:hover) {
  background-color: #263445;
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  color: var(--primary-color);
  background-color: #263445;
}

/* 子菜单项样式 - 让文字对齐更整齐 */
.sidebar-menu :deep(.sub-menu-item) {
  padding-left: 50px !important;
}

.sidebar-menu :deep(.sub-menu-title) {
  display: inline-block;
  min-width: 100px;
}
</style>
