import axios from 'axios'
import { supabase } from './supabase'

// Configuration de l'URL de base selon l'environnement
const getBaseURL = () => {
  if (import.meta.env.DEV) {
    return 'http://localhost:8000/api'
  }
  // En production, utilisez l'URL de votre backend déployé
  return (
    import.meta.env.VITE_API_URL ||
    "https://cv-offer-comparer.onrender.com/api"
  );
}

const api = axios.create({
  baseURL: getBaseURL(),
  timeout: 30000,
})

// Intercepteur pour ajouter le token d'authentification
api.interceptors.request.use(async (config) => {
  const { data: { session } } = await supabase.auth.getSession()
  if (session?.access_token) {
    config.headers.Authorization = `Bearer ${session.access_token}`
  }
  return config
})

// Intercepteur pour gérer les erreurs
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Rediriger vers la page de connexion si non authentifié
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export { api } 