import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  api,
  streamCompare,
  streamFreeCompare,
  checkFreeAnalysisStatus,
  getComparison,
} from "@/lib/api";
import { useAuthStore } from "./auth";
import posthog from "posthog-js";


export interface ComparisonItem {
  id: string;
  category: string;
  offerText: string;
  cvText?: string;
  status: "match" | "missing" | "unclear";
  confidence: number;
  suggestions?: string[];
}

export interface ComparisonResult {
  items: ComparisonItem[];
  summary: {
    totalItems: number;
    matches: number;
    missing: number;
    unclear: number;
    matchPercentage: number;
  };
}

export const useCompareStore = defineStore("compare", () => {
  const offerText = ref("");
  const cvText = ref("");
  const comparisonResult = ref<ComparisonResult | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const progress = ref(0);
  const status = ref("");
  const hasUsedFreeAnalysis = ref(false);

  const checkFreeAnalysisUsage = async () => {
    try {
      const { isAuthenticated } = useAuthStore();

      if (isAuthenticated) {
        hasUsedFreeAnalysis.value = false;
        return false;
      }

      const status = await checkFreeAnalysisStatus();
      hasUsedFreeAnalysis.value = !status.can_use_free_analysis;
      return hasUsedFreeAnalysis.value;
    } catch (error) {
      console.error("Erreur lors de la vérification du statut:", error);
      const used = localStorage.getItem("cv-offer-compare-free-analysis-used");
      hasUsedFreeAnalysis.value = used === "true";
      return hasUsedFreeAnalysis.value;
    }
  };

  const markFreeAnalysisAsUsed = () => {
    localStorage.setItem("cv-offer-compare-free-analysis-used", "true");
    hasUsedFreeAnalysis.value = true;
  };

  const resetFreeAnalysis = () => {
    localStorage.removeItem("cv-offer-compare-free-analysis-used");
    hasUsedFreeAnalysis.value = false;
  };

  const hasData = computed(() => {
    const offer = String(offerText.value || "");
    const cv = String(cvText.value || "");
    return offer.trim() && cv.trim();
  });

  const canAnalyze = computed(() => {
    const { isAuthenticated } = useAuthStore();
    return !hasUsedFreeAnalysis.value || isAuthenticated;
  });

  async function compareCVWithOffer() {
    const offer = String(offerText.value || "");
    const cv = String(cvText.value || "");

    if (!offer.trim() || !cv.trim()) {
      error.value = "Veuillez saisir le texte de l'offre et du CV";
      return;
    }

    loading.value = true;
    error.value = null;

    try {
      const response = await api.post("/compare", {
        offer_text: offer,
        cv_text: cv,
      });

      comparisonResult.value = response.data;

      const { isAuthenticated } = useAuthStore();
      if (!isAuthenticated) {
        markFreeAnalysisAsUsed();
      }
    } catch (err: any) {
      error.value =
        err.response?.data?.detail || "Erreur lors de la comparaison";
      console.error("Erreur de comparaison:", err);
    } finally {
      loading.value = false;
    }
  }

  async function compareCVWithOfferStream() {
    const offer = String(offerText.value || "");
    const cv = String(cvText.value || "");

    if (!offer.trim() || !cv.trim()) {
      error.value = "Veuillez saisir le texte de l'offre et du CV";
      return;
    }

    loading.value = true;
    error.value = null;
    comparisonResult.value = null;
    progress.value = 0;
    status.value = "Début de l'analyse...";

    const items: ComparisonItem[] = [];
    let summary: any = null;

    try {
      const { isAuthenticated } = useAuthStore();

      const streamFunction = isAuthenticated
        ? streamCompare
        : streamFreeCompare;

      await streamFunction(
        offer,
        cv,
        (message: string) => {
          status.value = message;
          console.log("Status:", message);
        },
        (value: number, current: number, total: number) => {
          progress.value = value;
          console.log("Progress:", value + "%");
        },
        (item: any) => {
          items.push(item);
          comparisonResult.value = {
            items: [...items],
            summary: summary || {
              totalItems: 0,
              matches: 0,
              missing: 0,
              unclear: 0,
              matchPercentage: 0,
            },
          };
        },
        (summaryData: any) => {
          summary = summaryData;
          comparisonResult.value = {
            items: [...items],
            summary: summary,
          };
        },
        () => {
          status.value = "Comparaison terminée";

          if (isAuthenticated) {
            posthog.capture("comparison_completed", { comparison_mode: "authenticated" });
          } else {
            markFreeAnalysisAsUsed();
          }
        },
        (errorMessage: string) => {
          error.value = errorMessage;
          console.error("Erreur de comparaison:", errorMessage);
        }
      );
    } catch (err: any) {
      error.value = err.message || "Erreur lors de la comparaison";
      console.error("Erreur de comparaison:", err);
    } finally {
      loading.value = false;
      progress.value = 0;
    }
  }

  function clearData() {
    offerText.value = "";
    cvText.value = "";
    comparisonResult.value = null;
    error.value = null;
  }

  function updateOfferText(text: string) {
    offerText.value = String(text || "");
  }

  function updateCVText(text: string) {
    cvText.value = String(text || "");
  }

  async function loadFromHistory(comparisonId: string) {
    loading.value = true;
    error.value = null;
    try {
      const detail = await getComparison(comparisonId);
      offerText.value = detail.offer_text || "";
      cvText.value = detail.cv_text || "";
      comparisonResult.value = {
        items: (detail.items || []) as ComparisonItem[],
        summary: {
          totalItems: Number(detail.summary?.totalItems ?? detail.total_items ?? 0),
          matches: Number(detail.summary?.matches ?? detail.matches ?? 0),
          missing: Number(detail.summary?.missing ?? detail.missing ?? 0),
          unclear: Number(detail.summary?.unclear ?? detail.unclear ?? 0),
          matchPercentage: Number(
            detail.summary?.matchPercentage ?? detail.match_percentage ?? 0,
          ),
        },
      };
      status.value = "Historique chargé";
    } catch (err: any) {
      error.value =
        err.response?.data?.detail || "Impossible de charger cette comparaison";
      throw err;
    } finally {
      loading.value = false;
    }
  }

  return {
    offerText,
    cvText,
    comparisonResult,
    loading,
    error,
    progress,
    status,
    hasData,
    hasUsedFreeAnalysis,
    canAnalyze,
    compareCVWithOffer,
    compareCVWithOfferStream,
    clearData,
    updateOfferText,
    updateCVText,
    loadFromHistory,
    checkFreeAnalysisUsage,
    markFreeAnalysisAsUsed,
    resetFreeAnalysis,
  };
}); 