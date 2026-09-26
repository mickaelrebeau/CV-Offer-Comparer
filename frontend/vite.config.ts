import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { copyFileSync, writeFileSync } from 'fs'
import { resolve } from 'path'
import { prerenderRoutes } from './prerender-routes'

const dist = (file: string) => resolve(__dirname, 'dist', file)

// Routes du routeur non prégénérées (espace connecté, liens e-mail…) : servies par un shell SPA
// vierge, pour ne pas hériter du head de l'accueil (canonical, JSON-LD…)
const SPA_SHELL = '_spa.html'
let spaRoutes: string[] = []

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  ssgOptions: {
    script: 'async',
    formatting: 'minify',
    // Fichiers plats (login.html) : `serve` les associe à /login via cleanUrls
    dirStyle: 'flat',
    beastiesOptions: false,
    includedRoutes(paths) {
      spaRoutes = paths.filter((path) => !prerenderRoutes.includes(path) && !path.includes(':'))
      // Appelé avant le rendu : dist/index.html est encore le template client non rendu
      copyFileSync(dist('index.html'), dist(SPA_SHELL))
      return prerenderRoutes
    },
    // `serve -s` réécrivait toutes les URL vers index.html (page d'accueil), même quand
    // une page prégénérée existait : seules les routes SPA sont réécrites désormais
    onFinished() {
      const config = {
        cleanUrls: true,
        rewrites: spaRoutes.map((source) => ({ source, destination: `/${SPA_SHELL}` })),
      }
      writeFileSync(dist('serve.json'), JSON.stringify(config, null, 2))
    },
  },
})
