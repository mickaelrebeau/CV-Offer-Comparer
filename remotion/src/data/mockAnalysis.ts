export const offerSnippet =
  "Développeur·se Full Stack — Vue 3, TypeScript, Docker\n\nMissions : concevoir des interfaces réactives, maintenir une couverture de tests Vitest, conteneuriser les services avec Docker et GitHub Actions.\n\nProfil : 3 ans d'expérience minimum, anglais professionnel.";

export const cvSnippet =
  "Mickael Rébeau — Développeur Frontend\n\n• Vue 3 / Composition API, TypeScript (4 ans)\n• Tests unitaires avec Vitest et Playwright\n• CI/CD GitHub Actions, déploiement Railway\n• Anglais courant (C1)";

export const summaryStats = [
  { label: 'Correspondances', value: '12', color: 'text-emerald-500' },
  { label: 'Manquants', value: '3', color: 'text-rose-500' },
  { label: 'À préciser', value: '2', color: 'text-amber-500' },
  { label: 'Score ATS', value: '88%', color: 'text-ink' },
];

export const categories = [
  { label: 'Techniques', value: 92 },
  { label: 'Transverses', value: 85 },
  { label: 'Langues', value: 100 },
  { label: 'Expérience', value: 78 },
];

export const criteria = [
  {
    id: '1',
    category: 'Technique',
    offerText: 'TypeScript — 3 ans minimum',
    cvText: 'TypeScript (4 ans) — projets Vue 3 en production',
    status: 'match' as const,
    confidence: 0.94,
  },
  {
    id: '2',
    category: 'Technique',
    offerText: 'Vue 3 / Composition API',
    cvText: 'Interfaces réactives avec Composition API et Pinia',
    status: 'match' as const,
    confidence: 0.91,
  },
  {
    id: '3',
    category: 'Technique',
    offerText: 'Tests unitaires (Vitest)',
    cvText: 'Vitest et Playwright sur le frontend',
    status: 'unclear' as const,
    confidence: 0.72,
  },
  {
    id: '4',
    category: 'Technique',
    offerText: 'Docker / conteneurisation',
    cvText: undefined,
    status: 'missing' as const,
    confidence: 0.88,
    suggestions: [
      'Conteneurisation des services applicatifs avec Docker et déploiement continu via GitHub Actions, réduisant le temps de mise en production de 40 %.',
    ],
  },
  {
    id: '5',
    category: 'Langue',
    offerText: 'Anglais professionnel',
    cvText: 'Anglais courant (C1) — documentation et réunions',
    status: 'match' as const,
    confidence: 0.96,
  },
];

export const streamStatuses = [
  { id: '001', label: 'TypeScript', status: 'couvert' },
  { id: '002', label: 'Vue 3', status: 'couvert' },
  { id: '003', label: 'Tests unitaires', status: 'partiel' },
  { id: '004', label: 'Docker', status: 'manquant' },
];

export const progressMessages = [
  'Extraction des critères…',
  'Analyse du CV…',
  'Correspondance sémantique…',
  'Génération des reformulations…',
];
