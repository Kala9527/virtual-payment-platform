import { createRouter, createWebHistory } from 'vue-router'
import StorefrontPage from '../pages/StorefrontPage.vue'
import CheckoutPage from '../pages/CheckoutPage.vue'

const routes = [
  { path: '/', name: 'storefront', component: StorefrontPage },
  { path: '/checkout/:productId', name: 'checkout', component: CheckoutPage, props: true },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})

