import {fileURLToPath, URL} from 'node:url'
import {defineConfig, loadEnv} from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import {ElementPlusResolver} from 'unplugin-vue-components/resolvers'
 
export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, process.cwd(), '')
    const serverUrl = (env.VITE_SERVER_URL || 'http://10.252.133.135:5000').replace(/\/$/, '')
    
    return {
    plugins: [
        vue(),
        vueJsx(),
        AutoImport({
            resolvers: [ElementPlusResolver()],
        }),
        Components({
            resolvers: [ElementPlusResolver()],
        }),
    ],
    resolve: {
        alias: {
            '@': fileURLToPath(new URL('./src', import.meta.url))
        }
    },
    server: {
        host: '0.0.0.0',
        port: 5173,
        proxy: {
            '/api': {
                target: serverUrl,
                changeOrigin: true,
                rewrite: (path) => path.replace(/^\/api/, '/api')
            },
        }
    },
    base: './',
    build: {
        outDir: 'dist',
    },
}
})
