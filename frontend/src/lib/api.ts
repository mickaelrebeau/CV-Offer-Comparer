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

// Fonction pour l'analyse gratuite (sans authentification)
export async function streamFreeCompare(
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
    const response = await fetch(`${getBaseURL()}/free-compare-stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "text/event-stream",
      },
      body: JSON.stringify({
        offer_text: offerText,
        cv_text: cvText,
      }),
    });

    if (!response.ok) {
      if (response.status === 429) {
        throw new Error("Vous avez déjà utilisé votre analyse gratuite. Veuillez créer un compte pour continuer.");
      }
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
    onError(error.message || "Erreur lors de la comparaison gratuite");
  }
}

// Fonction pour vérifier le statut de l'analyse gratuite
export async function checkFreeAnalysisStatus() {
  try {
    const response = await fetch(`${getBaseURL()}/free-analysis-status`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error: any) {
    console.error("Erreur lors de la vérification du statut:", error);
    return { 
      can_use_free_analysis: false, 
      message: "Erreur de vérification - Essai offert utilisé",
      error: error.message 
    };
  }
}

// Fonction pour réinitialiser l'analyse gratuite (pour les tests)
export async function resetFreeAnalysis() {
  try {
    const response = await fetch(`${getBaseURL()}/reset-free-analysis`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error: any) {
    console.error("Erreur lors de la réinitialisation:", error);
    throw error;
  }
}

// Fonction pour récupérer les statistiques des analyses gratuites
export async function getFreeAnalysisStats() {
  try {
    const response = await fetch(`${getBaseURL()}/free-analysis-stats`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error: any) {
    console.error("Erreur lors de la récupération des statistiques:", error);
    return {
      stats: { total_free_analyses: 0, today_free_analyses: 0, date: new Date().toISOString().split('T')[0] },
      redis_health: false,
      timestamp: new Date().toISOString()
    };
  }
}

// Fonction pour uploader un CV PDF pour l'essai gratuit
export async function uploadFreeCV(file: File): Promise<{ success: boolean; text: string; message: string }> {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${getBaseURL()}/free-upload-cv`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error: any) {
    console.error("Erreur lors de l'upload du CV gratuit:", error);
    return {
      success: false,
      text: "",
      message: error.message || "Erreur lors de l'upload du CV"
    };
  }
}

// Fonctions pour le simulateur d'entretien
export async function generateInterviewQuestions(
  cvFile: File,
  jobText: string,
  numQuestions: number = 5
): Promise<{ success: boolean; interview_session?: any; message: string }> {
  try {
    const formData = new FormData();
    formData.append('cv_file', cvFile);
    formData.append('job_text', jobText);
    formData.append('num_questions', numQuestions.toString());

    const response = await api.post('/interview/generate-questions', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  } catch (error: any) {
    console.error("Erreur lors de la génération des questions d'entretien:", error);
    return {
      success: false,
      message: error.response?.data?.detail || error.message || "Erreur lors de la génération des questions"
    };
  }
}

export async function analyzeInterviewResponses(
  questions: any[],
  answers: any[],
  cvText: string,
  jobText: string
): Promise<{ success: boolean; analysis?: any; message: string }> {
  try {
    const formData = new FormData();
    formData.append('questions', JSON.stringify(questions));
    formData.append('answers', JSON.stringify(answers));
    formData.append('cv_text', cvText);
    formData.append('job_text', jobText);

    const response = await api.post('/interview/analyze-responses', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  } catch (error: any) {
    console.error("Erreur lors de l'analyse des réponses:", error);
    return {
      success: false,
      message: error.response?.data?.detail || error.message || "Erreur lors de l'analyse des réponses"
    };
  }
}

export async function saveInterviewSession(interviewData: any): Promise<{ success: boolean; session_id?: string; message: string }> {
  try {
    const response = await api.post('/interview/save-session', interviewData);
    return response.data;
  } catch (error: any) {
    console.error("Erreur lors de la sauvegarde de la session d'entretien:", error);
    return {
      success: false,
      message: error.response?.data?.detail || error.message || "Erreur lors de la sauvegarde"
    };
  }
}

export async function getInterviewHistory(): Promise<{ success: boolean; interviews?: any[]; message: string }> {
  try {
    const response = await api.get('/interview/history');
    return response.data;
  } catch (error: any) {
    console.error("Erreur lors de la récupération de l'historique d'entretien:", error);
    return {
      success: false,
      message: error.response?.data?.detail || error.message || "Erreur lors de la récupération de l'historique"
    };
  }
}

export { api } 