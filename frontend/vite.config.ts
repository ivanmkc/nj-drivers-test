import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/nj-drivers-test/',
  build: {
    outDir: '../docs',
    emptyOutDir: false,
  },
})
