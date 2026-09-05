import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/nj-drivers-test/',
  build: {
    // Built site lives outside docs/ so internal documentation is never
    // published; deploy-pages.yml uploads site/ as the Pages artifact.
    outDir: '../site',
    emptyOutDir: true,
  },
})
