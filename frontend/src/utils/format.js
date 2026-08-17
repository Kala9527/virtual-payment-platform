export function formatPrice(priceCents, currency = 'CNY') {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency,
  }).format(priceCents / 100)
}

