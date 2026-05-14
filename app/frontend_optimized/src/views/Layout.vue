<template>
  <el-container class="app-container">
    <!-- 左侧边栏 - 功能面板 -->
    <el-aside :width="sidebarWidth" class="sidebar">
      <div class="sidebar-header">
        <el-icon :size="28" color="#409EFF"><Target /></el-icon>
        <span class="app-title" v-show="!isCollapse">职业规划智能体</span>
        <el-button @click="toggleSidebar" text class="collapse-btn">
          <el-icon><component :is="isCollapse ? 'Expand' : 'Fold'" /></el-icon>
        </el-button>
      </div>

      <!-- 状态指示器 -->
      <div class="status-section">
        <div class="status-item" :class="{ active: appStore.hasResume }">
          <el-icon><Document /></el-icon>
          <span>简历</span>
          <el-icon class="status-icon" :is="appStore.hasResume ? 'Check' : 'Close'" />
        </div>
        <div class="status-item" :class="{ active: appStore.studentProfile }">
          <el-icon><User /></el-icon>
          <span>学生画像</span>
          <el-icon class="status-icon" :is="appStore.studentProfile ? 'Check' : 'Close'" />
        </div>
        <div class="status-item" :class="{ active: appStore.jobProfile }">
          <el-icon><Briefcase /></el-icon>
          <span>岗位分析</span>
          <el-icon class="status-icon" :is="appStore.jobProfile ? 'Check' : 'Close'" />
        </div>
        <div class="status-item" :class="{ active: appStore.matchResult }">
          <el-icon><DataAnalysis /></el-icon>
          <span>匹配结果</span>
          <el-icon class="status-icon" :is="appStore.matchResult ? 'Check' : 'Close'" />
        </div>
      </div>

      <!-- 功能面板 -->
      <el-tabs v-model="activePanel" type="card" class="function-tabs">
        <el-tab-pane label="简历上传" name="resume">
          <el-upload
            ref="uploadRef"
            drag
            :auto-upload="true"
            :show-file-list="false"
            :on-change="handleFileChange"
            :before-upload="beforeUpload"
            accept=".txt,.docx,.pdf"
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              拖拽或<em>点击上传</em>简历
            </div>
            <template #tip>
              <div class="el-upload__tip">.txt / .docx / .pdf</div>
            </template>
          </el-upload>
        </el-tab-pane>

        <el-tab-pane label="学生画像" name="student">
          <div v-if="appStore.studentProfile" class="profile-preview">
            <div class="profile-stat">
              <span class="label">技能</span>
              <span class="value">{{ appStore.studentProfile.skills?.length || 0 }}</span>
            </div>
            <div class="profile-stat">
              <span class="label">经历</span>
              <span class="value">{{ appStore.studentProfile.Experience?.length || 0 }}</span>
            </div>
            <div class="profile-stat">
              <span class="label">证书</span>
              <span class="value">{{ appStore.studentProfile.certificates?.length || 0 }}</span>
            </div>
            <div class="profile-stat">
              <span class="label">素养</span>
              <el-tag :type="getLevelType(appStore.studentProfile.Professionalism?.level)" size="small">
                {{ appStore.studentProfile.Professionalism?.level || '-' }}
              </el-tag>
            </div>
            <el-button type="primary" link @click="showStudentDetail = true" style="width: 100%; margin-top: 8px;">
              查看详情
            </el-button>
          </div>
          <el-empty v-else description="请上传简历" :image-size="80" />
        </el-tab-pane>

        <el-tab-pane label="岗位分析" name="job">
          <el-form :model="jobForm" label-position="top" size="small">
            <el-form-item label="岗位名称">
              <el-input v-model="jobForm.jobName" placeholder="例如：Java 开发工程师" />
            </el-form-item>
            <el-form-item label="岗位描述（可选）">
              <el-input v-model="jobForm.jobDescription" type="textarea" :rows="4" placeholder="粘贴岗位描述..." />
            </el-form-item>
            <el-button
              type="primary"
              :loading="appStore.loading"
              @click="handleAnalyzeJob"
              :disabled="!jobForm.jobName"
              style="width: 100%"
            >
              分析岗位
            </el-button>
          </el-form>
          <div v-if="appStore.jobProfile" class="job-preview">
            <div class="job-name">{{ appStore.jobProfile.name }}</div>
            <el-button type="primary" link @click="showJobDetail = true" style="width: 100%;">
              查看详情
            </el-button>
          </div>
        </el-tab-pane>

        <el-tab-pane label="匹配结果" name="match">
          <div v-if="appStore.matchResult" class="match-preview">
            <div class="match-degree" :class="getDegreeClass(appStore.matchResult.summary?.matching_degree)">
              {{ appStore.matchResult.summary?.matching_degree || '-' }}
            </div>
            <el-button type="primary" link @click="showMatchDetail = true" style="width: 100%;">
              查看详情
            </el-button>
          </div>
          <el-empty v-else description="请先分析岗位" :image-size="80" />
        </el-tab-pane>
      </el-tabs>

      <!-- 底部操作 -->
      <div class="sidebar-footer">
        <el-button @click="clearAll" type="danger" plain size="small" style="width: 100%">
          <el-icon><Delete /></el-icon>
          <span v-show="!isCollapse">清除所有数据</span>
        </el-button>
      </div>
    </el-aside>

    <!-- 主内容区 - 对话界面 -->
    <el-main class="chat-main">
      <div class="chat-wrapper">
        <!-- 消息列表 -->
        <div class="message-list" ref="messageListRef">
          <div v-if="appStore.chatMessages.length === 0" class="welcome-screen">
            <div class="welcome-content">
              <el-icon :size="80" color="#409EFF"><ChatDotRound /></el-icon>
              <h1>你好，我是你的职业规划助手</h1>
              <p>我可以帮你分析简历、匹配岗位、规划职业发展</p>
              <div class="quick-actions">
                <el-button @click="sendQuickQuestion('请分析我的简历，告诉我有哪些优势')">
                  <el-icon><Document /></el-icon>
                  分析我的简历
                </el-button>
                <el-button @click="sendQuickQuestion('我想了解 Java 开发工程师的要求')">
                  <el-icon><Briefcase /></el-icon>
                  了解岗位要求
                </el-button>
                <el-button @click="sendQuickQuestion('根据我的背景，给我一些职业发展建议')">
                  <el-icon><Guide /></el-icon>
                  获取发展建议
                </el-button>
              </div>
            </div>
          </div>

          <div
            v-for="(message, index) in appStore.chatMessages"
            :key="index"
            class="message-wrapper"
            :class="message.role"
          >
            <div class="message-avatar">
              <el-avatar v-if="message.role === 'user'" :size="40">
                <el-icon><User /></el-icon>
              </el-avatar>
              <el-avatar v-else :size="40" class="ai-avatar">
                <el-icon><Cpu /></el-icon>
              </el-avatar>
            </div>

            <div class="message-body">
              <!-- 用户消息 -->
              <div v-if="message.role === 'user'" class="user-message">
                {{ message.content }}
              </div>

              <!-- AI 消息 -->
              <div v-else class="assistant-message">
                <!-- 思考过程（可折叠） -->
                <el-collapse v-if="message.reasoning" class="reasoning-collapse">
                  <el-collapse-item title="思考过程" name="reasoning">
                    <div class="reasoning-content">{{ message.reasoning }}</div>
                  </el-collapse-item>
                </el-collapse>

                <!-- 工具调用 -->
                <div v-if="message.toolCalls?.length" class="tool-calls">
                  <div v-for="(tool, tIndex) in message.toolCalls" :key="tIndex" class="tool-item">
                    <div class="tool-title">
                      <el-icon><Tools /></el-icon>
                      <span>{{ tool.name }}</span>
                    </div>
                    <div v-if="tool.result" class="tool-result">{{ tool.result }}</div>
                  </div>
                </div>

                <!-- 回答内容 -->
                <div v-if="message.content" class="answer-content" v-html="formatContent(message.content)"></div>

                <!-- 流式输出中 -->
                <div v-if="index === appStore.chatMessages.length - 1 && appStore.isChatStreaming" class="streaming-status">
                  <el-tag type="info" size="small" effect="plain">
                    <el-icon class="is-loading"><Loading /></el-icon>
                    正在生成回答...
                  </el-tag>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 输入区域 -->
        <div class="chat-input-wrapper">
          <div class="input-container">
            <el-input
              v-model="inputMessage"
              type="textarea"
              :rows="2"
              placeholder="输入消息... (Enter 发送，Shift+Enter 换行)"
              @keydown="handleKeydown"
              :disabled="appStore.isChatStreaming"
              ref="inputRef"
            />
            <div class="input-toolbar">
              <div class="toolbar-left">
                <el-tooltip content="上传简历">
                  <el-button text @click="triggerUpload">
                    <el-icon><Document /></el-icon>
                  </el-button>
                </el-tooltip>
              </div>
              <div class="toolbar-right">
                <el-button
                  type="primary"
                  @click="sendMessage"
                  :loading="appStore.isChatStreaming"
                  :disabled="!inputMessage.trim()"
                >
                  发送
                  <el-icon><Promotion /></el-icon>
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-main>

    <!-- 详情弹窗 -->
    <!-- 学生画像详情 -->
    <el-dialog v-model="showStudentDetail" title="学生画像详情" width="800px" top="5vh">
      <StudentProfileDetail
        v-if="showStudentDetail"
        :profile="appStore.studentProfile"
      />
    </el-dialog>

    <!-- 岗位画像详情 -->
    <el-dialog v-model="showJobDetail" title="岗位画像详情" width="800px" top="5vh">
      <JobProfileDetail
        v-if="showJobDetail"
        :profile="appStore.jobProfile"
      />
    </el-dialog>

    <!-- 匹配结果详情 -->
    <el-dialog v-model="showMatchDetail" title="人岗匹配结果" width="900px" top="5vh">
      <MatchResultDetail
        v-if="showMatchDetail"
        :result="appStore.matchResult"
      />
    </el-dialog>
  </el-container>
