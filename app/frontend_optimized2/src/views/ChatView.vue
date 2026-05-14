<template>
  <div class="chat-view">
    <div class="chat-container">
      <!-- 消息列表 -->
      <div class="messages-container" ref="messagesContainer">
        <div v-if="messages.length === 0 && !uploading" class="welcome-message">
          <el-empty description="开始与职业规划智能体对话吧">
            <el-upload
              drag
              :auto-upload="true"
              :http-request="handleFileUpload"
              :show-file-list="false"
              :before-upload="beforeFileUpload"
              accept=".txt,.docx,.pdf"
            >
              <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
              <div class="el-upload__text">
                拖拽简历文件到此处或<em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  支持 .txt / .docx / .pdf 格式
                </div>
              </template>
            </el-upload>
          </el-empty>
        </div>

        <!-- 上传加载状态 -->
        <div v-if="uploading" class="uploading-container">
          <el-card class="uploading-card">
            <div class="uploading-content">
              <el-icon class="uploading-icon" :size="48"><Loading /></el-icon>
              <div class="uploading-text">正在上传并解析简历...</div>
              <el-progress :percentage="uploadProgress" :indeterminate="true" :stroke-width="3" />
              <div class="uploading-hint">
                <el-text size="small" type="info">这可能需要 10-30 秒，请耐心等待</el-text>
              </div>
            </div>
          </el-card>
        </div>

        <div v-else-if="messages.length > 0" class="messages">
          <div
            v-for="(msg, index) in messages"
            :key="index"
            :class="['message', msg.role]"
          >
            <div class="message-avatar">
              <el-icon v-if="msg.role === 'user'"><User /></el-icon>
              <el-icon v-else><Reading /></el-icon>
            </div>
            <div class="message-content">
              <div v-if="msg.reasoning" class="reasoning-box">
                <el-text type="info" size="small">思考过程：</el-text>
                <div class="reasoning-content">{{ msg.reasoning }}</div>
              </div>
              <!-- AI 消息使用 markdown 渲染 -->
              <div v-if="msg.role === 'ai'" class="message-markdown" v-html="renderMarkdown(msg.content)"></div>
              <!-- 用户消息纯文本 -->
              <div v-else class="message-text">{{ msg.content }}</div>
              <div v-if="msg.toolCalls && msg.toolCalls.length" class="tool-calls">
                <el-tag
                  v-for="(tool, i) in msg.toolCalls"
                  :key="i"
                  size="small"
                  type="info"
                  effect="plain"
                >
                  <el-icon><Tools /></el-icon> {{ tool.name }}
                </el-tag>
              </div>
            </div>
          </div>

          <!-- 加载中状态 -->
          <div v-if="loading" class="message ai">
            <div class="message-avatar">
              <el-icon><Reading /></el-icon>
            </div>
            <div class="message-content">
              <el-skeleton :rows="2" animated />
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="input-container">
        <div class="input-box">
          <el-input
            v-model="inputMessage"
            type="textarea"
            :rows="2"
            placeholder="输入消息与智能体对话..."
            :disabled="loading || uploading"
            @keydown.enter.exact.prevent="sendMessage"
            resize="none"
          />
          <el-button
            type="primary"
            :disabled="loading || uploading || !inputMessage.trim()"
            @click="sendMessage"
          >
            <el-icon><Promotion /></el-icon> 发送
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { uploadResume, chatStream } from '@/api/services'
import MarkdownIt from 'markdown-it'

// 初始化 markdown-it
const md = new MarkdownIt({
  html: true,
  breaks: true,
  linkify: true,
  typographer: true
})

// 自定义渲染规则 - 添加代码高亮类
md.renderer.rules.fence = (tokens, idx, options, env, self) => {
  const token = tokens[idx]
  const info = token.info ? token.info.trim() : ''
  let str = `<pre><code class="language-${info}" ${info ? `data-language="${info}"` : ''}>`
  str += md.utils.escapeHtml(token.content)
  str += '</code></pre>'
  return str
}

const messages = ref([])
const inputMessage = ref('')
const loading = ref(false)
const uploading = ref(false)
const uploadProgress = ref(0)
const messagesContainer = ref(null)

// 获取会话 ID
const getSessionId = () => window.getSessionId?.() || ''
const updateSessionId = (id) => window.updateSessionId?.(id)

// 生成消息存储键
const getMessagesStorageKey = (sessionId) => `chat_messages_${sessionId}`

