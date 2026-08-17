import { defineStore } from 'pinia'
import { api } from '../api/http'

export const useCheckoutStore = defineStore('checkout', {
  state: () => ({
    order: null,
    creating: false,
    confirming: false,
    error: '',
    confirmMessage: '',
  }),
  actions: {
    reset() {
      this.order = null
      this.error = ''
      this.confirmMessage = ''
    },
    async createOrder(payload) {
      this.creating = true
      this.error = ''
      this.confirmMessage = ''
      try {
        this.order = await api.createOrder(payload)
      } catch (error) {
        this.error = error.message
      } finally {
        this.creating = false
      }
    },
    async confirmOrder() {
      if (!this.order) return
      this.confirming = true
      this.error = ''
      try {
        const result = await api.confirmOrder(this.order.order_no)
        this.order = result.order
        this.confirmMessage =
          result.notification_channel === 'smtp'
            ? '确认成功，通知邮件已发送。'
            : '确认成功，通知已写入本地 outbox。'
      } catch (error) {
        this.error = error.message
      } finally {
        this.confirming = false
      }
    },
  },
})

