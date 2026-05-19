// 验证工具函数

export const isEmpty = (value: any): boolean => {
  return value === null || value === undefined || value === ''
}

export const isPhone = (phone: string): boolean => {
  const reg = /^1[3-9]\d{9}$/
  return reg.test(phone)
}

export const isEmail = (email: string): boolean => {
  const reg = /^[\w-]+(\.[\w-]+)*@[\w-]+(\.[\w-]+)+$/
  return reg.test(email)
}

export const isUsername = (username: string): boolean => {
  const reg = /^[a-zA-Z0-9_]{4,20}$/
  return reg.test(username)
}

export const isPassword = (password: string): boolean => {
  return password.length >= 6 && password.length <= 20
}

export const isVin = (vin: string): boolean => {
  const reg = /^[A-HJ-NPR-Z0-9]{17}$/i
  return reg.test(vin)
}
