import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { generateInterviewQuestions, analyzeInterviewResponses } from '@/lib/api'

export const useInterviewStore = defineStore('interview', () => {
  // État
  const currentInterview = ref<any>(null)
  const isLoading = ref(false)
  const error = ref('')

  // Getters
  const hasCurrentInterview = computed(() => !!currentInterview.value)
  const currentQuestions = computed(() => currentInterview.value?.questions || [])

  // Actions
  const generateQuestions = async (cvFile: File, jobText: string, numQuestions: number = 5) => {
    isLoading.value = true
    error.value = ''
    
    try {
      const result = await generateInterviewQuestions(cvFile, jobText, numQuestions)
      
      if (result.success && result.interview_session) {
        currentInterview.value = result.interview_session
        return { success: true, interview: result.interview_session }
      } else {
        throw new Error(result.message)
      }
    } catch (err: any) {
      error.value = err.message || 'Erreur lors de la génération des questions'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  const analyzeResponses = async (questions: any[], answers: any[], cvText: string, jobText: string) => {
    isLoading.value = true
    error.value = ''
    
    try {
      const result = await analyzeInterviewResponses(questions, answers, cvText, jobText)
      
      if (result.success && result.analysis) {
        return { success: true, analysis: result.analysis }
      } else {
        throw new Error(result.message)
      }
    } catch (err: any) {
      error.value = err.message || 'Erreur lors de l\'analyse des réponses'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  const clearCurrentInterview = () => {
    currentInterview.value = null
    error.value = ''
  }

  return {
    // État
    currentInterview,
    isLoading,
    error,
    
    // Getters
    hasCurrentInterview,
    currentQuestions,
    
    // Actions
    generateQuestions,
    analyzeResponses,
    clearCurrentInterview
  }
}) 