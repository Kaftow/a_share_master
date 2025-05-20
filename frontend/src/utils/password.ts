import { ref, watch, type Ref } from 'vue'
import zxcvbn from 'zxcvbn'

export function usePasswordStrength(passwordRef: Ref<string>) {
  const score = ref(0)
  const feedback = ref<{ level: string; message: string[] }>({
    level: '非常弱',
    message: []
  })

  const levelMap = ['非常弱', '较弱', '一般', '强', '非常强']

  const customSuggestionsMap: Record<string, string> = {
    'Add another word or two. Uncommon words are better.': '添加一两个不常见的词更好',
    'Use a few words, avoid common phrases': '使用几个词语，避免常见短语',
    'No need for symbols, digits, or uppercase letters': '不一定需要符号、数字或大写字母',
    'Avoid repeated words and characters': '避免重复的词或字符',
    'Avoid sequences': '避免使用递增或递减的字符序列',
    'Avoid recent years': '避免使用最近的年份',
    'Avoid years that are associated with you': '避免使用和你有关的年份',
    'Avoid dates and years that are associated with you': '避免和你相关的日期或年份',
    'Avoid common passwords': '避免使用常见密码',
    'Avoid common names and surnames': '避免使用常见名字和姓氏',
  }

  const customWarningMap: Record<string, string> = {
    'This is a top-10 common password': '这是一个常见的弱密码',
    'This is a top-100 common password': '这是一个非常常见的密码',
    'This is a very common password': '这是一个非常弱的密码',
    'This is similar to a commonly used password': '这与常见密码非常相似',
    'A word by itself is easy to guess': '单个词很容易被猜中',
    'Names and surnames by themselves are easy to guess': '名字或姓氏单独使用很容易被猜中',
  }

  watch(passwordRef, (newVal) => {
    const result = zxcvbn(newVal)
    score.value = result.score

    const level = levelMap[result.score] || '未知'

    const translatedWarnings = result.feedback.warning && customWarningMap[result.feedback.warning]
      ? [customWarningMap[result.feedback.warning]]
      : []

    const translatedSuggestions = (result.feedback.suggestions || [])
      .map(s => customSuggestionsMap[s])
      .filter(Boolean)  // 过滤掉没有匹配到的提示

    feedback.value = {
      level,
      message: [...translatedWarnings, ...translatedSuggestions]
    }
  })

  return {
    score,
    feedback
  }
}

