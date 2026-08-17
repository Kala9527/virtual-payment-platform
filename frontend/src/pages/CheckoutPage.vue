<template>
  <section class="checkout-page">
    <RouterLink class="back-link" to="/">
      <ArrowLeft :size="17" />
      返回商品
    </RouterLink>

    <div v-if="catalog.loading" class="state-box">正在加载商品...</div>
    <div v-else-if="!product" class="state-box error">未找到该商品。</div>
    <template v-else>
      <section class="checkout-product">
        <img :src="assetUrl(product.image_url)" :alt="product.name" />
        <div>
          <span class="eyebrow">{{ product.category }}</span>
          <h1>{{ product.name }}</h1>
          <p>{{ product.description }}</p>
          <div class="price-line">{{ formatPrice(product.price_cents, product.currency) }}</div>
          <div class="delivery-line">
            <PackageCheck :size="18" />
            {{ product.delivery_hint }}
          </div>
          <div v-if="!isOnSale" class="sale-warning">{{ saleStatusLabel }}，当前不能购买。</div>
        </div>
      </section>

      <div v-if="isOnSale" class="checkout-grid">
        <section class="checkout-form">
          <div class="section-heading compact">
            <span>Checkout</span>
            <h2>提交支付信息</h2>
          </div>

          <form @submit.prevent="submitOrder">
            <label>
              邮箱联系方式
              <input v-model="form.buyer_email" type="email" placeholder="buyer@example.com" required />
              <span class="field-hint">此邮箱用于账号创建不用填写真实邮箱仅需符合邮箱格式即可</span>
            </label>

            <label>
              支付方式
              <PaymentMethodSelector v-model="form.payment_method" />
            </label>

            <label>
              备注
              <textarea
                v-model="form.remark"
                rows="4"
                maxlength="500"
                placeholder="可填写开通账号、联系方式或其他交付说明"
              />
            </label>

            <button class="primary-button full" type="submit" :disabled="checkout.creating">
              <CreditCard :size="18" />
              {{ checkout.creating ? '正在下单' : '下单并生成支付二维码' }}
            </button>
          </form>

          <p v-if="checkout.error" class="notice error">{{ checkout.error }}</p>
          <p v-if="checkout.confirmMessage" class="notice success">{{ checkout.confirmMessage }}</p>
        </section>

        <PaymentPanel
          v-if="checkout.order"
          :order="checkout.order"
          :confirming="checkout.confirming"
          @confirm="checkout.confirmOrder"
        />
        <section v-else class="empty-payment">
          <QrCode :size="46" />
          <h2>支付码将在这里展示</h2>
          <p>生成订单后可查看对应收款码，并在支付后点击确认。</p>
        </section>
      </div>
      <section v-else class="state-box error">该商品{{ saleStatusLabel }}，请选择其它在售商品。</section>
    </template>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowLeft, CreditCard, PackageCheck, QrCode } from '@lucide/vue'
import { assetUrl } from '../api/http'
import PaymentMethodSelector from '../components/payment/PaymentMethodSelector.vue'
import PaymentPanel from '../components/payment/PaymentPanel.vue'
import { useCatalogStore } from '../stores/catalogStore'
import { useCheckoutStore } from '../stores/checkoutStore'
import { formatPrice } from '../utils/format'

const route = useRoute()
const catalog = useCatalogStore()
const checkout = useCheckoutStore()

const form = reactive({
  buyer_email: '',
  payment_method: 'alipay',
  remark: '',
})

const product = computed(() => catalog.productById(route.params.productId))
const saleStatusMap = {
  1: '在售',
  2: '补货中',
  3: '停止发售',
}
const saleStatusLabel = computed(() => saleStatusMap[product.value?.sale_status] || '停止发售')
const isOnSale = computed(() => product.value?.sale_status === 1)

onMounted(async () => {
  if (!catalog.products.length) {
    await catalog.fetchProducts()
  }
})

watch(
  () => route.params.productId,
  () => checkout.reset(),
  { immediate: true },
)

async function submitOrder() {
  if (!product.value || !isOnSale.value) return
  await checkout.createOrder({
    product_id: product.value.id,
    buyer_email: form.buyer_email.trim(),
    payment_method: form.payment_method,
    remark: form.remark || null,
  })
}
</script>
