import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://backend:8001', // Ajusta a la URL de tu backend en Docker
        changeOrigin: true,
        secure: false,
      },
    },
  },
  define: {
  },
});
