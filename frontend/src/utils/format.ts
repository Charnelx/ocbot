export function formatCurrency(value: number | null, currency: string | null): string {
  if (value === null || currency === null) return '—'
  
  const locale = typeof navigator !== 'undefined' && navigator.language.toLowerCase().startsWith('uk') 
    ? 'uk-UA' 
    : 'en-US'
  
  try {
    return new Intl.NumberFormat(locale, {
      style: 'currency',
      currency: currency === 'UAH' ? 'UAH' : 'USD',
      maximumFractionDigits: 0,
    }).format(value)
  } catch {
    return `${value.toLocaleString()} ${currency}`
  }
}

export function formatNumber(value: number): string {
  const locale = typeof navigator !== 'undefined' && navigator.language.toLowerCase().startsWith('uk') 
    ? 'uk-UA' 
    : 'en-US'
  
  return new Intl.NumberFormat(locale).format(value)
}
