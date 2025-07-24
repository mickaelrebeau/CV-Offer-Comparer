import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api, streamCompare } from "@/lib/api";
import { supabase } from "@/lib/supabase";

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

  const hasData = computed(() => {
    const offer = String(offerText.value || "");
    const cv = String(cvText.value || "");
    return offer.trim() && cv.trim();
  });

  async function compareCVWithOffer() {
    // Vérification supplémentaire pour s'assurer que les valeurs sont des chaînes
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
    } catch (err: any) {
      error.value =
        err.response?.data?.detail || "Erreur lors de la comparaison";
      console.error("Erreur de comparaison:", err);
    } finally {
      loading.value = false;
    }
  }

  async function compareCVWithOfferStream() {
    // Vérification supplémentaire pour s'assurer que les valeurs sont des chaînes
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
      await streamCompare(
        offer,
        cv,
        // onStatus
        (message: string) => {
          status.value = message;
          console.log("Status:", message);
        },
        // onProgress
        (value: number, current: number, total: number) => {
          progress.value = value;
          console.log("Progress:", value + "%");
        },
        // onItem
        (item: any) => {
          items.push(item);
          // Mettre à jour le résultat en temps réel
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
        // onSummary
        (summaryData: any) => {
          summary = summaryData;
          comparisonResult.value = {
            items: [...items],
            summary: summary,
          };
        },
        // onComplete
        () => {
          status.value = "Comparaison terminée";
          console.log("Comparaison terminée");
        },
        // onError
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

  async function getAuthToken(): Promise<string> {
    const {
      data: { session },
    } = await supabase.auth.getSession();
    return session?.access_token || "";
  }

  function clearData() {
    offerText.value = "";
    cvText.value = "";
    comparisonResult.value = null;
    error.value = null;
  }

  function updateOfferText(text: string) {
    console.log("updateOfferText called with:", text.length, "characters");
    console.log("Before update - offerText.value:", offerText.value.length);
    console.log("Text to set:", text.substring(0, 50) + "...");
    offerText.value = String(text || "");
    console.log("After update - offerText.value:", offerText.value.length);
    console.log("hasData:", hasData.value);
    console.log("offerText.value type:", typeof offerText.value);
  }

  function updateCVText(text: string) {
    cvText.value = String(text || "");
    console.log(
      "updateCVText:",
      cvText.value.length,
      "hasData:",
      hasData.value
    );
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
    compareCVWithOffer,
    compareCVWithOfferStream,
    clearData,
    updateOfferText,
    updateCVText,
  };
}); 