import { http } from '@/services/http'

/**
 * 登录接口。
 * 后端当前使用表单数据，因此这里继续沿用 FormData 以保持兼容。
 */
export async function loginByPassword(payload) {
  const formData = new FormData()
  formData.append('email', payload.email)
  formData.append('password', payload.password)

  const { data } = await http.put('/user/login', formData)
  return data
}

/**
 * 注册接口。
 */
export async function registerByPassword(payload) {
  const { data } = await http.post('/user/register', {
    email: payload.email,
    password: payload.password,
  })

  return data
}

/**
 * 获取当前登录用户信息。
 */
export async function fetchUserProfile() {
  const { data } = await http.get('/user/info')
  return data
}
