<template>
  <div class="student-profile-detail">
    <el-row :gutter="20">
      <!-- 左侧：雷达图 -->
      <el-col :span="14">
        <div class="chart-section">
          <h3>技能能力雷达图</h3>
          <div ref="radarChartRef" class="radar-chart"></div>
        </div>
      </el-col>

      <!-- 右侧：详细信息 -->
      <el-col :span="10">
        <div class="info-section">
          <div class="info-card">
            <div class="info-label">职业素养</div>
            <el-progress
              :percentage="getLevelPercentage(profile?.Professionalism?.level)"
              :color="getLevelColor(profile?.Professionalism?.level)"
              :format="() => profile?.Professionalism?.level || '未知'"
            />
          </div>

          <div class="info-card">
            <div class="info-label">发展潜力</div>
            <el-progress
              :percentage="getLevelPercentage(profile?.Potential?.level)"
              :color="getLevelColor(profile?.Potential?.level)"
              :format="() => profile?.Potential?.level || '未知'"
            />
          </div>

          <div class="info-card">
            <div class="info-label">
              <el-icon><FolderOpened /></el-icon>
              技能列表 ({{ profile?.skills?.length || 0 }})
            </div>
            <div class="skill-tags">
              <el-tag
                v-for="(skill, index) in profile?.skills"
                :key="index"
                type="primary"
                effect="plain"
                style="margin: 4px"
              >
                {{ skill.name }}
              </el-tag>
            </div>
          </div>

          <div class="info-card" v-if="profile?.certificates?.length">
            <div class="info-label">
              <el-icon><Award /></el-icon>
              证书列表
            </div>
            <div class="certificate-list">
              <div v-for="(cert, index) in profile.certificates" :key="index" class="cert-item">
                <el-icon :size="20" color="#67C23A"><Award /></el-icon>
                <span>{{ cert.name }}</span>
              </div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 经历部分 -->
    <div class="experience-section" v-if="profile?.Experience?.length">
      <h3><el-icon><Briefcase /></el-icon> 经历列表</h3>
      <el-timeline>
        <el-timeline-item
          v-for="(exp, index) in profile.Experience"
          :key="index"
          :timestamp="`经历 ${index + 1}`"
          placement="top"
          color="#409EFF"
        >
          <el-card>
            <div class="exp-name">{{ exp.name }}</div>
            <div class="exp-evidence">{{ exp.evidence }}</div>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  profile: Object
})

const radarChartRef = ref(null)
let radarChart = null

const initRadarChart = () => {
  if (!radarChartRef.value || !props.profile) return

  radarChart = echarts.init(radarChartRef.value)

  const skills = props.profile.skills || []
  const maxSkills = 8

  const indicator = skills.slice(0, maxSkills).map(skill => ({
    name: skill.name,
    max: 100
  }))

  const values = skills.slice(0, maxSkills).map(() => 80)

  const option = {
    color: ['#409EFF'],
    tooltip: {},
    radar: {
      shape: 'circle',
      indicator: indicator,
      radius: '70%',
      center: ['50%', '50%'],
      axisName: {
        color: '#333',
        fontSize: 12,
        fontWeight: 'bold'
      },
      splitArea: {
        areaStyle: {
          color: ['#f8f9fa', '#e9ecef', '#dee2e6', '#ced4da']
        }
      },
      axisLine: { lineStyle: { color: '#409EFF' } },
      splitLine: { lineStyle: { color: '#409EFF' } }
    },
    series: [{
      type: 'radar',
      data: [{
        value: values,
        name: '技能水平',
        areaStyle: {
          color: new echarts.graphic.RadialGradient(0.5, 0.5, 1, [
            { offset: 0, color: 'rgba(64, 158, 255, 0.1)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.5)' }
          ])
        },
        lineStyle: { width: 3 },
        itemStyle: {
          color: '#409EFF',
          shadowBlur: 10,
          shadowColor: 'rgba(64, 158, 255, 0.5)'
        }
      }]
    }]
  }

  radarChart.setOption(option)
  window.addEventListener('resize', () => radarChart && radarChart.resize())
}

const getLevelPercentage = (level) => {
  const percentages = { '高': 90, '中': 60, '低': 30 }
  return percentages[level] || 50
}

const getLevelColor = (level) => {
  const colors = { '高': '#67C23A', '中': '#E6A23C', '低': '#F56C6C' }
  return colors[level] || '#909399'
}

watch(() => props.profile, () => {
  nextTick(() => initRadarChart())
}, { immediate: true })
</script>

<style scoped lang="scss">
.student-profile-detail {
  .chart-section {
    background: #fff;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 20px;

    h3 {
      margin: 0 0 16px 0;
      font-size: 16px;
      color: #303133;
    }

    .radar-chart {
      height: 350px;
      width: 100%;
    }
  }

  .info-section {
    .info-card {
      background: #fff;
      padding: 16px;
      border-radius: 12px;
      margin-bottom: 16px;

      .info-label {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 14px;
        font-weight: 600;
        color: #303133;
        margin-bottom: 12px;
      }

      .skill-tags {
        display: flex;
        flex-wrap: wrap;
      }
    }

    .certificate-list {
      .cert-item {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 0;
        font-size: 13px;
        color: #606266;
        border-bottom: 1px solid #f0f0f0;

        &:last-child {
          border-bottom: none;
        }
      }
    }
  }

  .experience-section {
    background: #fff;
    padding: 20px;
    border-radius: 12px;

    h3 {
      display: flex;
      align-items: center;
      gap: 8px;
      margin: 0 0 16px 0;
      font-size: 16px;
      color: #303133;
    }

    .exp-name {
      font-weight: 600;
      color: #303133;
      margin-bottom: 6px;
    }

    .exp-evidence {
      font-size: 13px;
      color: #909399;
      line-height: 1.6;
    }
  }
}
</style>
