"""Service IA 100 % Gemini — un appel structuré par cas d'usage."""

from __future__ import annotations

import json
import re
import uuid
from typing import Any

from google import genai
from google.genai import types

from app.config import settings


class AIService:
    def __init__(self) -> None:
        self.model_name = settings.GEMINI_MODEL
        try:
            self.client = genai.Client(api_key=settings.GOOGLE_API_KEY)
            print(f"Client Gemini prêt ({self.model_name})")
        except Exception as exc:
            print(f"Erreur init Gemini: {exc}")
            self.client = None

    def _generate_json(self, prompt: str, *, temperature: float = 0.2) -> Any:
        if not self.client:
            raise RuntimeError("Client Gemini non initialisé")

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=temperature,
                response_mime_type="application/json",
            ),
        )
        text = (response.text or "").strip()
        if not text:
            raise RuntimeError("Réponse Gemini vide")
        return self._parse_json(text)

    @staticmethod
    def _parse_json(text: str) -> Any:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Fallback si le modèle enveloppe le JSON
            start_obj, end_obj = text.find("{"), text.rfind("}")
            start_arr, end_arr = text.find("["), text.rfind("]")
            if start_obj != -1 and end_obj > start_obj and (
                start_arr == -1 or start_obj < start_arr
            ):
                return json.loads(text[start_obj : end_obj + 1])
            if start_arr != -1 and end_arr > start_arr:
                return json.loads(text[start_arr : end_arr + 1])
            raise

    @staticmethod
    def _clip(text: str, max_chars: int = 12000) -> str:
        text = re.sub(r"\s+", " ", (text or "").strip())
        if len(text) <= max_chars:
            return text
        return text[:max_chars] + "…"

    def compare_offer_and_cv(self, offer_text: str, cv_text: str) -> dict[str, Any]:
        """
        Une seule requête LLM : extraction + matching + suggestions.
        Retourne { items: [...], summary: {...} } au format frontend.
        """
        offer = self._clip(offer_text)
        cv = self._clip(cv_text)

        prompt = f"""Tu es un expert ATS / recrutement. Compare l'offre et le CV.

OBJECTIF
- Extraire les exigences clés de l'offre (8 à 18 max, les plus importantes).
- Pour chacune, évaluer la présence dans le CV.
- Produire un JSON STRICT conforme au schéma.

STATUTS
- "match" : clairement présent dans le CV
- "unclear" : partiellement / implicitement présent
- "missing" : absent du CV
- confidence : nombre entre 0 et 1

CATÉGORIES possibles (choisir la plus pertinente) :
"langues", "soft skills", "expérience et niveau", "formation et certification",
"domaine métier", "compétences techniques", "autres"

Pour missing/unclear : 1 à 3 suggestions concrètes et actionnables pour le CV.
Pour match : suggestions = [] ou null.

SCHÉMA JSON
{{
  "items": [
    {{
      "category": "compétences techniques",
      "offerText": "exigence de l'offre",
      "cvText": "extrait/preuves du CV ou null",
      "status": "match|missing|unclear",
      "confidence": 0.0,
      "suggestions": ["..."]
    }}
  ]
}}

OFFRE:
\"\"\"{offer}\"\"\"

CV:
\"\"\"{cv}\"\"\"
"""

        raw = self._generate_json(prompt, temperature=0.15)
        items_raw = raw.get("items") if isinstance(raw, dict) else raw
        if not isinstance(items_raw, list) or not items_raw:
            raise RuntimeError("Gemini n'a renvoyé aucun item de comparaison")

        items: list[dict[str, Any]] = []
        matches = missing = unclear = 0

        for index, row in enumerate(items_raw):
            if not isinstance(row, dict):
                continue
            status = str(row.get("status") or "missing").lower().strip()
            if status not in {"match", "missing", "unclear"}:
                status = "missing"

            try:
                confidence = float(row.get("confidence") or 0.0)
            except (TypeError, ValueError):
                confidence = 0.0
            confidence = max(0.0, min(1.0, confidence))

            suggestions = row.get("suggestions") or []
            if not isinstance(suggestions, list):
                suggestions = []
            suggestions = [str(s).strip() for s in suggestions if str(s).strip()][:3]
            if status == "match":
                suggestions = []

            if status == "match":
                matches += 1
            elif status == "unclear":
                unclear += 1
            else:
                missing += 1

            cv_text_val = row.get("cvText")
            items.append(
                {
                    "id": str(uuid.uuid4()),
                    "category": str(row.get("category") or "autres"),
                    "offerText": str(row.get("offerText") or "").strip(),
                    "cvText": str(cv_text_val).strip() if cv_text_val else None,
                    "status": status,
                    "confidence": confidence,
                    "suggestions": suggestions or None,
                }
            )

        # Filtrer les lignes vides
        items = [i for i in items if i["offerText"]]
        total = len(items)
        if total == 0:
            raise RuntimeError("Aucun item valide après parsing Gemini")

        # Recalculer compteurs après filtre
        matches = sum(1 for i in items if i["status"] == "match")
        missing = sum(1 for i in items if i["status"] == "missing")
        unclear = sum(1 for i in items if i["status"] == "unclear")

        category_stats: dict[str, dict[str, Any]] = {}
        for item in items:
            cat = item["category"]
            if cat not in category_stats:
                category_stats[cat] = {
                    "description": cat,
                    "color": "#6366f1",
                    "total": 0,
                    "matches": 0,
                    "missing": 0,
                    "unclear": 0,
                    "match_percentage": 0.0,
                }
            category_stats[cat]["total"] += 1
            if item["status"] == "match":
                category_stats[cat]["matches"] += 1
            elif item["status"] == "missing":
                category_stats[cat]["missing"] += 1
            else:
                category_stats[cat]["unclear"] += 1

        for stats in category_stats.values():
            if stats["total"]:
                stats["match_percentage"] = (stats["matches"] / stats["total"]) * 100

        return {
            "items": items,
            "summary": {
                "totalItems": total,
                "matches": matches,
                "missing": missing,
                "unclear": unclear,
                "matchPercentage": matches / total if total else 0.0,
                "categoryStats": category_stats,
            },
        }

    def generate_interview_questions(
        self, cv_text: str, job_offer_text: str, num_questions: int = 10
    ) -> list[dict[str, str]]:
        prompt = f"""Tu es un expert recrutement. Génère exactement {num_questions} questions d'entretien.

CV (extrait):
\"\"\"{self._clip(cv_text, 8000)}\"\"\"

OFFRE (extrait):
\"\"\"{self._clip(job_offer_text, 8000)}\"\"\"

Retourne un JSON array:
[
  {{"text": "Question complète ?", "category": "Expérience|Compétences|Motivation|Problème|Spécifique"}}
]

Questions variées, spécifiques au profil et au poste. JSON uniquement."""

        try:
            raw = self._generate_json(prompt, temperature=0.4)
            questions = raw if isinstance(raw, list) else raw.get("questions", [])
            cleaned: list[dict[str, str]] = []
            for q in questions:
                if not isinstance(q, dict):
                    continue
                text = str(q.get("text") or "").strip()
                if not text:
                    continue
                cleaned.append(
                    {
                        "text": text,
                        "category": str(q.get("category") or "Général"),
                    }
                )
            if cleaned:
                return cleaned[:num_questions]
        except Exception as exc:
            print(f"Erreur génération questions: {exc}")

        return self._fallback_questions(num_questions)

    def analyze_interview_responses(
        self,
        questions: list[dict[str, str]],
        answers: list[dict[str, str]],
        cv_text: str,
        job_text: str,
    ) -> dict[str, Any]:
        qa_block = []
        for i, (question, answer) in enumerate(zip(questions, answers)):
            qa_block.append(
                f"Q{i+1} ({question.get('category', 'Général')}): {question.get('text', '')}\n"
                f"R: {answer.get('answer', 'Aucune réponse')}"
            )

        prompt = f"""Tu es coach entretien. Analyse les réponses.

CV: \"\"\"{self._clip(cv_text, 6000)}\"\"\"
OFFRE: \"\"\"{self._clip(job_text, 6000)}\"\"\"

ÉCHANGES:
{chr(10).join(qa_block)}

JSON uniquement:
{{
  "score_global": 7,
  "points_forts": ["..."],
  "points_amelioration": ["..."],
  "suggestions": [
    {{"titre": "...", "description": "...", "priorite": "haute|moyenne|basse"}}
  ],
  "conseils_specifiques": [
    {{"question": "...", "conseil": "..."}}
  ]
}}"""

        try:
            analysis = self._generate_json(prompt, temperature=0.3)
            if isinstance(analysis, dict):
                return {"success": True, "analysis": analysis}
        except Exception as exc:
            print(f"Erreur analyse entretien: {exc}")

        return self._fallback_analysis()

    @staticmethod
    def _fallback_questions(num_questions: int) -> list[dict[str, str]]:
        base = [
            {"text": "Pouvez-vous vous présenter et parler de votre parcours ?", "category": "Expérience"},
            {"text": "Quelles sont vos compétences techniques principales ?", "category": "Compétences"},
            {"text": "Pourquoi ce poste vous intéresse-t-il ?", "category": "Motivation"},
            {"text": "Décrivez une difficulté professionnelle et votre résolution.", "category": "Problème"},
            {"text": "Quels sont vos objectifs à moyen terme ?", "category": "Motivation"},
            {"text": "Comment gérez-vous le stress et les délais ?", "category": "Compétences"},
            {"text": "Parlez d’un projet dont vous êtes fier.", "category": "Expérience"},
            {"text": "Comment vous formez-vous en continu ?", "category": "Compétences"},
            {"text": "Quelle est votre approche du travail en équipe ?", "category": "Compétences"},
            {"text": "Avez-vous des questions sur le poste ?", "category": "Spécifique"},
        ]
        return base[:num_questions]

    @staticmethod
    def _fallback_analysis() -> dict[str, Any]:
        return {
            "success": True,
            "analysis": {
                "score_global": 6,
                "points_forts": ["Réponses structurées", "Expérience pertinente"],
                "points_amelioration": ["Préparation des exemples", "Concision"],
                "suggestions": [
                    {
                        "titre": "Préparez des exemples concrets",
                        "description": "Préparez 3-5 exemples STAR de vos réalisations",
                        "priorite": "haute",
                    },
                    {
                        "titre": "Améliorez la concision",
                        "description": "Gardez vos réponses entre 1 et 2 minutes",
                        "priorite": "moyenne",
                    },
                ],
                "conseils_specifiques": [],
            },
        }


# Instance partagée (évite de recréer le client)
ai_service = AIService()
