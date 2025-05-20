import { AppIcons } from '@/icons'

export function resolveIcon(name?: string) {
  if (!name) {
    console.warn('Icon name is undefined or empty.')
    return null
}

  const icon = AppIcons[name as keyof typeof AppIcons]
  if (!icon) {
    console.warn(`Icon "${name}" not found in AppIcons.`)
  }
  return icon || null
}