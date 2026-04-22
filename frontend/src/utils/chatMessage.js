const IMAGE_MESSAGE_PREFIX = '__TD_IMAGE__:'
const THINK_OPEN_TAG = '<think>'
const THINK_CLOSE_TAG = '</think>'

function normalizeImageUrl(url = '') {
  if (!url) {
    return ''
  }

  if (/^(blob:|data:|https?:\/\/|\/)/i.test(url)) {
    return url
  }

  return `/${url.replace(/^\/+/, '')}`
}

export function parseStoredImageMessage(content = '') {
  if (!content.startsWith(IMAGE_MESSAGE_PREFIX)) {
    return null
  }

  try {
    const payload = JSON.parse(content.slice(IMAGE_MESSAGE_PREFIX.length))
    return {
      ...payload,
      preview_url: normalizeImageUrl(payload.preview_url || payload.storage_path || ''),
    }
  } catch (error) {
    console.warn('Failed to parse stored image message.', error)
    return null
  }
}

export function splitAssistantMessageContent(content = '') {
  const openIndex = content.indexOf(THINK_OPEN_TAG)
  if (openIndex === -1) {
    return {
      hasThink: false,
      thinkContent: '',
      answerContent: content.trim(),
      thinkClosed: true,
    }
  }

  const prefix = content.slice(0, openIndex)
  const afterOpen = content.slice(openIndex + THINK_OPEN_TAG.length)
  const closeIndex = afterOpen.indexOf(THINK_CLOSE_TAG)

  if (closeIndex === -1) {
    return {
      hasThink: true,
      thinkContent: afterOpen.trim(),
      answerContent: prefix.trim(),
      thinkClosed: false,
    }
  }

  const thinkContent = afterOpen.slice(0, closeIndex).trim()
  const suffix = afterOpen.slice(closeIndex + THINK_CLOSE_TAG.length)
  const answerContent = `${prefix}${suffix}`.trim()

  return {
    hasThink: Boolean(thinkContent),
    thinkContent,
    answerContent,
    thinkClosed: true,
  }
}

export function getSpeakableAssistantContent(content = '') {
  const { answerContent, thinkContent } = splitAssistantMessageContent(content)
  return (answerContent || thinkContent || '')
    .replace(/<[^>]+>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}
