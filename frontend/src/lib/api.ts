import axios from 'axios'
import { currentLocale, t } from '@/i18n'
import { localizePath } from '@/i18n/routing'
import { getAccessToken, clearAccessToken } from './authToken'

/** Langue de l'interface : le backend traduit ses messages (erreurs, statuts SSE, e-mails). */
const localeHeaders = () => ({ 'Accept-Language': currentLocale() })

export const getApiBaseURL = () => {
  const apiUrl = (import.meta as any).env?.VITE_API_URL as string | undefined
  if (apiUrl) {
    return apiUrl.replace(/\/$/, "") + "/api"
  }
  if ((import.meta as any).env?.DEV) {
    return "http://localhost:8000/api"
  }
  return "/api"
};

const api = axios.create({
  baseURL: getApiBaseURL(),
  timeout: 30000,
});

api.interceptors.request.use(async (config) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  config.headers['Accept-Language'] = currentLocale();
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const url = String(error.config?.url || "")
    const isAuthRoute = url.includes("/auth/login") || url.includes("/auth/register") || url.includes("/auth/me")
    if (error.response?.status === 401 && !isAuthRoute) {
      clearAccessToken()
      window.location.href = localizePath("/login", currentLocale());
    }
    return Promise.reject(error);
  }
);

export type ComparisonHistoryItem = {
  id: string
  offer_excerpt: string
  cv_excerpt: string
  match_percentage: number
  total_items: number
  matches: number
  missing: number
  unclear: number
  created_at: string | null
}

export type ComparisonHistoryDetail = ComparisonHistoryItem & {
  summary: Record<string, unknown>
  items: unknown[]
  offer_text: string
  cv_text: string
}

export async function listComparisons(limit = 20, offset = 0) {
  const { data } = await api.get<{
    items: ComparisonHistoryItem[]
    total: number
    limit: number
    offset: number
  }>("/comparisons", { params: { limit, offset } })
  return data
}

export async function getComparison(id: string) {
  const { data } = await api.get<ComparisonHistoryDetail>(`/comparisons/${id}`)
  return data
}

export async function deleteComparison(id: string) {
  const { data } = await api.delete<{ success: boolean }>(`/comparisons/${id}`)
  return data
}

export type InterviewHistoryItem = {
  id: string
  job_excerpt: string
  cv_excerpt: string
  score_global: number
  num_questions: number
  duration_seconds: number
  created_at: string | null
}

export type InterviewHistoryDetail = InterviewHistoryItem & {
  questions: unknown[]
  answers: unknown[]
  analysis: Record<string, unknown>
  cv_text: string
  job_text: string
}

export async function listInterviews(limit = 20, offset = 0) {
  const { data } = await api.get<{
    items: InterviewHistoryItem[]
    total: number
    limit: number
    offset: number
  }>('/interviews', { params: { limit, offset } })
  return data
}

export async function getInterview(id: string) {
  const { data } = await api.get<InterviewHistoryDetail>(`/interviews/${id}`)
  return data
}

export async function deleteInterview(id: string) {
  const { data } = await api.delete<{ success: boolean }>(`/interviews/${id}`)
  return data
}

export type CoverLetterTone = 'professional' | 'warm' | 'confident' | 'formal'
export type CoverLetterLength = 'short' | 'standard' | 'detailed'
export type CoverLetterLanguage = 'auto' | 'fr' | 'en'

export type CoverLetter = {
  subject: string
  greeting: string
  opening: string
  body: string[]
  closing: string
  signoff: string
  signature: string
  language: string
}

export type CoverLetterSection = {
  key: 'subject' | 'greeting' | 'opening' | 'body' | 'closing' | 'signoff' | 'signature'
  text: string
}

export type CoverLetterHistoryItem = {
  id: string
  subject: string
  job_excerpt: string
  cv_excerpt: string
  tone: CoverLetterTone
  length: CoverLetterLength
  language: string
  word_count: number
  created_at: string | null
}

export type CoverLetterHistoryDetail = CoverLetterHistoryItem & {
  letter: CoverLetter
  cv_text: string
  job_text: string
}

export async function listCoverLetters(limit = 20, offset = 0) {
  const { data } = await api.get<{
    items: CoverLetterHistoryItem[]
    total: number
    limit: number
    offset: number
  }>('/cover-letters', { params: { limit, offset } })
  return data
}

