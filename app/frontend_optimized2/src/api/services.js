import api from './index'

/**
 * 上传简历文件
 * @param {File} file - 简历文件
 * @param {string} sessionId - 可选的会话 ID
 * @returns {Promise} 返回 session_id
 */
export function uploadResume(file, sessionId = '') {
  const formData = new FormData()
  formData.append('file', file)

  return api.post('/upload', formData, {
    params: { session_id: sessionId },
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 获取学生画像
 * @param {string} sessionId - 会话 ID
 * @returns {Promise} 返回学生画像数据
 */
export function getStudentProfile(sessionId = '') {
  return api.get('/profile/student', {
    params: { session_id: sessionId }
  })
}

/**
 * 获取岗位画像
 * @param {string} sessionId - 会话 ID
 * @returns {Promise} 返回岗位画像数据
 */
export function getJobProfile(sessionId = '') {
  return api.get('/profile/job', {
    params: { session_id: sessionId }
  })
}

/**
 * 获取匹配结果
 * @param {string} sessionId - 会话 ID
 * @returns {Promise} 返回匹配结果数据
 */
export function getMatchResult(sessionId = '') {
  return api.get('/match/result', {
    params: { session_id: sessionId }
  })
}

/**
 * 分析岗位并生成画像和匹配结果
 * @param {string} jobName - 岗位名称
 * @param {string} jobDescription - 岗位描述
 * @param {string} sessionId - 会话 ID
 * @returns {Promise} 返回岗位画像和匹配结果
 */
export function analyzeJob(jobName, jobDescription = '', sessionId = '') {
  return api.post('/job/analyze', {
    job_name: jobName,
    job_description: jobDescription
  }, {
    params: { session_id: sessionId }
  })
}

/**
 * 获取会话状态
 * @param {string} sessionId - 会话 ID
 * @returns {Promise} 返回会话状态
 */
export function getSession(sessionId) {
  return api.get(`/session/${sessionId}`)
}

/**
 * 删除会话
 * @param {string} sessionId - 会话 ID
 * @returns {Promise} 删除结果
 */
export function deleteSession(sessionId) {
  return api.delete(`/session/${sessionId}`)
}

/**
 * 流式对话
 * @param {string} message - 用户消息
 * @param {string} sessionId - 会话 ID
 * @returns {ReadableStream} 返回流式响应
 */
export async function chatStream(message, sessionId = '') {
  const response = await fetch('/api/chat/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      message,
      session_id: sessionId
    })
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new Error(error.detail || '对话请求失败')
  }

  return response.body
}

/**
 * 上报前端日志
 * @param {string} level - 日志级别 (INFO, WARN, ERROR)
 * @param {string} message - 日志消息
 */
export function sendLog(level, message) {
  const logEntry = {
    timestamp: new Date().toISOString(),
    level,
    message
  }

  // 使用 sendBeacon 确保日志在页面卸载时也能发送
  navigator.sendBeacon('/api/log', JSON.stringify(logEntry))
}
