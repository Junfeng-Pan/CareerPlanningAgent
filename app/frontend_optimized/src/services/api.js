import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建 axios 实例
const api = axios.create({
  baseURL: '/api',
  timeout: 120000, // 120 秒超时
  headers: {
    'Content-Type': 'application/json'
  }
})

// 响应拦截器
api.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error)
    ElMessage.error(error.message || '请求失败，请检查网络连接')
    return Promise.reject(error)
  }
)

// 会话管理
let sessionId = null

export function getSessionId() {
  return sessionId
}

export function setSessionId(id) {
  sessionId = id
}

// API 方法
export const apiService = {
  // 上传简历
  async uploadResume(file) {
    const formData = new FormData()
    formData.append('file', file)
    if (sessionId) {
      formData.append('session_id', sessionId)
    }
    const response = await api.post('/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    if (response.data.session_id) {
      setSessionId(response.data.session_id)
    }
    return response.data
  },

  // 获取学生画像
  async getStudentProfile() {
    const params = sessionId ? { session_id: sessionId } : {}
    const response = await api.get('/profile/student', { params })
    return response.data
  },

  // 获取岗位画像
  async getJobProfile() {
    const params = sessionId ? { session_id: sessionId } : {}
    const response = await api.get('/profile/job', { params })
    return response.data
  },

  // 获取匹配结果
  async getMatchResult() {
    const params = sessionId ? { session_id: sessionId } : {}
    const response = await api.get('/match/result', { params })
    return response.data
  },

  // 分析岗位
  async analyzeJob(jobName, jobDescription = '') {
    const params = sessionId ? { session_id: sessionId } : {}
    const response = await api.post('/job/analyze', {
      job_name: jobName,
      job_description: jobDescription
    }, { params })
    return response.data
  },

  // 流式对话
  async chatStream(message, onEvent) {
    const currentSessionId = sessionId
    const params = { session_id: currentSessionId }

    const response = await fetch('/api/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, session_id: currentSessionId })
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    try {
      while (true) {
        const { value, done } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || '' // 保留不完整的一行

        for (const line of lines) {
          if (line.trim()) {
            try {
              const event = JSON.parse(line)
              onEvent(event)
            } catch (e) {
              console.warn('Failed to parse event:', line, e)
            }
          }
        }
      }

      // 处理剩余内容
      if (buffer.trim()) {
        try {
          const event = JSON.parse(buffer)
          onEvent(event)
        } catch (e) {
          console.warn('Failed to parse remaining buffer:', buffer)
        }
      }
    } catch (error) {
      console.error('Stream reading error:', error)
      throw error
    }
  },

  // 获取会话状态
  async getSessionStatus() {
    if (!sessionId) return null
    const response = await api.get(`/session/${sessionId}`)
    return response.data
  },

  // 删除会话
  async deleteSession() {
    if (!sessionId) return
    await api.delete(`/session/${sessionId}`)
    sessionId = null
  }
}

export default api
