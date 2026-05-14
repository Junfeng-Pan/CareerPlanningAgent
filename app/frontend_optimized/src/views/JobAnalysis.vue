<template>
  <div class="job-analysis-container">
    <el-row :gutter="20">
      <!-- 左侧：岗位信息输入 -->
      <el-col :span="12">
        <el-card class="input-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><Edit /></el-icon> 岗位信息</span>
            </div>
          </template>

          <el-form :model="jobForm" label-position="top">
            <el-form-item label="岗位名称" required>
              <el-input
                v-model="jobForm.jobName"
                placeholder="例如：Java 开发工程师、前端工程师、产品经理"
                clearable
              >
                <template #prefix>
                  <el-icon><Briefcase /></el-icon>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item label="岗位描述（可选）" required>
              <el-input
                v-model="jobForm.jobDescription"
                type="textarea"
                :rows="10"
                placeholder="请粘贴岗位职责和要求描述..."
              />
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                size="large"
                :loading="appStore.loading"
                @click="handleAnalyze"
                :disabled="!jobForm.jobName"
                style="width: 100%"
              >
                <el-icon><Search /></el-icon>
                开始分析
              </el-button>
            </el-form-item>
          </el-form>

          <!-- 常用岗位快捷选择 -->
          <div class="quick-jobs">
            <div class="quick-title">常用岗位：</div>
            <el-space wrap>
              <el-tag
                v-for="job in commonJobs"
                :key="job"
                closable
                @click="jobForm.jobName = job"
                style="cursor: pointer"
              >
                {{ job }}
              </el-tag>
            </el-space>
          </div>
        </el-card>

        <!-- 发展路径 -->
        <el-card class="path-card" shadow="hover" v-if="appStore.jobProfile?.paths?.length">
          <template #header>
            <div class="card-header">
              <span><el-icon><Guide /></el-icon> 职业发展路径</span>
            </div>
          </template>

          <el-timeline>
            <el-timeline-item
              v-for="(path, index) in appStore.jobProfile.paths"
              :key="index"
              :timestamp="`路径 ${index + 1}`"
              placement="top"
              :color="getTimelineColor(index)"
            >
              <el-card shadow="hover">
                <div class="path-title">{{ path.path }}</div>
                <div class="path-requirements">{{ path.requisitions }}</div>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>

      <!-- 右侧：岗位画像展示 -->
      <el-col :span="12">
        <el-card class="profile-card" shadow="hover" v-if="appStore.jobProfile">
          <template #header>
            <div class="card-header">
              <span><el-icon><Document /></el-icon> 岗位画像</span>
              <el-tag type="success">{{ appStore.jobProfile.name }}</el-tag>
            </div>
          </template>

          <!-- 岗位综述 -->
          <div class="summary-section">
            <h4>岗位综述</h4>
            <p>{{ appStore.jobProfile.summary || '暂无综述' }}</p>
          </div>

          <!-- 技能要求 -->
          <div class="section">
            <h4><el-icon><FolderOpened /></el-icon> 专业技能要求</h4>
            <el-tag
              v-for="(skill, index) in appStore.jobProfile.skills"
              :key="index"
              type="primary"
              effect="plain"
              style="margin: 4px"
            >
              {{ skill.name }}
            </el-tag>
          </div>

          <!-- 门槛要求 -->
          <div class="section">
            <h4><el-icon><Document /></el-icon> 基础门槛要求</h4>
            <el-tag
              v-for="(threshold, index) in appStore.jobProfile.thresholds"
              :key="index"
              type="warning"
              effect="plain"
              style="margin: 4px"
            >
              {{ threshold.name }}
            </el-tag>
          </div>

          <!-- 职业素养 -->
          <div class="section">
            <h4><el-icon><Star /></el-icon> 职业素养要求</h4>
            <el-tag
              v-for="(prof, index) in appStore.jobProfile.professionalism"
              :key="index"
              type="success"
              effect="plain"
              style="margin: 4px"
            >
              {{ prof.name }}
            </el-tag>
          </div>
        </el-card>

        <!-- 技能要求图表 -->
        <el-card class="chart-card" shadow="hover" v-if="appStore.jobProfile?.skills?.length">
          <template #header>
            <div class="card-header">
              <span><el-icon><DataAnalysis /></el-icon> 技能要求分布</span>
            </div>
          </template>

          <div ref="skillsChartRef" class="echarts-chart"></div>
        </el-card>

        <!-- 空状态 -->
        <el-empty
          v-if="!appStore.jobProfile"
          description="请输入岗位信息并点击分析"
          :image-size="150"
        />
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, watch, nextTick, onMounted } from 'vue'
import { useAppStore } from '@/store/app'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const appStore = useAppStore()
const skillsChartRef = ref(null)
let skillsChart = null

