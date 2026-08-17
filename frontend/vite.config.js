import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  build: {
    assetsDir: 'static',
  },
  server: {
    host: '127.0.0.1',
    port: 5176,
  },
})
