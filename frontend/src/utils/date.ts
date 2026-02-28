import { format, formatDistanceToNow } from 'date-fns'
import { uk, ru, enUS } from 'date-fns/locale'

type Locale = 'uk' | 'ru' | 'en'

const localeMap: Record<Locale, typeof uk> = {
  uk,
  ru,
  en: enUS,
}

function detectLocale(): Locale {
  if (typeof navigator === 'undefined') return 'en'
  
  const lang = navigator.language.toLowerCase()
  if (lang.startsWith('uk')) return 'uk'
  if (lang.startsWith('ru')) return 'ru'
  return 'en'
}

export function relativeTime(dateString: string): string {
  try {
    const date = new Date(dateString)
    const locale = localeMap[detectLocale()]
    return formatDistanceToNow(date, { addSuffix: true, locale })
  } catch {
    return dateString
  }
}

export function fullDate(dateString: string): string {
  try {
    const date = new Date(dateString)
    return date.toISOString()
  } catch {
    return dateString
  }
}

export function exactTime(dateString: string): string {
  try {
    const date = new Date(dateString)
    const locale = localeMap[detectLocale()]
    return format(date, 'yyyy-MM-dd HH:mm', { locale })
  } catch {
    return dateString
  }
}
