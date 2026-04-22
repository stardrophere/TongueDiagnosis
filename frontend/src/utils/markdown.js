import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'

/**
 * 统一创建 Markdown 渲染器，避免多个组件重复初始化高亮逻辑。
 * 这里关闭原始 HTML，优先保证可控的渲染结果。
 */
export const markdownRenderer = new MarkdownIt({
  html: false,
  linkify: true,
  typographer: true,
  highlight(code, language) {
    if (language && hljs.getLanguage(language)) {
      try {
        return `<pre class="hljs"><code>${hljs.highlight(code, { language }).value}</code></pre>`
      } catch (error) {
        console.warn('代码高亮失败，回退为纯文本渲染。', error)
      }
    }

    return `<pre class="hljs"><code>${markdownRenderer.utils.escapeHtml(code)}</code></pre>`
  },
})

/**
 * 将 Markdown 文本转为 HTML。
 * 组件侧只关心展示，不必重复关心具体解析实现。
 */
export function renderMarkdown(content = '') {
  return markdownRenderer.render(content)
}
