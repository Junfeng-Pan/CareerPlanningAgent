<template>
  <div class="job-profile-detail">
    <el-row :gutter="20">
      <!-- 左侧：岗位信息 -->
      <el-col :span="14">
        <div class="summary-section">
          <h3>岗位综述</h3>
          <p class="summary-text">{{ profile?.summary || '暂无描述' }}</p>
        </div>

        <div class="skills-section">
          <h3><el-icon><FolderOpened /></el-icon> 专业技能要求</h3>
          <div class="skill-cards">
            <el-card
              v-for="(skill, index) in profile?.skills"
              :key="index"
              shadow="hover"
              class="skill-card"
            >
              <div class="skill-name">{{ skill.name }}</div>
              <div class="skill-evidence">{{ skill.evidence }}</div>
            </el-card>
          </div>
        </div>

        <div class="thresholds-section" v-if="profile?.thresholds?.length">
          <h3><el-icon><Document /></el-icon> 基础门槛要求</h3>
          <div class="threshold-tags">
            <el-tag
              v-for="(threshold, index) in profile.thresholds"
              :key="index"
              type="warning"
              effect="plain"
              style="margin: 4px"
            >
              {{ threshold.name }}
            </el-tag>
          </div>
        </div>

        <div class="professionalism-section" v-if="profile?.professionalism?.length">
          <h3><el-icon><Star /></el-icon> 职业素养要求</h3>
          <div class="prof-tags">
            <el-tag
              v-for="(prof, index) in profile.professionalism"
              :key="index"
              type="success"
              effect="plain"
              style="margin: 4px"
            >
              {{ prof.name }}
            </el-tag>
          </div>
        </div>
      </el-col>

      <!-- 右侧：图表和发展路径 -->
      <el-col :span="10">
        <div class="chart-section" v-if="profile?.skills?.length">
          <h3>技能要求分布</h3>
          <div ref="barChartRef" class="bar-chart"></div>
        </div>

        <div class="path-section" v-if="profile?.paths?.length">
          <h3><el-icon><Guide /></el-icon> 职业发展路径</h3>
          <el-timeline class="path-timeline">
            <el-timeline-item
              v-for="(path, index) in profile.paths"
              :key="index"
              :timestamp="`路径 ${index + 1}`"
              placement="top"
              :color="getTimelineColor(index)"
            >
              <el-card shadow="hover">
                <div class="path-title">{{ path.path }}</div>
                <div class="path-req">{{ path.requisitions }}</div>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  profile: Object
})

const barChartRef = ref(null)
let barChart = null

const initBarChart = () => {
  if (!barChartRef.value || !props.profile?.skills?.length) return

  barChart = echarts.init(barChartRef.value)

  const skills = props.profile.skills.slice(0, 10)
  const skillNames = skills.map(s => s.name)

  const option = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: {
      type: 'category',
      data: skillNames,
      axisLabel: { interval: 0, rotate: 30, fontSize: 11 }
    },
    yAxis: { type: 'value', name: '重要程度' },
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
      }
    }]
  }

  barChart.setOption(option)
  window.addEventListener('resize', () => barChart && barChart.resize())
}

const getTimelineColor = (index) => {
  const colors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C']
  return colors[index % colors.length]
}

watch(() => props.profile, () => {
  nextTick(() => initBarChart())
}, { immediate: true })
</script>

<style scoped lang="scss">
.job-profile-detail {
  .summary-section {
    background: #fff;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 20px;

    h3 {
      margin: 0 0 12px 0;
      font-size: 16px;
      color: #303133;
    }

    .summary-text {
      margin: 0;
      font-size: 14px;
      line-height: 1.8;
      color: #606266;
    }
  }

  .skills-section, .thresholds-section, .professionalism-section {
    background: #fff;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 20px;

    h3 {
      display: flex;
      align-items: center;
      gap: 6px;
      margin: 0 0 12px 0;
      font-size: 16px;
      color: #303133;
    }
  }

  .skill-cards {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;

    .skill-card {
      .skill-name {
        font-weight: 600;
        color: #303133;
        margin-bottom: 8px;
        font-size: 14px;
      }

      .skill-evidence {
        font-size: 12px;
        color: #909399;
        line-height: 1.5;
      }
    }
  }

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

    .bar-chart {
      height: 250px;
      width: 100%;
    }
  }

  .path-section {
    background: #fff;
    padding: 20px;
    border-radius: 12px;

    h3 {
      display: flex;
      align-items: center;
      gap: 6px;
      margin: 0 0 16px 0;
      font-size: 16px;
      color: #303133;
    }

    .path-timeline {
      :deep(.el-timeline-item__content) {
        .path-title {
          font-weight: 600;
          color: #303133;
          margin-bottom: 6px;
        }

        .path-req {
          font-size: 13px;
          color: #606266;
          line-height: 1.6;
        }
      }
    }
  }
}
</style>
