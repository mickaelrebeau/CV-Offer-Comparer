/** Routes publiques générées en HTML statique (SEO), en français puis sous /en. */
const frenchRoutes = [
  '/',
  '/free-trial',
  '/login',
  '/register',
  '/mentions-legales',
  '/cgv',
  '/confidentialite',
]

const toEnglish = (path: string) => (path === '/' ? '/en' : `/en${path}`)

export const prerenderRoutes = [...frenchRoutes, ...frenchRoutes.map(toEnglish)]