</template>

<script setup>
import { ref, reactive, nextTick, watch, computed, onMounted } from 'vue'
import { useAppStore } from '@/store/app'
import { ElMessage } from 'element-plus'
import StudentProfileDetail from '../components/StudentProfileDetail.vue'
import JobProfileDetail from '../components/JobProfileDetail.vue'
import MatchResultDetail from '../components/MatchResultDetail.vue'

const appStore = useAppStore()
const messageListRef = ref(null)
const inputRef = ref(null)
const uploadRef = ref(null)
const isCollapse = ref(false)
const activePanel = ref('resume')
const showStudentDetail = ref(false)
const showJobDetail = ref(false)
const showMatchDetail = ref(false)

const sidebarWidth = computed(() => isCollapse.value ? '64px' : '360px')

const jobForm = reactive({
  jobName: '',
  jobDescription: ''
})

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messageListRef.value) {
      messageListRef.value.scrollTop = messageListRef.value.scrollHeight
    }
  })
}

watch(() => appStore.chatMessages.length, () => {
  scrollToBottom()
}, { immediate: true })

const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value
}

const handleFileChange = async (file) => {
  try {
    await appStore.uploadResume(file.raw)
    ElMessage.success('简历上传成功！')
  } catch (error) {
    ElMessage.error('上传失败，请重试')
  }
}

