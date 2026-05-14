<template>
  <div class="job-profile-view">
    <div class="page-header">
      <h2>岗位画像</h2>
      <div class="header-actions">
        <el-button type="primary" @click="showAnalyzeDialog = true">
          <el-icon><Edit /></el-icon> 分析岗位
        </el-button>
        <el-button type="success" @click="loadProfile" :loading="loading">
          <el-icon><Refresh /></el-icon> 刷新
        </el-button>
      </div>
    </div>

    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>

    <div v-else-if="error" class="error-container">
      <el-result icon="error" title="加载失败" :sub-title="error">
        <template #extra>
          <el-button type="primary" @click="loadProfile">重新加载</el-button>
        </template>
      </el-result>
    </div>

    <div v-else-if="!profile" class="empty-container">
      <el-result icon="info" title="暂无数据" :sub-title="'请点击「分析岗位」按钮，输入岗位名称和描述进行分析'">
        <template #extra>
          <el-button type="primary" @click="showAnalyzeDialog = true">分析岗位</el-button>
        </template>
      </el-result>
    </div>

    <div v-else class="profile-content">
      <!-- 岗位基本信息 -->
      <el-card class="info-card">
        <template #header>
          <div class="card-header">
            <el-icon><Briefcase /></el-icon>
            <span>{{ profile.name }}</span>
          </div>
        </template>
        <div class="summary">
          <h4>岗位综述</h4>
          <p>{{ profile.summary || '暂无综述信息' }}</p>
        </div>
      </el-card>

      <!-- 技能要求 -->
      <el-card class="skills-card">
        <template #header>
          <div class="card-header">
            <el-icon><Setting /></el-icon>
            <span>专业技能要求</span>
          </div>
        </template>
        <el-empty v-if="!profile.skills?.length" description="暂无技能要求" />
        <div v-else class="skills-grid">
          <el-card
            v-for="(skill, index) in profile.skills"
            :key="index"
            class="skill-item"
            shadow="hover"
          >
            <div class="skill-name">
              <el-tag type="primary" size="large">{{ skill.name }}</el-tag>
            </div>
            <div class="skill-evidence">
              <el-text type="info" size="small">{{ skill.evidence || '无详细描述' }}</el-text>
            </div>
          </el-card>
        </div>
      </el-card>

      <!-- 基础门槛 -->
      <el-card class="thresholds-card">
        <template #header>
          <div class="card-header">
            <el-icon><Document /></el-icon>
            <span>基础门槛要求</span>
          </div>
        </template>
        <el-empty v-if="!profile.thresholds?.length" description="暂无门槛要求" />
        <div v-else class="thresholds-list">
          <div
            v-for="(item, index) in profile.thresholds"
            :key="index"
            class="threshold-item"
          >
            <div class="threshold-icon">
              <el-icon :size="24"><CircleCheckFilled /></el-icon>
            </div>
            <div class="threshold-content">
              <h4>{{ item.name }}</h4>
              <p>{{ item.evidence || '无详细描述' }}</p>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 职业素养 -->
      <el-card class="professionalism-card">
        <template #header>
          <div class="card-header">
            <el-icon><Star /></el-icon>
            <span>职业素养要求</span>
          </div>
        </template>
        <el-empty v-if="!profile.professionalism?.length" description="暂无素养要求" />
        <div v-else class="professionalism-grid">
          <el-card
            v-for="(item, index) in profile.professionalism"
            :key="index"
            class="prof-item"
            shadow="hover"
          >
            <div class="prof-icon">
              <el-icon :size="20"><UserFilled /></el-icon>
            </div>
            <div class="prof-content">
              <h4>{{ item.name }}</h4>
              <p>{{ item.evidence || '无详细描述' }}</p>
            </div>
          </el-card>
        </div>
      </el-card>

      <!-- 发展路径 -->
      <el-card class="paths-card">
        <template #header>
          <div class="card-header">
            <el-icon><TrendCharts /></el-icon>
            <span>职业发展路径</span>
          </div>
        </template>
        <el-empty v-if="!profile.paths?.length" description="暂无发展路径" />
        <div v-else class="paths-list">
          <div
            v-for="(path, index) in profile.paths"
            :key="index"
            class="path-item"
          >
            <div class="path-header">
              <el-tag type="success" size="large">路径 {{ index + 1 }}</el-tag>
            </div>
            <div class="path-steps">
              <el-steps direction="vertical" :active="10" align-center>
                <el-step
                  v-for="(step, stepIndex) in parsePathSteps(path.path)"
                  :key="stepIndex"
                  :title="step"
                  :icon="getStepIcon(stepIndex)"
                >
                  <template #description>
                    <el-text v-if="stepIndex === parsePathSteps(path.path).length - 1" type="info">
                      {{ path.requisitions || '无详细要求' }}
                    </el-text>
                  </template>
                </el-step>
              </el-steps>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 分析岗位对话框 -->
    <el-dialog
      v-model="showAnalyzeDialog"
      title="分析岗位"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form :model="analyzeForm" label-width="80px" label-position="top">
        <el-form-item label="岗位名称" required>
          <el-input
            v-model="analyzeForm.jobName"
            placeholder="例如：Java 开发工程师"
          />
        </el-form-item>
        <el-form-item label="岗位描述" label-width="80px">
          <el-input
            v-model="analyzeForm.jobDescription"
            type="textarea"
            :rows="8"
            placeholder="粘贴岗位描述（JD）内容，可选"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAnalyzeDialog = false">取消</el-button>
        <el-button type="primary" @click="handleAnalyze" :loading="analyzing">
          开始分析
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getJobProfile, analyzeJob } from '@/api/services'

