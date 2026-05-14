<template>
  <div class="home-container">
    <!-- 欢迎卡片 -->
    <el-card class="welcome-card" shadow="hover">
      <div class="welcome-content">
        <div class="welcome-icon">
          <el-icon :size="64" color="#409EFF"><Target /></el-icon>
        </div>
        <div class="welcome-text">
          <h1>欢迎使用职业规划智能体</h1>
          <p>基于 AI 的智能职业规划助手，帮助您分析简历、匹配岗位、规划职业发展路径</p>
        </div>
      </div>
    </el-card>

    <!-- 功能卡片 -->
    <el-row :gutter="20" class="feature-cards">
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="feature-card" shadow="hover" @click="$router.push('/student-profile')">
          <div class="feature-icon blue">
            <el-icon :size="40"><User /></el-icon>
          </div>
          <h3>学生画像</h3>
          <p>上传简历后自动提取您的技能、经历和能力特长</p>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="feature-card" shadow="hover" @click="$router.push('/job-analysis')">
          <div class="feature-icon green">
            <el-icon :size="40"><Briefcase /></el-icon>
          </div>
          <h3>岗位分析</h3>
          <p>分析目标岗位的职责要求和技能需求</p>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="feature-card" shadow="hover" @click="$router.push('/match-result')">
          <div class="feature-icon orange">
            <el-icon :size="40"><DataAnalysis /></el-icon>
          </div>
          <h3>人岗匹配</h3>
          <p>智能分析您与岗位的匹配度和差距</p>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="feature-card" shadow="hover" @click="$router.push('/chat')">
          <div class="feature-icon purple">
            <el-icon :size="40"><ChatDotRound /></el-icon>
          </div>
          <h3>智能对话</h3>
          <p>与 AI 助手交流，获取职业规划建议</p>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快速操作区 -->
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card class="upload-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><Document /></el-icon> 上传简历</span>
            </div>
          </template>

          <div v-if="uploading" class="uploading-overlay">
            <div class="loading-content">
              <el-icon class="is-loading" :size="48"><Loading /></el-icon>
              <p class="loading-text">正在解析简历...</p>
              <p class="loading-subtext">AI 正在分析您的技能和经历，请稍候</p>
            </div>
          </div>

          <div
            class="custom-upload-area"
            :class="{ 'is-uploading': uploading }"
            @click="triggerFileInput"
            @dragover.prevent="handleDragOver"
            @dragleave.prevent="handleDragLeave"
            @drop.prevent="handleDrop"
          >
            <input
              ref="fileInputRef"
              type="file"
              accept=".txt,.docx,.pdf"
              style="display: none"
              @change="handleFileSelect"
            />
            <el-icon class="el-icon--upload" :size="50"><UploadFilled /></el-icon>
            <div class="upload-text">
              拖拽文件到此处或<em>点击上传</em>
            </div>
            <div class="upload-tip">
              支持 .txt / .docx / .pdf 格式，文件大小不超过 5MB
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="status-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><CircleCheck /></el-icon> 当前状态</span>
            </div>
          </template>

          <div class="status-list">
            <div class="status-item">
              <span class="status-label">简历</span>
              <el-tag :type="appStore.hasResume ? 'success' : 'info'" size="large">
                <el-icon :is="appStore.hasResume ? 'Check' : 'Close'" />
                {{ appStore.hasResume ? '已上传' : '未上传' }}
              </el-tag>
            </div>

            <div class="status-item">
              <span class="status-label">学生画像</span>
              <el-tag :type="appStore.studentProfile ? 'success' : 'info'" size="large">
                <el-icon :is="appStore.studentProfile ? 'Check' : 'Close'" />
                {{ appStore.studentProfile ? '已生成' : '未生成' }}
              </el-tag>
            </div>

            <div class="status-item">
              <span class="status-label">岗位画像</span>
              <el-tag :type="appStore.jobProfile ? 'success' : 'info'" size="large">
                <el-icon :is="appStore.jobProfile ? 'Check' : 'Close'" />
                {{ appStore.jobProfile ? '已分析' : '未分析' }}
              </el-tag>
            </div>

            <div class="status-item">
              <span class="status-label">匹配结果</span>
              <el-tag :type="appStore.matchResult ? 'success' : 'info'" size="large">
                <el-icon :is="appStore.matchResult ? 'Check' : 'Close'" />
                {{ appStore.matchResult ? '已完成' : '未完成' }}
              </el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 数据概览 -->
    <el-row :gutter="20" v-if="appStore.studentProfile || appStore.jobProfile">
      <el-col :span="12" v-if="appStore.studentProfile">
        <el-card class="overview-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><User /></el-icon> 学生画像概览</span>
              <el-button type="primary" link @click="$router.push('/student-profile')">
                查看详情 <el-icon><ArrowRight /></el-icon>
              </el-button>
            </div>
          </template>

          <div class="overview-content">
            <div class="stat-item">
              <div class="stat-value">{{ appStore.studentProfile.skills?.length || 0 }}</div>
              <div class="stat-label">技能数量</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ appStore.studentProfile.Experience?.length || 0 }}</div>
              <div class="stat-label">经历数量</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ appStore.studentProfile.certificates?.length || 0 }}</div>
              <div class="stat-label">证书数量</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">
                <el-tag :type="getLevelType(appStore.studentProfile.Professionalism?.level)">
                  {{ appStore.studentProfile.Professionalism?.level || '未知' }}
                </el-tag>
              </div>
              <div class="stat-label">职业素养</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="12" v-if="appStore.jobProfile">
        <el-card class="overview-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><Briefcase /></el-icon> 岗位画像概览</span>
              <el-button type="primary" link @click="$router.push('/job-analysis')">
                查看详情 <el-icon><ArrowRight /></el-icon>
              </el-button>
            </div>
          </template>

          <div class="overview-content">
            <div class="stat-item">
              <div class="stat-value">{{ appStore.jobProfile.name || '未知岗位' }}</div>
              <div class="stat-label">岗位名称</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ appStore.jobProfile.skills?.length || 0 }}</div>
              <div class="stat-label">技能要求</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ appStore.jobProfile.thresholds?.length || 0 }}</div>
              <div class="stat-label">门槛要求</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ appStore.jobProfile.paths?.length || 0 }}</div>
              <div class="stat-label">发展路径</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { useAppStore } from '@/store/app'