export async function getCoverLetter(id: string) {
  const { data } = await api.get<CoverLetterHistoryDetail>(`/cover-letters/${id}`)
  return data
}

export async function deleteCoverLetter(id: string) {
  const { data } = await api.delete<{ success: boolean }>(`/cover-letters/${id}`)
  return data
}

export async function streamCoverLetter(
  params: {
    jobText: string
    cvText: string
    tone: CoverLetterTone
    length: CoverLetterLength
    language: CoverLetterLanguage
  },
  handlers: {
    onStatus: (message: string) => void
    onProgress: (progress: number) => void
    onSection: (section: CoverLetterSection) => void
    onLetter: (letter: CoverLetter, id: string | null) => void
    onError: (error: string) => void
  },
) {
  try {
    const form = new FormData()
    form.append('job_text', params.jobText)
    form.append('cv_text', params.cvText)
    form.append('tone', params.tone)
    form.append('length', params.length)
    form.append('language', params.language)

    const response = await fetch(`${getApiBaseURL()}/cover-letter`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${getAccessToken()}`,
        Accept: 'text/event-stream',
        ...localeHeaders(),
      },
      body: form,
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
    }

    const reader = response.body?.getReader()
    if (!reader) {
      throw new Error(t('errors.readStream'))
    }

    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue
        let data: any
        try {
          data = JSON.parse(line.slice(6))
        } catch (e) {
          console.error('Erreur parsing SSE:', e)
          continue
        }
        switch (data.type) {
          case 'status':
            handlers.onStatus(data.message)
            break
          case 'progress':
            handlers.onProgress(data.value)
            break
          case 'section':
            handlers.onSection(data.section)
            break
          case 'letter':
            handlers.onLetter(data.letter, data.id ?? null)
            break
          case 'error':
            handlers.onError(data.message)
            break
        }
      }
    }
  } catch (error: any) {
    handlers.onError(error.message || t('coverLetter.errors.generic'))
  }
}

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
    const token = getAccessToken();

    const response = await fetch(`${getApiBaseURL()}/compare-stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
        Accept: "text/event-stream",
        ...localeHeaders(),
      },
      body: JSON.stringify({
        offer_text: offerText,
        cv_text: cvText,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error(t("errors.readStream"));
    }

    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || ""; 

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
    onError(error.message || t("comparison.errors.generic"));
  }
}

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
    const response = await fetch(`${getApiBaseURL()}/free-compare-stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "text/event-stream",
        ...localeHeaders(),
      },
      body: JSON.stringify({
        offer_text: offerText,
        cv_text: cvText,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      if (response.status === 429 && !errorData.detail) {
        throw new Error(t("freeTrial.errors.alreadyUsed"));
      }
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error(t("errors.readStream"));
    }

    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

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
    onError(error.message || t("freeTrial.errors.generic"));
  }
}

export async function checkFreeAnalysisStatus() {
  try {
    const response = await fetch(`${getApiBaseURL()}/free-analysis-status`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        ...localeHeaders(),
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
      message: t("freeTrial.errors.statusCheck"),
      error: error.message 
    };
  }
}

export async function uploadFreeCV(file: File): Promise<{ success: boolean; text: string; message: string }> {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${getApiBaseURL()}/free-upload-cv`, {
      method: "POST",
      headers: localeHeaders(),
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
      message: error.message || t("upload.uploadError")
    };
  }
}

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
      message: error.response?.data?.detail || error.message || t("interview.errors.generate")
    };
  }
}

export async function analyzeInterviewResponses(
  questions: any[],
  answers: any[],
  cvText: string,
  jobText: string,
  durationSeconds: number = 0,
): Promise<{ success: boolean; analysis?: any; interview_id?: string; message: string }> {
  try {
    const formData = new FormData();
    formData.append('questions', JSON.stringify(questions));
    formData.append('answers', JSON.stringify(answers));
    formData.append('cv_text', cvText);
    formData.append('job_text', jobText);
    formData.append('duration_seconds', String(Math.max(0, Math.round(durationSeconds || 0))));

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
      message: error.response?.data?.detail || error.message || t("interview.errors.analyze")
    };
  }
}

export { api } 