const loading = ref(false)
const error = ref('')
const profile = ref(null)
const showAnalyzeDialog = ref(false)
const analyzing = ref(false)

const analyzeForm = ref({
  jobName: '',
  jobDescription: ''
})

const getSessionId = () => window.getSessionId?.() || ''

// 加载岗位画像
const loadProfile = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await getJobProfile(getSessionId())
    profile.value = response.job_profile
  } catch (e) {
    error.value = e.message || '加载失败'
  } finally {
    loading.value = false
  }
}

// 解析路径步骤
const parsePathSteps = (pathStr) => {
  if (!pathStr) return []
  return pathStr.split('-').map(s => s.trim()).filter(s => s)
}

// 获取步骤图标
const getStepIcon = (index) => {
  const icons = ['User', 'UserFilled', 'Star', 'Trophy', 'Medal']
  return icons[index % icons.length]
}

// 处理分析
const handleAnalyze = async () => {
  if (!analyzeForm.jobName.trim()) {
    ElMessage.warning('请输入岗位名称')
    return
  }

  analyzing.value = true
  try {
    const response = await analyzeJob(
      analyzeForm.jobName,
      analyzeForm.jobDescription,
      getSessionId()
    )

    if (response.success) {
      profile.value = response.job_profile
      ElMessage.success('岗位分析完成')
      showAnalyzeDialog.value = false
      analyzeForm.value = {
        jobName: '',
        jobDescription: ''
      }
    } else {
      ElMessage.error(response.error || '分析失败')
    }
  } catch (e) {
    ElMessage.error('分析失败：' + e.message)
  } finally {
    analyzing.value = false
  }
}

onMounted(() => {
  loadProfile()
})
</script>

<style scoped>
.job-profile-view {
  padding: 24px;
  height: 100%;
  overflow-y: auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h2 {
  color: var(--text-primary);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.loading-container,
.error-container,
.empty-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.profile-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-primary);
  font-weight: 500;
}

.summary {
  padding: 8px 0;
}

.summary h4 {
  color: var(--primary-color);
  margin: 0 0 12px 0;
}

.summary p {
  color: var(--text-primary);
  line-height: 1.8;
  margin: 0;
}

.skills-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.skill-item {
  background-color: var(--bg-tertiary);
}

.skill-name {
  margin-bottom: 12px;
}

.skill-evidence {
  color: var(--text-secondary);
  line-height: 1.6;
}

.thresholds-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.threshold-item {
  display: flex;
  gap: 16px;
  padding: 16px;
  background-color: var(--bg-tertiary);
  border-radius: 8px;
}

.threshold-icon {
  color: var(--success-color);
  flex-shrink: 0;
}

.threshold-content h4 {
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.threshold-content p {
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0;
}

.professionalism-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.prof-item {
  display: flex;
  gap: 12px;
  background-color: var(--bg-tertiary);
}

.prof-icon {
  color: var(--warning-color);
  flex-shrink: 0;
}

.prof-content h4 {
  color: var(--text-primary);
  margin: 0 0 8px 0;
  font-size: 14px;
}

.prof-content p {
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0;
  font-size: 13px;
}

.paths-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.path-item {
  padding: 16px;
  background-color: var(--bg-tertiary);
  border-radius: 8px;
}

.path-header {
  margin-bottom: 16px;
}
</style>