const commonJobs = [
  'Java 开发工程师',
  '前端开发工程师',
  'Python 开发工程师',
  '产品经理',
  '数据分析师',
  '测试工程师',
  '运维工程师',
  'UI 设计师'
]

const jobForm = reactive({
  jobName: '',
  jobDescription: ''
})

// 分析岗位
const handleAnalyze = async () => {
  if (!jobForm.jobName) {
    ElMessage.warning('请输入岗位名称')
    return
  }

  try {
    const result = await appStore.analyzeJob(jobForm.jobName, jobForm.jobDescription)
    if (result.success) {
      ElMessage.success('岗位分析完成！')
    } else {
      ElMessage.error(result.error || '分析失败')
    }
  } catch (error) {
    ElMessage.error('分析失败，请重试')
  }
}

// 初始化技能图表
const initSkillsChart = () => {
  if (!skillsChartRef.value || !appStore.jobProfile?.skills?.length) return

  skillsChart = echarts.init(skillsChartRef.value)

  const skills = appStore.jobProfile.skills.slice(0, 10)
  const skillNames = skills.map(s => s.name)

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: skillNames,
      axisLabel: {
        interval: 0,
        rotate: 30,
        fontSize: 11
      }
    },
    yAxis: {
      type: 'value',
      name: '重要程度'
    },
    series: [{
      data: new Array(skills.length).fill(85),
      type: 'bar',
      barWidth: '50%',
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#83bff6' },
          { offset: 0.5, color: '#188df0' },
          { offset: 1, color: '#188df0' }
        ])
      },
      emphasis: {
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#2378f7' },
            { offset: 0.7, color: '#2378f7' },
            { offset: 1, color: '#83bff6' }
          ])
        }
      }
    }]
  }

  skillsChart.setOption(option)

  window.addEventListener('resize', () => {
    skillsChart && skillsChart.resize()
  })
}

const getTimelineColor = (index) => {
  const colors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C']
  return colors[index % colors.length]
}

watch(() => appStore.jobProfile, () => {
  nextTick(() => {
    initSkillsChart()
  })
}, { immediate: true })

onMounted(() => {
  if (!appStore.jobProfile) {
    appStore.fetchJobProfile()
  }
})
</script>

<style scoped lang="scss">
.job-analysis-container {
  max-width: 1400px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 16px;
  justify-content: space-between;
}

.input-card {
  margin-bottom: 20px;
}

.quick-jobs {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;

  .quick-title {
    font-size: 13px;
    color: #909399;
    margin-bottom: 8px;
  }
}

.path-card {
  :deep(.el-timeline-item__content) {
    .path-title {
      font-weight: 600;
      color: #303133;
      margin-bottom: 8px;
    }

    .path-requirements {
      font-size: 13px;
      color: #606266;
      line-height: 1.6;
    }
  }
}

.profile-card {
  margin-bottom: 20px;

  .summary-section {
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 1px solid #f0f0f0;

    h4 {
      margin: 0 0 12px 0;
      color: #303133;
      font-size: 15px;
    }

    p {
      margin: 0;
      color: #606266;
      line-height: 1.8;
      font-size: 14px;
    }
  }

  .section {
    margin-bottom: 20px;

    h4 {
      display: flex;
      align-items: center;
      gap: 6px;
      margin: 0 0 12px 0;
      color: #303133;
      font-size: 15px;
    }
  }
}

.chart-card {
  .echarts-chart {
    height: 300px;
    width: 100%;
  }
}
</style>
