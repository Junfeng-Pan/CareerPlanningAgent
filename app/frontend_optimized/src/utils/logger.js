// 前端日志工具 - 将日志发送到后端写入文件

const LOG_ENDPOINT = '/api/log'

// 原始 console.log 备份
const originalConsoleLog = console.log
const originalConsoleError = console.error
const originalConsoleWarn = console.warn
const originalConsoleInfo = console.info

// 拦截并转发日志到后端
function sendLogToBackend(level, args) {
  // 在本地存储日志（备用）
  const logEntry = {
    timestamp: new Date().toISOString(),
    level,
    message: args.map(arg =>
      typeof arg === 'object' ? JSON.stringify(arg) : String(arg)
    ).join(' ')
  }

  // 存入 localStorage 作为备份
  const storedLogs = JSON.parse(localStorage.getItem('frontend_logs') || '[]')
  storedLogs.push(logEntry)
  if (storedLogs.length > 100) storedLogs.shift() // 只保留最近 100 条
  localStorage.setItem('frontend_logs', JSON.stringify(storedLogs))

  // 发送到后端（不阻塞）
  navigator.sendBeacon(LOG_ENDPOINT, JSON.stringify(logEntry))
}

// 重写 console 方法
console.log = (...args) => {
  originalConsoleLog(...args)
  sendLogToBackend('INFO', args)
}

console.error = (...args) => {
  originalConsoleError(...args)
  sendLogToBackend('ERROR', args)
}

console.warn = (...args) => {
  originalConsoleWarn(...args)
  sendLogToBackend('WARN', args)
}

console.info = (...args) => {
  originalConsoleInfo(...args)
  sendLogToBackend('INFO', args)
}

// 捕获全局错误
window.addEventListener('error', (event) => {
  sendLogToBackend('ERROR', [
    `Uncaught error: ${event.message}`,
    `at ${event.filename}:${event.lineno}:${event.colno}`
  ])
})

window.addEventListener('unhandledrejection', (event) => {
  sendLogToBackend('ERROR', [`Unhandled promise rejection: ${event.reason}`])
})

// 导出获取本地存储日志的方法
export function getStoredLogs() {
  return JSON.parse(localStorage.getItem('frontend_logs') || '[]')
}

export function clearStoredLogs() {
  localStorage.removeItem('frontend_logs')
}
