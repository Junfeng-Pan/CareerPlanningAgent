<template>
  <div class="chat-container">
    <el-card class="chat-card" shadow="never">
      <!-- 聊天头部 -->
      <div class="chat-header">
        <div class="chat-title">
          <el-icon><ChatDotRound /></el-icon>
          <span>智能对话助手</span>
        </div>
        <div class="chat-actions">
          <el-button @click="clearChat" size="small">
            <el-icon><Delete /></el-icon>
            清除对话
          </el-button>
        </div>
      </div>

      <!-- 消息列表 -->
      <div class="message-list" ref="messageListRef">
        <div v-if="appStore.chatMessages.length === 0" class="empty-chat">
          <el-empty :image-size="150" description="向我提问吧，我会尽力帮助您">
            <el-button type="primary" @click="sendQuickQuestion('我想了解 Java 开发工程师的要求')">
              了解岗位要求
            </el-button>
            <el-button @click="sendQuickQuestion('根据我的背景，我适合什么岗位？')">
              获取职业建议
            </el-button>
          </el-empty>
        </div>

        <div
          v-for="(message, index) in appStore.chatMessages"
          :key="index"
          class="message-wrapper"
          :class="message.role"
        >
          <div class="message-avatar">
            <el-icon v-if="message.role === 'user'" :size="24"><User /></el-icon>
            <el-icon v-else :size="24"><Cpu /></el-icon>
          </div>

          <div class="message-content">
            <!-- 用户消息 -->
            <div v-if="message.role === 'user'" class="user-message">
              {{ message.content }}
            </div>

            <!-- AI 消息 -->
            <div v-else class="assistant-message">
              <!-- 思考过程 -->
              <div v-if="message.reasoning" class="reasoning-block">
                <div class="reasoning-header">
                  <el-icon><Lightbulb /></el-icon>
                  <span>思考过程</span>
                </div>
                <div class="reasoning-content">{{ message.reasoning }}</div>
              </div>

              <!-- 工具调用 -->
              <div v-if="message.toolCalls?.length" class="tool-calls-block">
                <div
                  v-for="(tool, tIndex) in message.toolCalls"
                  :key="tIndex"
                  class="tool-call-item"
                >
                  <div class="tool-header">
                    <el-icon><Tools /></el-icon>
                    <span>调用工具：{{ tool.name }}</span>
                  </div>
                  <div v-if="tool.args" class="tool-args">
                    <span class="label">参数:</span>
                    <code>{{ JSON.stringify(tool.args, null, 2) }}</code>
                  </div>
                  <div v-if="tool.result" class="tool-result">
                    <span class="label">结果:</span>
                    <div class="result-content">{{ tool.result }}</div>
                  </div>
                </div>
              </div>

              <!-- 回答内容 -->
              <div v-if="message.content" class="answer-content" v-html="formatContent(message.content)"></div>

              <!-- 加载中状态 -->
              <div v-if="index === appStore.chatMessages.length - 1 && appStore.isChatStreaming" class="loading-indicator">
                <el-tag type="info" size="small">
                  <el-icon class="is-loading"><Loading /></el-icon>
                  正在思考...
                </el-tag>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="chat-input-area">
        <el-input
          v-model="inputMessage"
          type="textarea"
          :rows="3"
          placeholder="请输入您的问题，例如：'我想了解 Java 开发工程师的要求'..."
          @keydown.enter.exact.prevent="sendMessage"
          :disabled="appStore.isChatStreaming"
        />
        <div class="input-actions">
          <el-button
            type="primary"
            size="large"
            @click="sendMessage"
            :loading="appStore.isChatStreaming"
            :disabled="!inputMessage.trim()"
          >
            <el-icon><Promotion /></el-icon>
            发送
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, nextTick, watch } from 'vue'
import { useAppStore } from '@/store/app'
import { ElMessage } from 'element-plus'

const appStore = useAppStore()
const messageListRef = ref(null)
const inputMessage = ref('')

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messageListRef.value) {
      messageListRef.value.scrollTop = messageListRef.value.scrollHeight
    }
  })
}

// 监听消息变化
watch(() => appStore.chatMessages.length, () => {
  scrollToBottom()
}, { immediate: true })