const beforeUpload = (file) => {
  const validTypes = ['txt', 'docx', 'pdf']
  const fileExt = file.name.split('.').pop().toLowerCase()
  if (!validTypes.includes(fileExt)) {
    ElMessage.error('仅支持 .txt / .docx / .pdf 格式')
    return false
  }
  const maxSize = 5 * 1024 * 1024
  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过 5MB')
    return false
  }
  return true
}

const triggerUpload = () => {
  uploadRef.value.$el.querySelector('input[type="file"]').click()
}

const handleAnalyzeJob = async () => {
  if (!jobForm.jobName) {
    ElMessage.warning('请输入岗位名称')
    return
  }
  try {
    const result = await appStore.analyzeJob(jobForm.jobName, jobForm.jobDescription)
    if (result.success) {
      ElMessage.success('岗位分析完成！')
      // 自动切换到匹配结果面板
      activePanel.value = 'match'
    } else {
      ElMessage.error(result.error || '分析失败')
    }
  } catch (error) {
    ElMessage.error('分析失败，请重试')
  }
}

const inputMessage = ref('')

const sendMessage = async () => {
  const message = inputMessage.value.trim()
  if (!message || appStore.isChatStreaming) return

  inputMessage.value = ''
  await appStore.sendMessage(message)
}

