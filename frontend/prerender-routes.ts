/** Routes publiques générées en HTML statique (SEO). */
const frenchRoutes = [
  '/',
  '/free-trial',
  '/login',
  '/register',
  '/mentions-legales',
  '/cgv',
  '/confidentialite',
]

/** Versions anglaises (/en) des pages déjà traduites. Landing et pages légales : PR suivante (#17). */
const englishRoutes = ['/en/free-trial', '/en/login', '/en/register']

export const prerenderRoutes = [...frenchRoutes, ...englishRoutes]
