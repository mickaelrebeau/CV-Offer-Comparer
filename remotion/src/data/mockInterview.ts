export const interviewOffer =
  "Lead Frontend Vue 3 — équipe produit B2B SaaS. Maîtrise TypeScript, performance des listes longues, tests automatisés.";

export const interviewCv =
  "4 ans Vue 3 / TypeScript. Optimisation de rendu, virtualisation de listes, Vitest + Playwright, CI GitHub Actions.";

export const questions = [
  {
    category: 'technique',
    text: 'Votre CV mentionne Vue 3 et TypeScript. Comment gérez-vous le rendu d\'une liste de plusieurs milliers d\'éléments sans dégrader l\'interface ?',
  },
  {
    category: 'expérience',
    text: 'Décrivez un projet où vous avez amélioré les performances perçues côté utilisateur.',
  },
  {
    category: 'comportemental',
    text: 'Comment priorisez-vous les retours QA avant une mise en production ?',
  },
];

export const sampleAnswer =
  "J'utilise la virtualisation de liste avec des composants dédiés, le chargement différé des modules lourds et la mémoïsation via computed pour ne recalculer que les segments visibles.";

export const analysisResult = {
  score_global: 7.8,
  points_forts: [
    'Bonne articulation entre virtualisation et mémoïsation',
    'Exemples concrets alignés avec l\'offre Vue 3 / TypeScript',
  ],
  points_amelioration: [
    'Quantifier l\'impact performance (temps de rendu, mémoire)',
    'Mentionner les outils de profiling utilisés (Vue DevTools, Lighthouse)',
  ],
};
