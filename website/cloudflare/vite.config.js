import {defineConfig} from 'vite';
import {fileURLToPath} from 'node:url';
export default defineConfig({
  root:fileURLToPath(new URL('.',import.meta.url)),
  build:{outDir:'dist',emptyOutDir:true,target:'es2022'},
  worker:{format:'es'},
  server:{port:5173,strictPort:true},
});
