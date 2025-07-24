import axios from 'axios'
import { supabase } from './supabase'

// Configuration de l'URL de base selon l'environnement
const getBaseURL = () => {
  if ((import.meta as any).env?.DEV) {
    return "http://localhost:8000/api";
  }
  // En production, utilisez l'URL de votre backend déployé
  return "https://cv-offer-comparer.onrender.com/api";
};

const api = axios.create({
  baseURL: getBaseURL(),
  timeout: 30000,
});

// Intercepteur pour ajouter le token d'authentification
api.interceptors.request.use(async (config) => {
  const {
    data: { session },
  } = await supabase.auth.getSession();
  if (session?.access_token) {
    config.headers.Authorization = `Bearer ${session.access_token}`;
  }
  return config;
});

// Intercepteur pour gérer les erreurs
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Rediriger vers la page de connexion si non authentifié
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// Fonction de test SSE
export async function testStream(
  onStatus: (message: string) => void,
  onProgress: (progress: number, current: number, total: number) => void,
  onComplete: () => void,
  onError: (error: string) => void
) {
  try {
    const response = await fetch(`${getBaseURL()}/test-stream`, {
      method: "GET",
      headers: {
        Accept: "text/event-stream",
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error("Impossible de lire la réponse");
    }

    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || ""; // Garder la dernière ligne incomplète

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          try {
            const data = JSON.parse(line.slice(6));

            switch (data.type) {
              case "status":
                onStatus(data.message);
                break;
              case "progress":
                onProgress(data.value, data.current, data.total);
                break;
              case "complete":
                onComplete();
                break;
              case "error":
                onError(data.message);
                break;
            }
          } catch (e) {
            console.error("Erreur parsing SSE:", e);
          }
        }
      }
    }
  } catch (error: any) {
    onError(error.message || "Erreur lors du test");
  }
}

// Fonction pour gérer les SSE avec l'API Fetch native
export async function streamCompare(
  offerText: string,
  cvText: string,
  onStatus: (message: string) => void,
  onProgress: (progress: number, current: number, total: number) => void,
  onItem: (item: any) => void,
  onSummary: (summary: any) => void,
  onComplete: () => void,
  onError: (error: string) => void
) {
  try {
    const {
      data: { session },
    } = await supabase.auth.getSession();
    const token = session?.access_token;

    const response = await fetch(`${getBaseURL()}/compare-stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
        Accept: "text/event-stream",
      },
      body: JSON.stringify({
        offer_text: offerText,
        cv_text: cvText,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error("Impossible de lire la réponse");
    }

    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || ""; // Garder la dernière ligne incomplète

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          try {
            const data = JSON.parse(line.slice(6));

            switch (data.type) {
              case "status":
                onStatus(data.message);
                break;
              case "progress":
                onProgress(data.value, data.current, data.total);
                break;
              case "item":
                onItem(data.item);
                break;
              case "summary":
                onSummary(data.summary);
                break;
              case "complete":
                onComplete();
                break;
              case "error":
                onError(data.message);
                break;
            }
          } catch (e) {
            console.error("Erreur parsing SSE:", e);
          }
        }
      }
    }
  } catch (error: any) {
    onError(error.message || "Erreur lors de la comparaison");
  }
}

export { api } 