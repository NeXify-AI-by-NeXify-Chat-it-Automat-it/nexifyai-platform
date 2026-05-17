import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), 'REACT_APP_');
  const defined = {};
  for (const [k, v] of Object.entries(env)) {
    defined[`process.env.${k}`] = JSON.stringify(v);
  }
  defined['process.env.NODE_ENV'] = JSON.stringify(mode);
  
  return {
    plugins: [react()],
    define: defined,
    build: {
      outDir: 'build',
      sourcemap: false,
    },
    server: {
      port: 3000,
    },
  };
});
