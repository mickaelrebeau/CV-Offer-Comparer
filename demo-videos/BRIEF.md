---
workflow: general-video
flow: automation
storyboard: yes
message: "Talento est un vrai outil : on le voit analyser, entraîner et rédiger à partir d'un vrai CV et d'une vraie offre"
destination: website-embed
aspect: 1920x1080
language: fr, en
audience: candidats qui visitent la landing de Talento (section « Aperçu réel »)
length: 15s par vidéo, en boucle
angle: product-demo
---

## Intent

Régénérer les vidéos de démo produit de la landing Talento, en abandonnant Remotion
(dossier `/remotion`, à supprimer une fois les nouvelles vidéos en place) : tout est
produit avec HyperFrames.

Trois démos muettes, en boucle, qui montrent l'outil tel qu'il est (« Voici l'outil,
pas une maquette ») :

1. **Analyse** — saisie de l'offre et du CV, analyse en streaming, score ATS, critères
   couverts / partiels / manquants.
2. **Entretien** — questions générées, réponses minutées, rapport noté.
3. **Lettre de motivation** (nouvelle) — saisie offre + CV, choix du ton et de la longueur,
   lettre qui s'écrit paragraphe par paragraphe, copie / export.

Chaque démo existe en français et en anglais (6 vidéos).

## Assets

- ../cv.txt — CV source (données personnelles : ne jamais copier tel quel, ne jamais commiter). Base du profil anonymisé.
- ../offre.txt — offre source (entreprise nommée : ne jamais copier tel quel, ne jamais commiter). Base de l'offre anonymisée.
- ../frontend — l'app Vue elle-même : UI, tokens Tailwind (papier `#F1EEE7`, encre `#232323`), composants et libellés i18n FR/EN.

## Customizations

- Capture de l'app locale (pages comparateur, simulateur, lettre, en FR et EN) pour reconstruire les interfaces d'après l'UI réelle, en HTML, avec les vrais tokens et composants.
- Données anonymisées validées par l'utilisateur :
  - Offre : « Développeur·se Full Stack IA — éditeur de logiciels SaaS pour le secteur public » (assistants IA pour les services RH ; LLM, OpenAI, LangChain, RAG, API REST ; React, TypeScript, Next.js, Node.js, NestJS, Python, Azure, Docker, CI/CD ; Bac+3 à Bac+5). Sans Nexpublica, Wikit ni chiffres clients.
  - CV : « Alex Moreau — Développeur Full Stack » (freelance Vue.js / Python / AWS / LLM ; éditeur SaaS ; cabinet de conseil ; incubateur tech React / NestJS / Redis ; titre CDA, formation Développeur IA, BTS SIO ; anglais B2, espagnol bilingue). Sans coordonnées, date de naissance, réseaux, employeurs ni écoles nommés.
  - Résultats cohérents avec ce couple : score ATS ~70 % ; couverts Python, API REST, LLM, NestJS, expérience Full Stack, formation ; partiels React / TypeScript, Azure (AWS) ; manquants Next.js, LangChain / RAG, Docker.
- Sorties : `frontend/public/videos/{analyse,entretien,lettre}[-en].{mp4,webm}` + `-poster.webp`.
- Landing : 3ᵉ onglet « 03 · Lettre » ; `/en` affiche les versions anglaises ; libellés d'accessibilité mis à jour.

## Notes

- Format identique aux vidéos actuelles : 1920×1080, 30 fps, 15 s, muettes, boucle propre (dernière image ≈ première).
- Poids du dépôt : 18 fichiers vidéo/poster → débit modéré.
- Une composition par démo, la langue en variable (pas de code dupliqué FR/EN).
