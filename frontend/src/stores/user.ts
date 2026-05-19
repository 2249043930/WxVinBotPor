import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import { setToken, setUserInfo, clearAuth, getUserInfo } from '@/utils/auth'
import type { LoginForm, UserInfo } from '@/types/user'

export const useUserStore = defineStore('user', () => {
  // State
  const userInfo = ref<UserInfo | null>(getUserInfo())
  const token = ref<string>('')
  const loading = ref(false)

  // Getters
  const isLoggedIn = computed(() => !!userInfo.value)
  const nickname = computed(() => userInfo.value?.nickname || '')
  const username = computed(() => userInfo.value?.username || '')

  // Actions
  const login = async (form: LoginForm) => {
    loading.value = true
    try {
      // 登录前清除之前的认证信息，避免干扰
      clearAuth()
      token.value = ''
      userInfo.value = null
      
      const res = await authApi.login(form)
      token.value = res.token
      userInfo.value = res.userInfo
      setToken(res.token)
      setUserInfo(res.userInfo)
      return true
    } catch (error) {
      // 登录失败也要清除认证信息
      clearAuth()
      token.value = ''
      userInfo.value = null
      return false
    } finally {
      loading.value = false
    }
  }

  const fetchUserInfo = async () => {
    try {
      const res = await authApi.getUserInfo()
      userInfo.value = res
      setUserInfo(res)
      return res
    } catch (error) {
      return null
    }
  }

  const logout = async () => {
    try {
      await authApi.logout()
    } finally {
      clearAuth()
      userInfo.value = null
      token.value = ''
    }
  }

  return {
    userInfo,
    token,
    loading,
    isLoggedIn,
    nickname,
    username,
    login,
    fetchUserInfo,
    logout
  }
})
