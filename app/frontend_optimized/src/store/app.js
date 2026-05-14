import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiService, getSessionId, setSessionId } from '@/services/api'

export const useAppStore = defineStore('app', () => {
  // 状态
  const sessionId = ref(getSessionId())
  const hasResume = ref(false)
  const studentProfile = ref(null)
  const jobProfile = ref(null)
  const matchResult = ref(null)
  const loading = ref(false)
  const chatMessages = ref([])
  const isChatStreaming = ref(false)

  // Actions
  function setSession(id) {
    setSessionId(id)
    sessionId.value = id
  }

  function clearSession() {
    setSessionId(null)
    sessionId.value = null
    hasResume.value = false
    studentProfile.value = null
    jobProfile.value = null
    matchResult.value = null
    chatMessages.value = []
  }

  // 上传简历
  async function uploadResume(file) {
    loading.value = true
    try {
      const result = await apiService.uploadResume(file)
      hasResume.value = true
      // 上传成功后自动获取学生画像（不阻塞，让页面先显示成功）
      fetchStudentProfile()
      return result
    } finally {
      loading.value = false
    }
  }

  // 获取学生画像
  async function fetchStudentProfile() {
    try {
      const result = await apiService.getStudentProfile()
      if (result.student_profile) {
        studentProfile.value = result.student_profile
        return result.student_profile
      }
    } catch (error) {
      console.error('获取学生画像失败:', error)
    }
    return null
  }

  // 获取岗位画像
  async function fetchJobProfile() {
    try {
      const result = await apiService.getJobProfile()
      if (result.job_profile) {
        jobProfile.value = result.job_profile
        return result.job_profile
      }
    } catch (error) {
      console.error('获取岗位画像失败:', error)
    }
    return null
  }

  // 获取匹配结果
  async function fetchMatchResult() {
    try {
      const result = await apiService.getMatchResult()
      if (result.match_result) {
        matchResult.value = result.match_result
        return result.match_result
      }
    } catch (error) {
      console.error('获取匹配结果失败:', error)
    }
    return null
  }

  // 分析岗位
  async function analyzeJob(jobName, jobDescription = '') {
    loading.value = true
    try {
      const result = await apiService.analyzeJob(jobName, jobDescription)
      if (result.success) {
        if (result.job_profile) {
          jobProfile.value = result.job_profile
        }
        if (result.match_result) {
          matchResult.value = result.match_result
        }
      }
      return result
    } finally {
      loading.value = false
    }
  }

  // 发送消息（流式）
  async function sendMessage(message) {
    isChatStreaming.value = true
    const userMessage = { role: 'user', content: message }
    chatMessages.value.push(userMessage)

    // 创建一个空的 assistant 消息，用于流式更新
    const assistantMessage = ref({ role: 'assistant', content: '', reasoning: '', toolCalls: [] })
    chatMessages.value.push(assistantMessage.value)

    try {
      await apiService.chatStream(message, (event) => {
        const lastMsg = chatMessages.value[chatMessages.value.length - 1]
        if (event.type === 'reasoning') {
          lastMsg.reasoning += event.content
        } else if (event.type === 'answer') {
          lastMsg.content += event.content
        } else if (event.type === 'tool_call') {
          lastMsg.toolCalls.push({ name: event.name, args: event.args })
        } else if (event.type === 'tool_result') {
          const lastToolCall = lastMsg.toolCalls[lastMsg.toolCalls.length - 1]
          if (lastToolCall) {
            lastToolCall.result = event.result
          }
        } else if (event.type === 'final_answer') {
          lastMsg.content = event.content
        }
      })
    } catch (error) {
      console.error('对话失败:', error)
      const lastMsg = chatMessages.value[chatMessages.value.length - 1]
      lastMsg.content = '抱歉，连接失败，请稍后重试。'
    } finally {
      isChatStreaming.value = false
    }

    // 对话后更新画像和匹配结果
    await fetchStudentProfile()
    await fetchJobProfile()
    await fetchMatchResult()
  }

  // 清除对话历史
  function clearChat() {
    chatMessages.value = []
  }

  return {
    // State
    sessionId,
    hasResume,
    studentProfile,
    jobProfile,
    matchResult,
    loading,
    chatMessages,
    isChatStreaming,
    // Actions
    setSession,
    clearSession,
    uploadResume,
    fetchStudentProfile,
    fetchJobProfile,
    fetchMatchResult,
    analyzeJob,
    sendMessage,
    clearChat
  }
})