// 从 sessionStorage 加载消息
const loadMessages = () => {
  const sessionId = getSessionId()
  if (!sessionId) {
    messages.value = []
    return
  }
  const key = getMessagesStorageKey(sessionId)
  try {
    const stored = sessionStorage.getItem(key)
    if (stored) {
      messages.value = JSON.parse(stored)
    } else {
      messages.value = []
    }
  } catch (e) {
    console.error('加载消息失败:', e)
    messages.value = []
  }
}

// 保存消息到 sessionStorage
const saveMessages = () => {
  const sessionId = getSessionId()
  if (!sessionId) return
  const key = getMessagesStorageKey(sessionId)
  try {
    sessionStorage.setItem(key, JSON.stringify(messages.value))
  } catch (e) {
    console.error('保存消息失败:', e)
  }
}

// 监听会话 ID 变化
watch(() => getSessionId(), () => {
  loadMessages()
})

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// 渲染 markdown
const renderMarkdown = (text) => {
  if (!text) return ''
  return md.render(text)
}

// 模拟上传进度
const simulateUploadProgress = () => {
  let progress = 0
  const interval = setInterval(() => {
    progress += Math.random() * 15
    if (progress > 90) {
      progress = 90
      clearInterval(interval)
    }
    uploadProgress.value = Math.floor(progress)
  }, 500)
  return interval
}

// 处理文件上传
const handleFileUpload = async (file) => {
  uploading.value = true
  uploadProgress.value = 0

  // 开始模拟进度
  const progressInterval = simulateUploadProgress()

  try {
    const response = await uploadResume(file.file, getSessionId())

    // 清除进度模拟
    clearInterval(progressInterval)
    uploadProgress.value = 100

    if (response.success) {
      updateSessionId(response.session_id)
      ElMessage.success('简历上传成功')
      messages.value.push({
        role: 'ai',
        content: '简历已上传成功！我已经分析了您的简历信息。您可以查看"学生画像"了解更多详情，或者告诉我您想了解的职业规划问题。'
      })
      saveMessages()
    }
  } catch (error) {
    clearInterval(progressInterval)
    ElMessage.error('上传失败：' + error.message)
  } finally {
    uploading.value = false
    uploadProgress.value = 0
  }
}

// 文件上传前检查
const beforeFileUpload = (file) => {
  const validTypes = ['txt', 'docx', 'pdf']
  const extension = file.name.split('.').pop().toLowerCase()
  if (!validTypes.includes(extension)) {
    ElMessage.error('不支持的文件格式，请上传 .txt, .docx 或 .pdf 文件')
    return false
  }
  return true
}