const handleKeydown = (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

const sendQuickQuestion = (question) => {
  inputMessage.value = question
  sendMessage()
}

const clearAll = async () => {
  await appStore.clearSession()
  ElMessage.success('已清除所有数据')
}

const formatContent = (content) => {
  let formatted = content
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
  formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  formatted = formatted.replace(/\*(.+?)\*/g, '<em>$1</em>')
  formatted = formatted.replace(/^\s*[-*]\s+(.+)$/gm, '<li>$1</li>')
  formatted = formatted.replace(/(<li>.+<\/li>\n?)+/g, '<ul>$&</ul>')
  formatted = formatted.replace(/\n/g, '<br>')
  return formatted
}

const getLevelType = (level) => {
  const types = { '高': 'success', '中': 'warning', '低': 'danger' }
  return types[level] || 'info'
}

const getDegreeClass = (degree) => {
  const classes = { '高': 'high', '中': 'medium', '低': 'low' }
  return classes[degree] || ''
}
</script>

<style scoped lang="scss">
.app-container {
  height: 100vh;
  overflow: hidden;
}

.sidebar {
  background: #fff;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  transition: width 0.3s;

  .sidebar-header {
    height: 60px;
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 0 16px;
    border-bottom: 1px solid #e4e7ed;

    .app-title {
      flex: 1;
      font-size: 18px;
      font-weight: 600;
      color: #303133;
    }

    .collapse-btn {
      color: #909399;
    }
  }

  .status-section {
    padding: 16px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

    .status-item {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px;
      margin-bottom: 8px;
      background: rgba(255,255,255,0.1);
      border-radius: 8px;
      color: rgba(255,255,255,0.8);
      font-size: 13px;

      &:last-child {
        margin-bottom: 0;
      }

      &.active {
        background: rgba(255,255,255,0.2);
        color: #fff;

        .status-icon {
          color: #67C23A;
        }
      }
    }
  }

  .function-tabs {
    flex: 1;
    overflow: hidden;
    display: flex;
    flex-direction: column;

    :deep(.el-tabs__header) {
      margin: 0;
      padding: 0 8px;
    }

    :deep(.el-tabs__content) {
      flex: 1;
      overflow-y: auto;
      padding: 12px;
    }
  }

  .el-upload {
    width: 100%;

    :deep(.el-upload-dragger) {
      padding: 20px 10px;
      cursor: pointer;

      .el-icon--upload {
        font-size: 32px;
        color: #409EFF;
      }

      .el-upload__text {
        font-size: 13px;
        color: #606266;

        em {
          color: #409EFF;
          font-style: normal;
        }
      }

      .el-upload__tip {
        font-size: 12px;
        color: #909399;
      }
    }
  }

  .profile-preview, .job-preview, .match-preview {
    padding: 12px 0;

    .profile-stat, .job-preview, .match-preview {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 0;
      border-bottom: 1px solid #f0f0f0;

      .label {
        font-size: 13px;
        color: #909399;
      }

      .value {
        font-size: 18px;
        font-weight: 600;
        color: #303133;
      }
    }

    .job-name {
      font-size: 14px;
      font-weight: 600;
      color: #303133;
      margin-bottom: 8px;
    }

    .match-degree {
      font-size: 32px;
      font-weight: bold;
      text-align: center;
      padding: 20px;
      border-radius: 8px;
      margin-bottom: 12px;

      &.high {
        background: linear-gradient(135deg, #67C23A 0%, #52c41a 100%);
        color: #fff;
      }

      &.medium {
        background: linear-gradient(135deg, #E6A23C 0%, #e6a23c 100%);
        color: #fff;
      }

      &.low {
        background: linear-gradient(135deg, #F56C6C 0%, #f56c6c 100%);
        color: #fff;
      }
    }
  }

  .sidebar-footer {
    padding: 16px;
    border-top: 1px solid #e4e7ed;
  }
}

.chat-main {
  padding: 0;
  background: #f5f7fa;
  overflow: hidden;

  .chat-wrapper {
    height: 100%;
    display: flex;
    flex-direction: column;
  }

  .message-list {
    flex: 1;
    overflow-y: auto;
    padding: 24px;
    scroll-behavior: smooth;
  }

  .welcome-screen {
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;

    .welcome-content {
      text-align: center;

      h1 {
        margin: 24px 0 12px 0;
        font-size: 28px;
        font-weight: 600;
        color: #303133;
      }

      p {
        margin: 0 0 32px 0;
        font-size: 16px;
        color: #909399;
      }

      .quick-actions {
        display: flex;
        gap: 12px;
        justify-content: center;
        flex-wrap: wrap;

        .el-button {
          height: auto;
          padding: 12px 20px;
          font-size: 14px;

          .el-icon {
            margin-right: 6px;
          }
        }
      }
    }
  }

  .message-wrapper {
    display: flex;
    gap: 16px;
    margin-bottom: 24px;

    &.user {
      flex-direction: row-reverse;

      .message-body {
        max-width: 70%;
      }

      .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #fff;
      }
    }

    &.assistant {
      .message-body {
        max-width: 85%;
      }
    }

    .message-avatar {
      flex-shrink: 0;

      .ai-avatar {
        background: linear-gradient(135deg, #409EFF 0%, #00f2fe 100%);
      }
    }

    .message-body {
      .user-message {
        padding: 14px 18px;
        border-radius: 16px 16px 4px 16px;
        font-size: 15px;
        line-height: 1.6;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
      }

      .assistant-message {
        background: #fff;
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
      }
    }
  }

  .reasoning-collapse {
    margin-bottom: 12px;
    border: 1px solid #f0f0f0;
    border-radius: 8px;

    :deep(.el-collapse-item__header) {
      padding: 10px 12px;
      background: #fff8e1;
      border-radius: 8px;
      font-size: 13px;
      color: #E6A23C;

      .el-collapse-item__arrow {
        color: #E6A23C;
      }
    }

    .reasoning-content {
      font-size: 13px;
      color: #606266;
      line-height: 1.6;
      padding: 12px;
      max-height: 200px;
      overflow-y: auto;
    }
  }

  .tool-calls {
    margin-bottom: 12px;

    .tool-item {
      background: #f0f9eb;
      border: 1px solid #e1f3d8;
      border-radius: 8px;
      padding: 10px;
      margin-bottom: 8px;

      .tool-title {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 13px;
        font-weight: 600;
        color: #67C23A;
        margin-bottom: 6px;
      }

      .tool-result {
        font-size: 12px;
        color: #606266;
        background: #fff;
        padding: 8px;
        border-radius: 4px;
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

  .streaming-status {
    margin-top: 8px;
  }

  .chat-input-wrapper {
    padding: 16px 24px;
    background: #fff;
    border-top: 1px solid #e4e7ed;
  }

  .input-container {
    max-width: 900px;
    margin: 0 auto;
  }

  .input-toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 8px;

    .toolbar-left, .toolbar-right {
      display: flex;
      gap: 8px;
    }
  }
}
</style>
