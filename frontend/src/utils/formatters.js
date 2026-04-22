/**
 * 将时间格式化为中文场景更易读的展示文本。
 * 后端时间为空时，兜底返回当前时间，避免界面出现空白。
 */
export function formatDateTime(value = Date.now()) {
  return new Date(value).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

/**
 * 生成新建会话时的默认名称。
 * 这样即使用户不手动输入标题，也能得到可区分的记录名称。
 */
export function createSessionName(prefix = '舌诊记录') {
  const date = new Date()
  const datePart = date.toLocaleDateString('zh-CN').replace(/\//g, '-')
  const timePart = date.toTimeString().slice(0, 5).replace(':', '')
  return `${prefix} ${datePart} ${timePart}`
}

/**
 * 对文本做空值兜底，防止模板层大量判空。
 */
export function safeText(value, fallback = '暂无内容') {
  if (value === null || value === undefined) {
    return fallback
  }

  const text = String(value).trim()
  return text || fallback
}
