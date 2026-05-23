<template>
  <div class="black-hole-overlay" v-if="visible">
    <!-- 背景遮罩 -->
    <div class="overlay-backdrop"></div>
    
    <!-- 玻璃卡片 -->
    <div class="glass-card">
      <!-- 银河系系统 -->
      <div class="galaxy-container">
        <!-- 背景星空 -->
        <div class="star-field">
          <div v-for="n in 500" :key="`star-${n}`" class="star" :style="getStarStyle(n)"></div>
        </div>
        
        <!-- 螺旋星系旋臂 -->
        <div class="spiral-arms">
          <div class="arm arm-1"></div>
          <div class="arm arm-2"></div>
          <div class="arm arm-3"></div>
          <div class="arm arm-4"></div>
        </div>
        
        <!-- 旋臂粒子流 -->
        <div class="arm-particles">
          <div v-for="n in 300" :key="`arm-p-${n}`" class="arm-particle" :style="getArmParticleStyle(n)"></div>
        </div>
        
        <!-- 环绕粒子环 -->
        <div class="orbit-particles">
          <div v-for="n in 200" :key="`orbit-${n}`" class="orbit-particle" :style="getOrbitStyle(n)"></div>
        </div>
        
        <!-- 数据流 -->
        <div class="data-streams">
          <div v-for="n in 80" :key="`data-${n}`" class="data-particle" :style="getDataStyle(n)">
            {{ getRandomChar() }}
          </div>
        </div>
        
        <!-- 中心黑洞 -->
        <div class="black-hole-center">
          <div class="singularity"></div>
          <div class="event-horizon"></div>
          <div class="accretion-glow"></div>
        </div>
        
        <!-- 蓝绿光晕 -->
        <div class="cyan-halo">
          <div class="halo-layer layer-1"></div>
          <div class="halo-layer layer-2"></div>
          <div class="halo-layer layer-3"></div>
        </div>
      </div>
      
      <!-- 底部文字 -->
      <div class="card-footer">
        <p class="main-text">云端大语言模型正在分析中……</p>
        <div class="progress-info">
          <span class="progress-label">分析进度</span>
          <span class="progress-value">{{ progressPercent.toFixed(2) }}</span>
          <span class="progress-unit">%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps<{
  visible: boolean
}>()

const progressPercent = ref(0)
let progressInterval: number | null = null

const chars = '0123456789ABCDEF'

const getRandomChar = () => chars[Math.floor(Math.random() * chars.length)]

const getStarStyle = (index: number) => {
  const size = Math.random() * 2 + 0.5
  const x = Math.random() * 100
  const y = Math.random() * 100
  const delay = Math.random() * 4
  const duration = 2 + Math.random() * 3
  return {
    width: `${size}px`,
    height: `${size}px`,
    left: `${x}%`,
    top: `${y}%`,
    animationDelay: `${delay}s`,
    animationDuration: `${duration}s`
  }
}

const getArmParticleStyle = (index: number) => {
  const armIndex = index % 4
  const armAngle = armIndex * 90 + 45
  const distance = 25 + (index / 300) * 130
  const spiralOffset = (index / 300) * 200
  const angle = armAngle + spiralOffset + Math.random() * 40
  const delay = Math.random() * 4
  const size = 1 + Math.random() * 3
  
  return {
    width: `${size}px`,
    height: `${size}px`,
    transform: `rotate(${angle}deg) translateX(${distance}px)`,
    animationDelay: `${delay}s`,
    opacity: 0.5 + Math.random() * 0.5
  }
}

const getOrbitStyle = (index: number) => {
  const ring = Math.floor(index / 40)
  const radius = 45 + ring * 22 + Math.random() * 12
  const angle = (index % 40) * 9 + Math.random() * 8
  const delay = Math.random() * 5
  
  return {
    transform: `rotate(${angle}deg) translateX(${radius}px)`,
    animationDelay: `${delay}s`
  }
}

