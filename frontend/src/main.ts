import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createHead } from '@vueuse/head'
import App from './App.vue'
import router from './router'
import './style.css'

const app = createApp(App)
const pinia = createPinia()
const head = createHead()

app.use(pinia)
app.use(router)
app.use(head)

app.mount('#app') 