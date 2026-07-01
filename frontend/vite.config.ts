import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 5173,
    proxy: {
      '/api/auth': {
        target: 'http://localhost:3000',
        changeOrigin: true,
      },
      '/api/admin': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/api/shipments': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/api/verification': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/api/me': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    }
  }
})
