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
      rollupOptions: {
        output: {
          manualChunks(id) {
            if (id.includes('node_modules/react-dom') || id.includes('node_modules/react/') || id.includes('node_modules/react-router')) {
              return 'vendor-react';
            }
            if (id.includes('node_modules/three') || id.includes('node_modules/@react-three')) {
              return 'vendor-3d';
            }
            if (id.includes('node_modules/framer-motion')) {
              return 'vendor-motion';
            }
            if (id.includes('node_modules/@unovis')) {
              return 'vendor-viz';
            }
          },
        },
      },
    },
    server: {
      port: 3000,
    },
  };
});
