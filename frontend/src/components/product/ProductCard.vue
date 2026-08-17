<template>
  <article class="product-card" :class="{ unavailable: !isOnSale }">
    <img :src="assetUrl(product.image_url)" :alt="product.name" />
    <div class="product-card-body">
      <div class="product-meta">
        <span>{{ product.category }}</span>
        <strong>{{ formatPrice(product.price_cents, product.currency) }}</strong>
      </div>
      <div class="sale-status" :class="statusClass">{{ statusLabel }}</div>
      <h3>{{ product.name }}</h3>
      <p>{{ product.summary }}</p>
      <RouterLink v-if="isOnSale" class="primary-button" :to="`/checkout/${product.id}`">
        <ShoppingCart :size="16" />
        选择商品
      </RouterLink>
      <button v-else class="primary-button unavailable-button" type="button" disabled>
        <ShoppingCart :size="16" />
        暂不可购买
      </button>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'
import { ShoppingCart } from '@lucide/vue'
import { assetUrl } from '../../api/http'
import { formatPrice } from '../../utils/format'

const props = defineProps({
  product: {
    type: Object,
    required: true,
  },
})

const saleStatusMap = {
  1: { label: '在售', className: 'on-sale' },
  2: { label: '补货中', className: 'restocking' },
  3: { label: '停止发售', className: 'discontinued' },
}

const status = computed(() => saleStatusMap[props.product.sale_status] || saleStatusMap[3])
const statusLabel = computed(() => status.value.label)
const statusClass = computed(() => status.value.className)
const isOnSale = computed(() => props.product.sale_status === 1)
</script>
