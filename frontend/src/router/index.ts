import { createRouter, createWebHistory } from 'vue-router'
import { isAuthenticated } from '@/utils/auth'
import { useUserStore } from '@/stores/user'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/login/index.vue'),
      meta: { public: true }
    },
    {
      path: '/',
      name: 'Layout',
      component: () => import('@/components/layout/MainContent.vue'),
      redirect: '/dashboard',
      children: [
        {
          path: 'dashboard',
          name: 'Dashboard',
          component: () => import('@/views/dashboard/index.vue'),
          meta: { title: '数据看板', icon: 'DataLine' }
        },
        {
          path: 'system',
          name: 'System',
          redirect: '/system/api-config',
          meta: { title: '系统管理', icon: 'Setting' },
          children: [
            {
              path: 'api-config',
              name: 'ApiConfig',
              component: () => import('@/views/system/ApiConfig.vue'),
              meta: { title: '接口配置' }
            },
            {
              path: 'user',
              name: 'UserManage',
              component: () => import('@/views/system/UserManage.vue'),
              meta: { title: '用户管理' }
            },
            {
              path: 'log',
              name: 'LogManage',
              component: () => import('@/views/system/LogManage.vue'),
              meta: { title: '日志管理' }
            },
            {
              path: 'wechat',
              name: 'WechatManage',
              component: () => import('@/views/system/WechatManage.vue'),
              meta: { title: '微信管理' }
            },
            {
              path: 'account',
              name: 'AccountManage',
              component: () => import('@/views/system/AccountManage.vue'),
              meta: { title: '账户管理' }
            }
          ]
        },
        {
          path: 'carModel',
          name: 'CarModel',
          redirect: 'config',
          meta: { title: '车型配置', icon: 'Van' },
          children: [
            {
              path: 'config',
              name: 'CarModelConfig',
              component: () => import('@/views/carModel/CarModelConfig.vue'),
              meta: { title: '群聊配置' }
            },
            {
              path: 'brand',
              name: 'CarModelBrand',
              component: () => import('@/views/carModel/CarModelBrand.vue'),
              meta: { title: '车型品牌管理' }
            }
          ]
        },
        {
          path: 'group',
          name: 'Group',
          redirect: '/group/manage',
          meta: { title: '厂群管理', icon: 'ChatDotSquare' },
          children: [
            {
              path: 'manage',
              name: 'GroupManage',
              component: () => import('@/views/group/GroupManage.vue'),
              meta: { title: '群管理' }
            },
            {
              path: 'vin',
              name: 'VinRecord',
              component: () => import('@/views/group/VinRecord.vue'),
              meta: { title: '车架号记录' }
            }
          ]
        },
        {
          path: 'statistics',
          name: 'Statistics',
          redirect: '/statistics/message',
          meta: { title: '数据统计', icon: 'TrendCharts' },
          children: [
            {
              path: 'message',
              name: 'MessageRecord',
              component: () => import('@/views/statistics/MessageRecord.vue'),
              meta: { title: '消息记录' }
            }
          ]
        }
      ]
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: () => import('@/views/login/index.vue')
    }
  ]
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  
  if (to.meta.public) {
    next()
    return
  }
  
  if (!isAuthenticated()) {
    next('/login')
    return
  }
  
  if (!userStore.userInfo) {
    await userStore.fetchUserInfo()
  }
  
  next()
})

export default router