import { ElMessage } from 'element-plus'
import {
  Loading,
  Target,
  User,
  Briefcase,
  DataAnalysis,
  ChatDotRound,
  Document,
  CircleCheck,
  ArrowRight,
  UploadFilled
} from '@element-plus/icons-vue'

// 导入日志工具（会自动拦截 console.log）
import '@/utils/logger'

const appStore = useAppStore()
const fileInputRef = ref(null)
const uploading = ref(false)
const isDragOver = ref(false)

console.log('[Home.vue] Component initialized')

// 触发文件输入框
const triggerFileInput = () => {
  console.log('[Home.vue] triggerFileInput called')
  if (!uploading.value && fileInputRef.value) {
    fileInputRef.value.click()
  }
}

// 处理文件选择
const handleFileSelect = (event) => {
  console.log('[Home.vue] handleFileSelect called')
  const files = event.target.files
  if (files && files.length > 0) {
    const file = files[0]
    console.log('[Home.vue] Selected file:', file.name, 'size:', file.size)
    uploadFile(file)
  }
  // 清空 input 以允许重复选择同一文件
  event.target.value = ''
}

// 处理拖拽悬停
const handleDragOver = (event: DragEvent) => {
  event.preventDefault()
  isDragOver.value = true
}

// 处理拖拽离开
const handleDragLeave = () => {
  isDragOver.value = false
}

// 处理拖拽放置
const handleDrop = (event: DragEvent) => {
  event.preventDefault()
  console.log('[Home.vue] handleDrop called')
  isDragOver.value = false

  if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
    const file = event.dataTransfer.files[0]
    console.log('[Home.vue] Dropped file:', file.name, 'size:', file.size)
    uploadFile(file)
  }
}

// 验证文件
const validateFile = (file) => {
  console.log('[Home.vue] validateFile called, file:', file.name, 'size:', file.size)
  const validTypes = ['txt', 'docx', 'pdf']
  const fileExt = file.name.split('.').pop().toLowerCase()

  if (!validTypes.includes(fileExt)) {
    console.log('[Home.vue] validateFile: invalid file type')
    ElMessage.error('仅支持 .txt / .docx / .pdf 格式')
    return false
  }

  const maxSize = 5 * 1024 * 1024
  if (file.size > maxSize) {
    console.log('[Home.vue] validateFile: file too large')
    ElMessage.error('文件大小不能超过 5MB')
    return false
  }

  console.log('[Home.vue] validateFile: file validated successfully')
  return true
}

