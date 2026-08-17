<template>
  <section class="payment-panel">
    <div class="section-heading">
      <span>订单 {{ order.order_no }}</span>
      <h2>扫码完成支付</h2>
      <p>{{ order.payment_instruction.account_hint }}</p>
    </div>

    <div class="qr-wrap">
      <img :src="assetUrl(order.payment_instruction.qr_code_url)" :alt="order.payment_instruction.label" />
    </div>

    <dl class="order-summary">
      <div>
        <dt>商品</dt>
        <dd>{{ order.product_name }}</dd>
      </div>
      <div>
        <dt>金额</dt>
        <dd>{{ formatPrice(order.amount_cents, order.currency) }}</dd>
      </div>
      <div v-if="order.buyer_email">
        <dt>邮箱</dt>
        <dd>{{ order.buyer_email }}</dd>
      </div>
      <div v-if="order.remark">
        <dt>备注</dt>
        <dd>{{ order.remark }}</dd>
      </div>
    </dl>

    <button class="primary-button full" type="button" :disabled="confirming || isConfirmed" @click="$emit('confirm')">
      <CheckCircle2 :size="18" />
      {{ isConfirmed ? '已确认支付' : confirming ? '正在确认' : '我已完成支付' }}
    </button>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { CheckCircle2 } from '@lucide/vue'
import { assetUrl } from '../../api/http'
import { formatPrice } from '../../utils/format'

const props = defineProps({
  order: {
    type: Object,
    required: true,
  },
  confirming: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['confirm'])

const isConfirmed = computed(() => props.order.status === 'paid_confirmed')
</script>
