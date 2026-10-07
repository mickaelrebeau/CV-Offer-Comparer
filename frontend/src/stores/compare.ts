import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  api,
  streamCompare,
  streamFreeCompare,
  checkFreeAnalysisStatus,
  getComparison,
  getComparisonDiff,
  type ComparisonDiff,
} from "@/lib/api";
import { useAuthStore } from "./auth";
import { useApplicationContextStore } from "./applicationContext";
import posthog from "posthog-js";
import { STORAGE_KEYS, readStorage, removeStorage } from "@/lib/storageKeys";
import { t } from "@/i18n";


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

/** CV + offre d'un élément de l'historique, proposés comme contexte courant */
export interface HistoryContext {
  cvText: string;
  offerText: string;
  offerUrl?: string | null;
}

/** Analyse réanalysée avec un CV mis à jour (offre conservée) */
export interface RescoreParent {
  id: string;
  matchPercentage: number;
}

export const useCompareStore = defineStore("compare", () => {
  // CV et offre : contexte de candidature partagé entre les modules
  const context = useApplicationContextStore();
  const historyContext = ref<HistoryContext | null>(null);
  const comparisonResult = ref<ComparisonResult | null>(null);
  // Identifiant (historique) et offre du résultat affiché, renvoyés par le flux ou l'historique
  const currentComparisonId = ref<string | null>(null);
  const analyzedOffer = ref<{ text: string; url: string | null } | null>(null);
  // Réanalyse en préparation : la prochaine analyse est rattachée à ce résultat
  const rescoreParent = ref<RescoreParent | null>(null);
  // Évolution par rapport à la version précédente (réanalyse)
  const diff = ref<ComparisonDiff | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);
  // Code API de la dernière erreur (quota plateforme, clé personnelle…)
  const errorCode = ref<string | null>(null);
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
      const used = readStorage(STORAGE_KEYS.freeAnalysisUsed);
      hasUsedFreeAnalysis.value = used === "true";
      return hasUsedFreeAnalysis.value;
    }
  };

  const markFreeAnalysisAsUsed = () => {
    localStorage.setItem(STORAGE_KEYS.freeAnalysisUsed, "true");
    hasUsedFreeAnalysis.value = true;
  };

  const resetFreeAnalysis = () => {
    removeStorage(STORAGE_KEYS.freeAnalysisUsed);
    hasUsedFreeAnalysis.value = false;
  };

  const hasData = computed(() => context.isComplete);

  const canAnalyze = computed(() => {
    const { isAuthenticated } = useAuthStore();
    return !hasUsedFreeAnalysis.value || isAuthenticated;
  });

  async function compareCVWithOffer() {
    const offer = context.offerText;
    const cv = context.cvText;

    if (!offer.trim() || !cv.trim()) {
      error.value = t("comparison.errors.missingInput");
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
        err.response?.data?.detail || t("comparison.errors.generic");
      console.error("Erreur de comparaison:", err);
    } finally {
      loading.value = false;
    }
  }

  async function compareCVWithOfferStream() {
    const offer = context.offerText;
    const cv = context.cvText;

    if (!offer.trim() || !cv.trim()) {
      error.value = t("comparison.errors.missingInput");
      return;
    }

    loading.value = true;
    error.value = null;
    errorCode.value = null;
    comparisonResult.value = null;
    currentComparisonId.value = null;
    analyzedOffer.value = { text: offer, url: context.offerUrl };
    diff.value = null;
    historyContext.value = null;
    progress.value = 0;
    status.value = t("comparison.statusStart");

    const items: ComparisonItem[] = [];
    let summary: any = null;
    const parent = rescoreParent.value;

    try {
      const { isAuthenticated } = useAuthStore();

      // La réanalyse (comptes connectés) passe la version précédente au flux
      const offerUrl = context.offerUrl;
      const streamFunction: typeof streamFreeCompare = isAuthenticated
        ? (...args) => streamCompare(...args, offerUrl, parent?.id)
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
        (comparisonId?: string) => {
          status.value = t("comparison.statusDone");
          currentComparisonId.value = comparisonId || null;

          if (isAuthenticated) {
            posthog.capture("comparison_completed", { comparison_mode: "authenticated" });
          } else {
            markFreeAnalysisAsUsed();
          }
          if (parent && comparisonId) {
            rescoreParent.value = null;
            void loadDiff(parent.id, comparisonId, true);
          }
        },
        (errorMessage: string, code?: string) => {
          error.value = errorMessage;
          errorCode.value = code || null;
          console.error("Erreur de comparaison:", errorMessage);
        },
      );
    } catch (err: any) {
      error.value = err.message || t("comparison.errors.generic");
      console.error("Erreur de comparaison:", err);
    } finally {
      loading.value = false;
      progress.value = 0;
    }
  }

  /** Évolution `beforeId` → `afterId` ; `track` : réanalyse qui vient d'aboutir (suivi PostHog). */
  async function loadDiff(beforeId: string, afterId: string, track = false) {
    try {
      const result = await getComparisonDiff(beforeId, afterId);
      // Résultat devenu obsolète entre-temps (autre analyse ouverte)
      if (currentComparisonId.value !== afterId) return;
      diff.value = result;
      if (track) {
        posthog.capture("comparison_rescored", {
          score_delta: Math.round(result.score_delta * 100),
          improved_count: result.improved.length,
          regressed_count: result.regressed.length,
        });
      }
    } catch (err) {
      // L'évolution est un complément : le résultat reste affiché sans elle
      console.error("Évolution indisponible:", err);
    }
  }

  /** Prépare la réanalyse du résultat affiché : même offre, CV à mettre à jour. */
  function startRescore() {
    const result = comparisonResult.value;
    if (!currentComparisonId.value || !result) return;
    rescoreParent.value = {
      id: currentComparisonId.value,
      matchPercentage: result.summary.matchPercentage,
    };
    // L'offre affichée est celle de l'analyse (le backend la reprend de toute façon)
    if (analyzedOffer.value) {
      context.setOffer(analyzedOffer.value.text, { url: analyzedOffer.value.url, from: "compare" });
    }
    historyContext.value = null;
  }

  function cancelRescore() {
    rescoreParent.value = null;
  }

  function clearResult() {
    comparisonResult.value = null;
    currentComparisonId.value = null;
    analyzedOffer.value = null;
    rescoreParent.value = null;
    diff.value = null;
    historyContext.value = null;
    error.value = null;
    errorCode.value = null;
  }

  /** Définit le CV et l'offre de l'élément d'historique ouvert comme contexte courant */
  function adoptHistoryContext() {
    if (!historyContext.value) return;
    context.setContext(historyContext.value, "compare");
    historyContext.value = null;
  }

  function dismissHistoryContext() {
    historyContext.value = null;
  }

  async function loadFromHistory(comparisonId: string) {
    loading.value = true;
    error.value = null;
    errorCode.value = null;
    rescoreParent.value = null;
    diff.value = null;
    try {
      const detail = await getComparison(comparisonId);
      const fromHistory = {
        cvText: detail.cv_text || "",
        offerText: detail.offer_text || "",
        offerUrl: detail.offer_url || null,
      };
      // Contexte vide ou identique : repris directement, sinon proposé à l'utilisateur
      if (!context.hasContext) context.setContext(fromHistory, "compare");
      historyContext.value =
        context.matches(fromHistory.cvText, fromHistory.offerText) ? null : fromHistory;
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
      currentComparisonId.value = String(detail.id);
      analyzedOffer.value = { text: fromHistory.offerText, url: fromHistory.offerUrl };
      if (detail.parent_comparison_id) void loadDiff(detail.parent_comparison_id, String(detail.id));
      status.value = t("comparison.historyLoaded");
    } catch (err: any) {
      error.value =
        err.response?.data?.detail || t("comparison.errors.loadHistory");
      throw err;
    } finally {
      loading.value = false;
    }
  }

  return {
    historyContext,
    comparisonResult,
    currentComparisonId,
    rescoreParent,
    diff,
    loading,
    error,
    errorCode,
    progress,
    status,
    hasData,
    hasUsedFreeAnalysis,
    canAnalyze,
    compareCVWithOffer,
    compareCVWithOfferStream,
    clearResult,
    startRescore,
    cancelRescore,
    adoptHistoryContext,
    dismissHistoryContext,
    loadFromHistory,
    checkFreeAnalysisUsage,
    markFreeAnalysisAsUsed,
    resetFreeAnalysis,
  };
}); 