import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createHead } from '@vueuse/head'
import App from './App.vue'
import router from './router'
import posthog from 'posthog-js'
import './style.css'

const app = createApp(App)
const pinia = createPinia()
const head = createHead()

const posthogToken = import.meta.env.VITE_POSTHOG_PROJECT_TOKEN
const posthogHost = import.meta.env.VITE_POSTHOG_HOST

if (posthogToken && posthogHost) {
  posthog.init(posthogToken, {
    api_host: posthogHost,
  })
} else if (import.meta.env.DEV) {
  const missingVariable = posthogToken
    ? 'VITE_POSTHOG_HOST'
    : 'VITE_POSTHOG_PROJECT_TOKEN'
  throw new Error(
    `${missingVariable} variable required by PostHog is missing or un-configured, this causes events to be silently missed. This error stops appearing once ${missingVariable} is configured`,
  )
}

app.use(pinia)
app.use(router)
app.use(head)

app.config.errorHandler = (error) => {
  if (posthogToken && posthogHost) {
    posthog.captureException(error)
  }
}

app.mount('#app') 