const getDataStyle = (index: number) => {
  const angle = (index / 80) * 360 + Math.random() * 25
  const startRadius = 150 + Math.random() * 60
  const delay = Math.random() * 3
  
  return {
    transform: `rotate(${angle}deg) translateX(${startRadius}px)`,
    animationDelay: `${delay}s`
  }
}

onMounted(() => {
  // 进度增长 - 使用递减增量，永远接近但不到100%
  progressInterval = window.setInterval(() => {
    const remaining = 99.99 - progressPercent.value
    const increment = remaining * 0.02 + Math.random() * 0.01
    progressPercent.value = Math.min(99.99, progressPercent.value + increment)
  }, 300)
})

onUnmounted(() => {
  if (progressInterval) clearInterval(progressInterval)
})
</script>

<style scoped>
.black-hole-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.overlay-backdrop {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(10px);
}

/* 玻璃卡片 - 蓝绿色调 */
.glass-card {
  position: relative;
  width: 480px;
  height: 480px;
  background: rgba(20, 30, 40, 0.6);
  border-radius: 20px;
  border: 1px solid rgba(64, 158, 255, 0.15);
  box-shadow: 
    0 30px 60px rgba(0, 0, 0, 0.4),
    0 0 60px rgba(64, 158, 255, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* 银河系容器 */
.galaxy-container {
  position: relative;
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
}

/* 星空背景 */
.star-field {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.star {
  position: absolute;
  background: white;
  border-radius: 50%;
  animation: twinkle ease-in-out infinite;
}

@keyframes twinkle {
  0%, 100% { opacity: 0.15; transform: scale(1); }
  50% { opacity: 0.9; transform: scale(1.5); }
}

/* 螺旋星系旋臂 - 蓝绿色 */
.spiral-arms {
  position: absolute;
  width: 380px;
  height: 380px;
  animation: galaxy-rotate 80s linear infinite;
}

.arm {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 300px;
  height: 150px;
  transform-origin: 0 0;
  background: radial-gradient(ellipse at 0 0,
    rgba(64, 158, 255, 0.5) 0%,
    rgba(103, 194, 58, 0.3) 20%,
    rgba(32, 160, 255, 0.15) 40%,
    rgba(48, 144, 255, 0.05) 60%,
    transparent 80%);
  border-radius: 0 100% 0 0;
  filter: blur(4px);
}

.arm-1 { transform: rotate(0deg); }
.arm-2 { transform: rotate(90deg); }
.arm-3 { transform: rotate(180deg); }
.arm-4 { transform: rotate(270deg); }

@keyframes galaxy-rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 旋臂粒子流 */
.arm-particles {
  position: absolute;
  width: 100%;
  height: 100%;
  animation: galaxy-rotate 80s linear infinite reverse;
}

.arm-particle {
  position: absolute;
  top: 50%;
  left: 50%;
  margin-left: -1.5px;
  margin-top: -1.5px;
  background: white;
  border-radius: 50%;
  box-shadow: 0 0 10px rgba(64, 158, 255, 0.9);
  animation: particle-spiral linear infinite;
}

@keyframes particle-spiral {
  0% {
    transform: rotate(var(--start-angle, 0deg)) translateX(var(--start-dist, 120px)) scale(1);
    opacity: 1;
  }
  100% {
    transform: rotate(calc(var(--start-angle, 0deg) + 200deg)) translateX(25px) scale(0.3);
    opacity: 0.2;
  }
}

/* 环绕粒子环 */
.orbit-particles {
  position: absolute;
  width: 100%;
  height: 100%;
}

.orbit-particle {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 2px;
  height: 2px;
  background: rgba(255, 255, 255, 0.85);
  border-radius: 50%;
  box-shadow: 0 0 5px rgba(64, 158, 255, 0.7);
  margin-left: -1px;
  margin-top: -1px;
  animation: orbit-in linear infinite;
}

@keyframes orbit-in {
  0% {
    opacity: 0.9;
    transform: rotate(0deg) translateX(var(--orbit-radius, 90px)) rotate(0deg);
  }
  100% {
    opacity: 0.15;
    transform: rotate(360deg) translateX(30px) rotate(-360deg);
  }
}

/* 数据流 */
.data-streams {
  position: absolute;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.data-particle {
  position: absolute;
  top: 50%;
  left: 50%;
  font-family: 'Courier New', monospace;
  font-size: 10px;
  font-weight: bold;
  color: #a0cfff;
  text-shadow: 0 0 8px rgba(160, 207, 255, 0.9);
  margin-left: -5px;
  margin-top: -5px;
  animation: data-spiral linear infinite;
}

@keyframes data-spiral {
  0% {
    transform: rotate(0deg) translateX(170px) scale(1);
    opacity: 1;
  }
  100% {
    transform: rotate(600deg) translateX(35px) scale(0.25);
    opacity: 0;
  }
}

/* 中心黑洞 */
.black-hole-center {
  position: relative;
  width: 110px;
  height: 110px;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10;
}

.singularity {
  position: absolute;
  width: 55px;
  height: 55px;
  border-radius: 50%;
  background: #000;
  box-shadow: 
    0 0 35px rgba(64, 158, 255, 0.9),
    0 0 70px rgba(64, 158, 255, 0.5),
    inset 0 0 25px rgba(32, 160, 255, 0.7);
  z-index: 5;
}

.event-horizon {
  position: absolute;
  width: 75px;
  height: 75px;
  border-radius: 50%;
  border: 2px solid rgba(64, 158, 255, 0.35);
  animation: horizon-pulse 2.5s ease-in-out infinite;
}

@keyframes horizon-pulse {
  0%, 100% { transform: scale(1); opacity: 0.35; }
  50% { transform: scale(1.2); opacity: 0.65; }
}

.accretion-glow {
  position: absolute;
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: radial-gradient(circle,
    rgba(64, 158, 255, 0.45) 0%,
    rgba(32, 160, 255, 0.25) 40%,
    transparent 70%);
  animation: glow-breathe 2.5s ease-in-out infinite;
}

@keyframes glow-breathe {
  0%, 100% { opacity: 0.5; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.25); }
}

/* 蓝绿光晕 */
.cyan-halo {
  position: absolute;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.halo-layer {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  border-radius: 50%;
}

.layer-1 {
  width: 130px;
  height: 130px;
  background: radial-gradient(circle, rgba(64, 158, 255, 0.3) 0%, transparent 70%);
  animation: halo-1 3.5s ease-in-out infinite;
}

.layer-2 {
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(32, 160, 255, 0.2) 0%, transparent 60%);
  animation: halo-2 4.5s ease-in-out infinite;
}

.layer-3 {
  width: 270px;
  height: 270px;
  background: radial-gradient(circle, rgba(103, 194, 58, 0.1) 0%, transparent 50%);
  animation: halo-3 5.5s ease-in-out infinite;
}

@keyframes halo-1 {
  0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 0.45; }
  50% { transform: translate(-50%, -50%) scale(1.35); opacity: 0.8; }
}

@keyframes halo-2 {
  0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 0.35; }
  50% { transform: translate(-50%, -50%) scale(1.25); opacity: 0.7; }
}

@keyframes halo-3 {
  0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 0.25; }
  50% { transform: translate(-50%, -50%) scale(1.15); opacity: 0.6; }
}

/* 卡片底部 */
.card-footer {
  padding: 20px 30px 25px;
  text-align: center;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.6), transparent);
}

.main-text {
  font-size: 16px;
  font-weight: 600;
  color: #f1f5f9;
  margin: 0 0 12px 0;
  letter-spacing: 1px;
}

.progress-info {
  display: flex;
  justify-content: center;
  align-items: baseline;
  gap: 6px;
  font-family: 'Courier New', monospace;
}

.progress-label {
  font-size: 12px;
  color: #94a3b8;
}

.progress-value {
  font-size: 18px;
  font-weight: bold;
  color: #67c23a;
  text-shadow: 0 0 10px rgba(103, 194, 58, 0.4);
  min-width: 70px;
}

.progress-unit {
  font-size: 14px;
  color: #67c23a;
}
</style>
