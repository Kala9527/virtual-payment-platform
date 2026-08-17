<template>
  <div class="method-grid">
    <button
      v-for="method in methods"
      :key="method.value"
      type="button"
      class="method-option"
      :class="{ active: modelValue === method.value }"
      @click="$emit('update:modelValue', method.value)"
    >
      <component :is="method.icon" :size="22" />
      <span>
        <strong>{{ method.label }}</strong>
        <small>{{ method.caption }}</small>
      </span>
    </button>
  </div>
</template>

<script setup>
import { BadgeDollarSign, WalletCards } from '@lucide/vue'

defineProps({
  modelValue: {
    type: String,
    required: true,
  },
})

defineEmits(['update:modelValue'])

const methods = [
  { value: 'alipay', label: '支付宝', caption: '展示支付宝收款码', icon: BadgeDollarSign },
  { value: 'wechat', label: '微信支付', caption: '展示微信收款码', icon: WalletCards },
]
</script>