// 发送消息
const sendMessage = async () => {
  const message = inputMessage.value.trim()
  if (!message || appStore.isChatStreaming) return

  inputMessage.value = ''
  await appStore.sendMessage(message)
}

// 快速提问
const sendQuickQuestion = (question) => {
  inputMessage.value = question
  sendMessage()
}

// 清除对话
const clearChat = () => {
  appStore.clearChat()
}

// 格式化内容（简单的 markdown 风格）
const formatContent = (content) => {
  // 转义 HTML
  let formatted = content
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')

  // 粗体
  formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  // 斜体
  formatted = formatted.replace(/\*(.+?)\*/g, '<em>$1</em>')
  // 列表
  formatted = formatted.replace(/^\s*[-*]\s+(.+)$/gm, '<li>$1</li>')
  formatted = formatted.replace(/(<li>.+<\/li>\n?)+/g, '<ul>$&</ul>')
  // 换行
  formatted = formatted.replace(/\n/g, '<br>')

  return formatted
}
</script>

<style scoped lang="scss">
.chat-container {
  max-width: 1000px;
  margin: 0 auto;
  height: calc(100vh - 140px);
}

.chat-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  border-radius: 12px;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;

  .chat-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 18px;
    font-weight: 600;
    color: #303133;
  }
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  scroll-behavior: smooth;
}

.empty-chat {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.message-wrapper {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;

  &.user {
    flex-direction: row-reverse;

    .message-content {
      max-width: 70%;
    }

    .user-message {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: #fff;
    }
  }

  &.assistant {
    .message-content {
      max-width: 85%;
    }
  }

  .message-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: #f5f7fa;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    color: #409EFF;
  }

  .message-content {
    .user-message {
      padding: 14px 18px;
      border-radius: 16px 16px 4px 16px;
      font-size: 15px;
      line-height: 1.6;
      box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }

    .assistant-message {
      background: #f8f9fa;
      padding: 16px;
      border-radius: 16px 16px 16px 4px;
    }
  }
}

.reasoning-block {
  background: #fff8e1;
  border-left: 4px solid #E6A23C;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 12px;

  .reasoning-header {
    display: flex;
    align-items: center;
    gap: 6px;
    font-weight: 600;
    color: #E6A23C;
    margin-bottom: 8px;
    font-size: 13px;
  }

  .reasoning-content {
    font-size: 13px;
    color: #606266;
    line-height: 1.6;
    max-height: 150px;
    overflow-y: auto;
  }
}

.tool-calls-block {
  margin-bottom: 12px;

  .tool-call-item {
    background: #f0f9eb;
    border: 1px solid #e1f3d8;
    border-radius: 8px;
    padding: 12px;
    margin-bottom: 8px;

    .tool-header {
      display: flex;
      align-items: center;
      gap: 6px;
      font-weight: 600;
      color: #67C23A;
      margin-bottom: 8px;
      font-size: 13px;
    }

    .tool-args {
      font-size: 12px;
      margin-bottom: 8px;

      .label {
        color: #909399;
        margin-right: 4px;
      }

      code {
        background: #fff;
        padding: 4px 8px;
        border-radius: 4px;
        font-family: 'Courier New', monospace;
        font-size: 11px;
        display: block;
        margin-top: 4px;
        white-space: pre-wrap;
        word-break: break-all;
      }
    }

    .tool-result {
      font-size: 12px;

      .label {
        color: #909399;
        margin-right: 4px;
      }

      .result-content {
        background: #fff;
        padding: 8px;
        border-radius: 4px;
        margin-top: 4px;
        max-height: 100px;
        overflow-y: auto;
        color: #606266;
      }
    }
  }
}

.answer-content {
  font-size: 14px;
  line-height: 1.8;
  color: #303133;

  :deep(ul) {
    padding-left: 20px;
    margin: 8px 0;
  }

  :deep(li) {
    margin: 4px 0;
  }

  :deep(strong) {
    color: #303133;
  }
}

.loading-indicator {
  margin-top: 8px;
}

.chat-input-area {
  padding: 16px 20px;
  border-top: 1px solid #e4e7ed;
  background: #fff;
  border-radius: 0 0 12px 12px;

  .el-textarea {
    margin-bottom: 12px;
  }

  .input-actions {
    display: flex;
    justify-content: flex-end;
  }
}
</style>