// 发送消息
const sendMessage = async () => {
  const message = inputMessage.value.trim()
  if (!message || loading.value || uploading.value) return

  inputMessage.value = ''
  messages.value.push({
    role: 'user',
    content: message
  })
  saveMessages()
  loading.value = true
  scrollToBottom()

  try {
    const stream = await chatStream(message, getSessionId())
    const reader = stream.getReader()
    const decoder = new TextDecoder()

    const aiMessage = {
      role: 'ai',
      content: '',
      reasoning: '',
      toolCalls: []
    }
    messages.value.push(aiMessage)

    let buffer = ''

    while (true) {
      const { value, done } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (!line.trim()) continue
        try {
          const event = JSON.parse(line)
          const lastMsg = messages.value[messages.value.length - 1]

          switch (event.type) {
            case 'reasoning':
              lastMsg.reasoning += event.content
              break
            case 'answer':
            case 'final_answer':
              lastMsg.content += event.content
              break
            case 'tool_call':
              if (!lastMsg.toolCalls) lastMsg.toolCalls = []
              lastMsg.toolCalls.push({ name: event.name, args: event.args })
              break
            case 'tool_result':
              break
            case 'tool_error':
              ElMessage.warning(`工具 ${event.name} 执行失败：${event.error}`)
              break
          }
        } catch (e) {
          console.error('解析流式响应失败:', e)
        }
      }
      saveMessages()
      scrollToBottom()
    }
  } catch (error) {
    ElMessage.error('对话失败：' + error.message)
    messages.value.pop()
    saveMessages()
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

onMounted(() => {
  loadMessages()
  scrollToBottom()
})
</script>

<style scoped>
.chat-view {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: var(--bg-primary);
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.welcome-message {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.welcome-message :deep(.el-empty__description) {
  color: var(--text-secondary);
}

.uploading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.uploading-card {
  width: 100%;
  max-width: 400px;
  background-color: var(--card-bg);
  border-color: var(--border-color);
}

.uploading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 20px;
}

.uploading-icon {
  color: var(--primary-color);
  animation: spin 2s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.uploading-text {
  font-size: 16px;
  font-weight: 500;
  color: var(--text-primary);
}

.uploading-hint {
  margin-top: 8px;
}

.messages {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message {
  display: flex;
  gap: 12px;
  max-width: 85%;
}

.message.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message.ai {
  align-self: flex-start;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.message.user .message-avatar {
  background-color: var(--primary-color);
  color: var(--bg-primary);
}

.message.ai .message-avatar {
  background-color: var(--success-color);
  color: var(--bg-primary);
}

.message-content {
  background-color: var(--card-bg);
  padding: 12px 16px;
  border-radius: 12px;
  color: var(--text-primary);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  max-width: 100%;
  overflow: hidden;
}

.message.user .message-content {
  background-color: var(--bg-secondary);
}

.message-text {
  white-space: pre-wrap;
  line-height: 1.6;
}

.message-markdown {
  line-height: 1.8;
}

.message-markdown :deep(p) {
  margin: 0.5em 0;
}

.message-markdown :deep(p:first-child) {
  margin-top: 0;
}

.message-markdown :deep(p:last-child) {
  margin-bottom: 0;
}

.message-markdown :deep(h1),
.message-markdown :deep(h2),
.message-markdown :deep(h3),
.message-markdown :deep(h4),
.message-markdown :deep(h5),
.message-markdown :deep(h6) {
  margin: 1em 0 0.5em;
  font-weight: 600;
  line-height: 1.4;
  color: var(--primary-color);
}

.message-markdown :deep(h1) {
  font-size: 1.4em;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 0.3em;
}

.message-markdown :deep(h2) {
  font-size: 1.2em;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 0.3em;
}

.message-markdown :deep(h3) {
  font-size: 1.1em;
}

.message-markdown :deep(h4),
.message-markdown :deep(h5),
.message-markdown :deep(h6) {
  font-size: 1em;
}

.message-markdown :deep(ul),
.message-markdown :deep(ol) {
  padding-left: 1.5em;
  margin: 0.5em 0;
}

.message-markdown :deep(li) {
  margin: 0.3em 0;
}

.message-markdown :deep(code) {
  background-color: var(--bg-tertiary);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Fira Code', 'Consolas', monospace;
  font-size: 0.9em;
  color: var(--danger-color);
}

.message-markdown :deep(pre) {
  background-color: var(--bg-tertiary);
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 0.5em 0;
}

.message-markdown :deep(pre code) {
  background: none;
  padding: 0;
  color: var(--text-primary);
}

.message-markdown :deep(blockquote) {
  border-left: 4px solid var(--primary-color);
  padding-left: 1em;
  margin: 0.5em 0;
  color: var(--text-secondary);
}

.message-markdown :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 0.5em 0;
}

.message-markdown :deep(th),
.message-markdown :deep(td) {
  border: 1px solid var(--border-color);
  padding: 8px;
  text-align: left;
}

.message-markdown :deep(th) {
  background-color: var(--bg-tertiary);
  font-weight: 600;
}

.message-markdown :deep(a) {
  color: var(--primary-color);
  text-decoration: none;
}

.message-markdown :deep(a:hover) {
  text-decoration: underline;
}

.reasoning-box {
  background-color: var(--bg-tertiary);
  padding: 8px 12px;
  border-radius: 8px;
  margin-bottom: 8px;
  border-left: 3px solid var(--danger-color);
}

.reasoning-content {
  margin-top: 4px;
  font-size: 13px;
  color: var(--text-secondary);
  white-space: pre-wrap;
}

.tool-calls {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}

.input-container {
  padding: 16px 20px;
  background-color: var(--bg-secondary);
  border-top: 1px solid var(--border-color);
}

.input-box {
  display: flex;
  gap: 12px;
  max-width: 900px;
  margin: 0 auto;
}

.input-box :deep(.el-textarea__inner) {
  background-color: var(--input-bg);
  border-color: var(--input-border);
  color: var(--text-primary);
  resize: none;
}

.input-box :deep(.el-textarea__inner):focus {
  border-color: var(--primary-color);
}
</style>