// 上传文件
const uploadFile = async (file) => {
  console.log('[Home.vue] uploadFile called')

  // 防止重复上传
  if (uploading.value) {
    console.log('[Home.vue] Already uploading, ignoring duplicate request')
    return
  }

  // 先验证文件
  if (!validateFile(file)) {
    return
  }

  console.log('[Home.vue] Setting uploading to true')
  uploading.value = true

  // Wait for next tick to ensure DOM updates
  await nextTick()
  await new Promise(resolve => setTimeout(resolve, 50))
  console.log('[Home.vue] uploading.value after update:', uploading.value)

  // 检查 overlay 是否存在
  const overlay = document.querySelector('.uploading-overlay')
  console.log('[Home.vue] Overlay element:', overlay)
  if (overlay) {
    console.log('[Home.vue] Overlay computed display:', getComputedStyle(overlay).display)
  }

  try {
    console.log('[Home.vue] Calling appStore.uploadResume...')
    const result = await appStore.uploadResume(file)
    console.log('[Home.vue] Upload successful:', result)
    ElMessage.success('简历上传成功！正在生成画像...')
    // 跳转到学生画像页面
    setTimeout(() => {
      window.location.href = '/student-profile'
    }, 1500)
  } catch (error) {
    console.error('[Home.vue] Upload error:', error)
    ElMessage.error('上传失败，请重试')
  } finally {
    // 确保动画至少显示 500ms，让用户能看到
    await new Promise(resolve => setTimeout(resolve, 500))
    console.log('[Home.vue] Setting uploading to false')
    uploading.value = false
  }
}

const getLevelType = (level) => {
  const types = { '高': 'success', '中': 'warning', '低': 'danger' }
  return types[level] || 'info'
}
</script>

<style scoped lang="scss">
.home-container {
  max-width: 1400px;
  margin: 0 auto;
}

.welcome-card {
  margin-bottom: 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;

  .welcome-content {
    display: flex;
    align-items: center;
    gap: 24px;
    padding: 20px;

    .welcome-icon {
      color: #fff;
    }

    .welcome-text {
      color: #fff;

      h1 {
        margin: 0 0 8px 0;
        font-size: 28px;
        font-weight: 600;
      }

      p {
        margin: 0;
        opacity: 0.9;
        font-size: 16px;
      }
    }
  }
}

.feature-cards {
  margin-bottom: 24px;

  .feature-card {
    text-align: center;
    cursor: pointer;
    transition: transform 0.3s;
    height: 200px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;

    &:hover {
      transform: translateY(-5px);
    }

    .feature-icon {
      width: 80px;
      height: 80px;
      border-radius: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 16px;

      &.blue {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #fff;
      }

      &.green {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: #fff;
      }

      &.orange {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: #fff;
      }

      &.purple {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: #fff;
      }
    }

    h3 {
      margin: 0 0 8px 0;
      font-size: 18px;
      color: #303133;
    }

    p {
      margin: 0;
      color: #909399;
      font-size: 14px;
      line-height: 1.6;
    }
  }
}

.upload-card, .status-card {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.el-upload {
  width: 100%;
}

// 自定义上传区域
.custom-upload-area {
  padding: 40px 20px;
  border: 2px dashed #dcdfe6;
  border-radius: 12px;
  background-color: #fafafa;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.3s;

  &:hover {
    border-color: #409EFF;
  }

  &.is-dragover {
    border-color: #409EFF;
    background-color: #ecf5ff;
  }

  &.is-uploading {
    pointer-events: none;
  }

  .el-icon--upload {
    color: #8c939d;
    margin-bottom: 16px;
  }

  .upload-text {
    color: #606266;
    font-size: 14px;
    margin-bottom: 8px;

    em {
      color: #409EFF;
      font-style: normal;
    }
  }

  .upload-tip {
    color: #909399;
    font-size: 12px;
  }
}

.upload-card {
  position: relative;
  z-index: 1;

  .uploading-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(255, 255, 255, 0.95);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 9999 !important;
    border-radius: 12px;
    pointer-events: none;

    .loading-content {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 16px;
      pointer-events: auto;

      .loading-text {
        font-size: 18px;
        font-weight: 600;
        color: #303133;
        margin: 0;
      }

      .loading-subtext {
        font-size: 14px;
        color: #909399;
        margin: 0;
      }
    }
  }
}

.status-list {
  .status-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 0;
    border-bottom: 1px solid #f0f0f0;

    &:last-child {
      border-bottom: none;
    }

    .status-label {
      color: #606266;
      font-size: 14px;
    }
  }
}

.overview-card {
  margin-bottom: 24px;

  .overview-content {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;

    .stat-item {
      text-align: center;
      padding: 16px;
      background: #f5f7fa;
      border-radius: 8px;

      .stat-value {
        font-size: 24px;
        font-weight: 600;
        color: #303133;
        margin-bottom: 8px;
      }

      .stat-label {
        font-size: 12px;
        color: #909399;
      }
    }
  }
}
</style>
