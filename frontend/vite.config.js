import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    // Local dev only: lets `npm run dev` talk to the backend running on
    // :8000 without hardcoding that host into VITE_API_BASE_URL. From
    // Phase 18 onward, Nginx does this same job in front of the built
    // app, so VITE_API_BASE_URL=/api never needs to change.
    proxy: {
      '/api': { target: 'http://localhost:8000', changeOrigin: true },
      '/uploads': { target: 'http://localhost:8000', changeOrigin: true },
    },
  },
  build: {
    outDir: 'dist',
  },
})
