<template>
  <section class="storefront-hero">
    <div class="hero-copy">
      <span class="eyebrow">Private Digital Store</span>
      <h1>VirtualPay</h1>
      <p>面向游戏、在线服务和数字资源的小型虚拟商品交易平台。</p>
    </div>
    <div class="hero-metrics" aria-label="平台概览">
      <div>
        <strong>{{ catalog.products.length }}</strong>
        <span>在售商品</span>
      </div>
      <div>
        <strong>2</strong>
        <span>支付方式</span>
      </div>
    </div>
  </section>

  <section class="page-section">
    <div class="section-heading">
      <span>Catalog</span>
      <h2>选择虚拟商品</h2>
      <p>点击商品后填写邮箱、支付方式和备注，系统会生成待确认订单。</p>
    </div>

    <div v-if="catalog.loading" class="state-box">正在加载商品...</div>
    <div v-else-if="catalog.error" class="state-box error">{{ catalog.error }}</div>
    <div v-else class="product-grid">
      <ProductCard v-for="product in catalog.featuredProducts" :key="product.id" :product="product" />
    </div>
  </section>
</template>

<script setup>
import { onMounted } from 'vue'
import ProductCard from '../components/product/ProductCard.vue'
import { useCatalogStore } from '../stores/catalogStore'

const catalog = useCatalogStore()

onMounted(() => {
  if (!catalog.products.length) {
    catalog.fetchProducts()
  }
})
</script>
