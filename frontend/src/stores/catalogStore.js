import { defineStore } from 'pinia'
import { api } from '../api/http'

export const useCatalogStore = defineStore('catalog', {
  state: () => ({
    products: [],
    loading: false,
    error: '',
  }),
  getters: {
    featuredProducts: (state) => state.products,
    productById: (state) => (id) => state.products.find((item) => item.id === Number(id)),
  },
  actions: {
    async fetchProducts() {
      this.loading = true
      this.error = ''
      try {
        this.products = await api.listProducts()
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },
  },
})

