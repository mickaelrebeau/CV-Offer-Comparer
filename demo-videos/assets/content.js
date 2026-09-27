// Généré par scripts/build-content.py — ne pas éditer à la main.
// Libellés : frontend/src/locales/{fr,en}.json ; données : couple CV / offre anonymisé.
window.TALENTO_CONTENT = {
 "fr": {
  "ui": {
   "nav.dashboard": "Tableau de bord",
   "nav.compare": "Comparateur",
   "nav.simulator": "Simulateur",
   "nav.coverLetter": "Lettre",
   "nav.profile": "Profil",
   "nav.signOut": "Déconnexion",
   "common.pdf": "PDF",
   "common.text": "Texte",
   "common.copy": "Copier",
   "cvInput.offerHeader": "01 · Offre d'emploi",
   "cvInput.cvHeader": "02 · Mon CV",
   "compare.label": "Comparateur",
   "compare.title": "CV ↔ Offre d'emploi",
   "compare.description": "Évaluez l'adéquation sémantique exacte entre votre profil et la fiche de poste.",
   "comparison.run": "Lancer la comparaison",
   "comparison.report": "Rapport détaillé par critère",
   "comparison.confidence": "conf. {value}",
   "comparison.cvExcerpt": "Extrait CV :",
   "comparison.rewrites": "Reformulations",
   "comparison.stats.matches": "Correspondances",
   "comparison.stats.missing": "Manquants",
   "comparison.stats.unclear": "À préciser",
   "comparison.stats.score": "Score ATS",
   "comparison.status.match": "couvert",
   "comparison.status.missing": "manquant",
   "comparison.status.partial": "partiel",
   "interview.label": "Simulateur",
   "interview.title": "Studio d'entraînement",
   "interview.description": "Préparez-vous aux questions ciblées générées d'après les zones d'attention de votre candidature.",
   "interview.generate": "Générer les questions",
   "interview.changeTopic": "Changer de sujet",
   "interview.start": "Lancer la simulation",
   "interview.estimate": "~{minutes} min · {count} questions",
   "interview.questionOf": "Question {current} / {total} · {category}",
   "interview.answerLabel": "Votre réponse",
   "interview.next": "Suivante",
   "interview.previous": "Précédente",
   "interview.pause": "Pause",
   "interview.progress": "Progression",
   "interview.questionN": "Question {n}",
   "interview.getReport": "Obtenir le rapport",
   "results.label": "Rapport",
   "results.title": "Résultats de la simulation",
   "results.description": "Évaluation synthétique et recommandations pour perfectionner vos arguments.",
   "results.globalScore": "Score global",
   "results.questions": "Questions",
   "results.duration": "Durée",
   "results.strengths": "Points forts",
   "results.improvements": "Pistes d'amélioration",
   "results.score.good": "Bonne prestation",
   "coverLetter.label": "Lettre de motivation",
   "coverLetter.title": "Une lettre qui répond à l’offre",
   "coverLetter.description": "Accroche, preuves tirées de votre CV et conclusion : une lettre ciblée, à relire et personnaliser avant l'envoi.",
   "coverLetter.cvFile": "Fichier",
   "coverLetter.options.header": "03 · Style de la lettre",
   "coverLetter.options.tone": "Ton",
   "coverLetter.options.length": "Longueur",
   "coverLetter.options.language": "Langue",
   "coverLetter.tones.professional": "Professionnel",
   "coverLetter.tones.warm": "Chaleureux",
   "coverLetter.tones.confident": "Affirmé",
   "coverLetter.tones.formal": "Formel",
   "coverLetter.lengths.short": "Concise",
   "coverLetter.lengths.standard": "Standard",
   "coverLetter.lengths.detailed": "Détaillée",
   "coverLetter.languages.auto": "Comme l'offre",
   "coverLetter.languages.fr": "Français",
   "coverLetter.languages.en": "Anglais",
   "coverLetter.run": "Générer la lettre",
   "coverLetter.result": "Votre lettre",
   "coverLetter.copied": "Lettre copiée",
   "coverLetter.reviewHint": "Relisez et ajustez la lettre avant de l'envoyer : vérifiez chaque fait cité.",
   "landing.hero.title": "L'analyse ATS que vous ne referez plus à la main.",
   "landing.footer.slogan": "Candidatez juste.",
   "landing.nav.analyze": "Analyser mon CV",
   "dashboard.modules.compare.features": [
    "Diagnostic d'écart sémantique",
    "Extraction des compétences requises",
    "Reformulations directes"
   ],
   "dashboard.modules.interview.features": [
    "Questions prédictives ciblées",
    "Chronomètre en direct",
    "Évaluation des réponses"
   ],
   "dashboard.modules.coverLetter.features": [
    "Accroche, corps et conclusion",
    "Ton et longueur au choix",
    "Copie et export .txt / .md"
   ],
   "dashboard.modules.interview.cta": "Démarrer la simulation",
   "dashboard.modules.coverLetter.cta": "Rédiger une lettre"
  },
  "status": {
   "analysisStart": "Début de l'analyse…",
   "analysisGemini": "Analyse ATS par Gemini (extraction + matching)…",
   "analysisStreaming": "Exigences analysées : 10 — diffusion des résultats…",
   "letterStart": "Lecture du CV et de l'offre…",
   "letterGemini": "Rédaction de la lettre par Gemini…",
   "letterWriting": "Mise en forme de la lettre…"
  },
  "hookInterview": "Préparez l'étape décisive.",
  "email": "alex.moreau@example.com",
  "inputs": {
   "offer": "Développeur·se Full Stack IA — éditeur de logiciels SaaS pour le secteur public\n\nNous développons des assistants IA qui simplifient le quotidien des services RH.\n\nMissions : concevoir des fonctionnalités Full Stack, intégrer des LLM (OpenAI, LangChain, RAG), développer des API REST robustes.\n\nStack : React, TypeScript, Next.js, Node.js, NestJS, Python, Azure, Docker, CI/CD.\n\nProfil : Bac+3 à Bac+5, expérience Full Stack, appétence pour l'IA, environnement SaaS apprécié.",
   "cv": "Alex Moreau — Développeur Full Stack\n\n• Freelance (2025 – aujourd'hui) : Vue.js, Python, AWS, LLM, PostgreSQL\n• Éditeur SaaS (2025) : applications web évolutives, Vue.js / Python / LLM\n• Cabinet de conseil (2024 – 2025) : missions Full Stack pour des clients\n• Incubateur tech (2023) : authentification et micro-services, React / NestJS / Redis\n\nFormation : titre Concepteur développeur d'applications, formation Développeur IA, BTS SIO\nLangues : anglais B2, espagnol bilingue"
  },
  "items": [
   [
    "compétences techniques",
    95,
    "Python et API REST",
    "Python, API REST — freelance et éditeur SaaS",
    "match",
    null
   ],
   [
    "compétences techniques",
    92,
    "Intégration de LLM (IA générative)",
    "Intégration de LLM en production (freelance, éditeur SaaS)",
    "match",
    null
   ],
   [
    "compétences techniques",
    86,
    "NestJS / Node.js",
    "NestJS et Redis — incubateur tech",
    "match",
    null
   ],
   [
    "expérience et niveau",
    90,
    "Expérience significative en Full Stack",
    "Développeur Full Stack depuis 2023",
    "match",
    null
   ],
   [
    "formation et certification",
    88,
    "Formation Bac+3 à Bac+5",
    "Titre Concepteur développeur d'applications",
    "match",
    null
   ],
   [
    "compétences techniques",
    64,
    "React et TypeScript",
    "React (incubateur tech) ; Vue.js au quotidien",
    "unclear",
    "Mettez en avant vos projets React et l'usage de TypeScript"
   ],
   [
    "compétences techniques",
    58,
    "Cloud Azure",
    "AWS en production",
    "unclear",
    "Précisez les services AWS utilisés et leurs équivalents Azure"
   ],
   [
    "compétences techniques",
    90,
    "Next.js",
    null,
    "missing",
    "Ajoutez un projet Next.js, même personnel"
   ],
   [
    "compétences techniques",
    87,
    "LangChain, RAG et bases vectorielles",
    null,
    "missing",
    "Décrivez un pipeline RAG ou un assistant IA que vous avez construit"
   ],
   [
    "compétences techniques",
    80,
    "Docker et CI/CD",
    null,
    "missing",
    "Mentionnez la conteneurisation et vos pipelines CI/CD"
   ]
  ],
  "questions": [
   [
    "Expérience",
    "Vous avez intégré des LLM en production : comment avez-vous maîtrisé les coûts et la qualité des réponses ?"
   ],
   [
    "Spécifique",
    "Comment concevriez-vous un assistant RH basé sur le RAG à partir de documents internes ?"
   ],
   [
    "Compétences",
    "Votre expérience cloud est sur AWS : comment aborderiez-vous une migration vers Azure ?"
   ],
   [
    "Compétences",
    "Décrivez une API REST que vous avez rendue plus robuste. Quelles mesures avez-vous prises ?"
   ],
   [
    "Motivation",
    "Pourquoi rejoindre un éditeur SaaS du secteur public ?"
   ]
  ],
  "answer": "Sur un assistant IA en production, j'ai mis en place un cache des réponses et un jeu d'évaluation : –35 % de coûts, et un suivi de la qualité à chaque livraison.",
  "strengths": [
   "Expérience concrète des LLM en production",
   "Réponses structurées et chiffrées",
   "Bonne maîtrise des API REST"
  ],
  "improvements": [
   "Préciser l'expérience RAG / bases vectorielles",
   "Illustrer la montée en compétence sur Azure"
  ],
  "letter": {
   "subject": "Objet : candidature au poste de Développeur Full Stack IA",
   "greeting": "Madame, Monsieur,",
   "opening": "Développeur Full Stack, j'intègre depuis deux ans des modèles d'IA générative dans des applications en production. Contribuer à des assistants IA qui simplifient le quotidien des services RH du secteur public est exactement le défi que je recherche.",
   "body": [
    "En freelance puis chez un éditeur SaaS, j'ai conçu des API REST en Python et intégré des LLM dans des produits utilisés au quotidien, en veillant à la qualité des réponses, à la performance et à la maîtrise des coûts.",
    "Au sein d'un incubateur tech, j'ai développé l'authentification et la gestion des profils d'une plateforme en micro-services avec NestJS, React et Redis. Habitué à AWS, je suis prêt à monter rapidement en compétence sur Azure, LangChain et le RAG."
   ],
   "closing": "Je serais heureux d'échanger avec vous sur la façon dont je pourrais contribuer à vos produits IA lors d'un entretien.",
   "signoff": "Je vous prie d'agréer, Madame, Monsieur, l'expression de mes salutations distinguées.",
   "signature": "Alex Moreau"
  }
 },
 "en": {
  "ui": {
   "nav.dashboard": "Dashboard",
   "nav.compare": "Comparison",
   "nav.simulator": "Simulator",
   "nav.coverLetter": "Letter",
   "nav.profile": "Profile",
   "nav.signOut": "Sign out",
   "common.pdf": "PDF",
   "common.text": "Text",
   "common.copy": "Copy",
   "cvInput.offerHeader": "01 · Job offer",
   "cvInput.cvHeader": "02 · My resume",
   "compare.label": "Comparison",
   "compare.title": "Resume ↔ Job offer",
   "compare.description": "Measure the exact semantic fit between your profile and the job description.",
   "comparison.run": "Run the comparison",
   "comparison.report": "Detailed report by criterion",
   "comparison.confidence": "conf. {value}",
   "comparison.cvExcerpt": "Resume excerpt:",
   "comparison.rewrites": "Suggested rewrites",
   "comparison.stats.matches": "Matches",
   "comparison.stats.missing": "Missing",
   "comparison.stats.unclear": "To clarify",
   "comparison.stats.score": "ATS score",
   "comparison.status.match": "covered",
   "comparison.status.missing": "missing",
   "comparison.status.partial": "partial",
   "interview.label": "Simulator",
   "interview.title": "Practice studio",
   "interview.description": "Get ready for targeted questions generated from the weak spots of your application.",
   "interview.generate": "Generate the questions",
   "interview.changeTopic": "Change topic",
   "interview.start": "Start the simulation",
   "interview.estimate": "~{minutes} min · {count} questions",
   "interview.questionOf": "Question {current} / {total} · {category}",
   "interview.answerLabel": "Your answer",
   "interview.next": "Next",
   "interview.previous": "Previous",
   "interview.pause": "Pause",
   "interview.progress": "Progress",
   "interview.questionN": "Question {n}",
   "interview.getReport": "Get the report",
   "results.label": "Report",
   "results.title": "Simulation results",
   "results.description": "Summary assessment and recommendations to sharpen your arguments.",
   "results.globalScore": "Overall score",
   "results.questions": "Questions",
   "results.duration": "Duration",
   "results.strengths": "Strengths",
   "results.improvements": "Areas for improvement",
   "results.score.good": "Good performance",
   "coverLetter.label": "Cover letter",
   "coverLetter.title": "A letter that answers the offer",
   "coverLetter.description": "A hook, evidence drawn from your resume and a closing: a targeted letter to review and personalize before sending it.",
   "coverLetter.cvFile": "File",
   "coverLetter.options.header": "03 · Letter style",
   "coverLetter.options.tone": "Tone",
   "coverLetter.options.length": "Length",
   "coverLetter.options.language": "Language",
   "coverLetter.tones.professional": "Professional",
   "coverLetter.tones.warm": "Warm",
   "coverLetter.tones.confident": "Confident",
   "coverLetter.tones.formal": "Formal",
   "coverLetter.lengths.short": "Concise",
   "coverLetter.lengths.standard": "Standard",
   "coverLetter.lengths.detailed": "Detailed",
   "coverLetter.languages.auto": "Same as the offer",
   "coverLetter.languages.fr": "French",
   "coverLetter.languages.en": "English",
   "coverLetter.run": "Generate the letter",
   "coverLetter.result": "Your letter",
   "coverLetter.copied": "Letter copied",
   "coverLetter.reviewHint": "Review and adjust the letter before sending it: check every fact it mentions.",
   "landing.hero.title": "The ATS analysis you will never do by hand again.",
   "landing.footer.slogan": "Apply with precision.",
   "landing.nav.analyze": "Analyze my resume",
   "dashboard.modules.compare.features": [
    "Semantic gap diagnosis",
    "Required skills extraction",
    "Ready-to-use rewrites"
   ],
   "dashboard.modules.interview.features": [
    "Targeted predictive questions",
    "Live timer",
    "Answer assessment"
   ],
   "dashboard.modules.coverLetter.features": [
    "Hook, body and closing",
    "Choose the tone and length",
    "Copy and export .txt / .md"
   ],
   "dashboard.modules.interview.cta": "Start the simulation",
   "dashboard.modules.coverLetter.cta": "Write a letter"
  },
  "status": {
   "analysisStart": "Starting the analysis…",
   "analysisGemini": "ATS analysis by Gemini (extraction + matching)…",
   "analysisStreaming": "Requirements analyzed: 10 — streaming results…",
   "letterStart": "Reading the resume and the job offer…",
   "letterGemini": "Gemini is writing the letter…",
   "letterWriting": "Formatting the letter…"
  },
  "hookInterview": "Prepare for the decisive step.",
  "email": "alex.moreau@example.com",
  "inputs": {
   "offer": "Full Stack AI Developer — SaaS software publisher for the public sector\n\nWe build AI assistants that make HR teams' daily work easier.\n\nMissions: design Full Stack features, integrate LLMs (OpenAI, LangChain, RAG), build robust REST APIs.\n\nStack: React, TypeScript, Next.js, Node.js, NestJS, Python, Azure, Docker, CI/CD.\n\nProfile: bachelor's to master's degree, Full Stack experience, keen interest in AI, SaaS background a plus.",
   "cv": "Alex Moreau — Full Stack Developer\n\n• Freelance (2025 – present): Vue.js, Python, AWS, LLM, PostgreSQL\n• SaaS publisher (2025): scalable web apps, Vue.js / Python / LLM\n• Consulting firm (2024 – 2025): Full Stack client engagements\n• Tech incubator (2023): authentication and microservices, React / NestJS / Redis\n\nEducation: Application Designer & Developer degree, AI Developer program, IT associate degree\nLanguages: English B2, Spanish bilingual"
  },
  "items": [
   [
    "technical skills",
    95,
    "Python and REST APIs",
    "Python, REST APIs — freelance and SaaS publisher",
    "match",
    null
   ],
   [
    "technical skills",
    92,
    "LLM integration (generative AI)",
    "LLMs integrated in production (freelance, SaaS publisher)",
    "match",
    null
   ],
   [
    "technical skills",
    86,
    "NestJS / Node.js",
    "NestJS and Redis — tech incubator",
    "match",
    null
   ],
   [
    "experience and seniority",
    90,
    "Significant Full Stack experience",
    "Full Stack developer since 2023",
    "match",
    null
   ],
   [
    "education and certification",
    88,
    "Bachelor's to master's degree",
    "Application Designer & Developer degree",
    "match",
    null
   ],
   [
    "technical skills",
    64,
    "React and TypeScript",
    "React (tech incubator); Vue.js day to day",
    "unclear",
    "Highlight your React projects and your use of TypeScript"
   ],
   [
    "technical skills",
    58,
    "Azure cloud",
    "AWS in production",
    "unclear",
    "Name the AWS services you used and their Azure equivalents"
   ],
   [
    "technical skills",
    90,
    "Next.js",
    null,
    "missing",
    "Add a Next.js project, even a personal one"
   ],
   [
    "technical skills",
    87,
    "LangChain, RAG and vector databases",
    null,
    "missing",
    "Describe a RAG pipeline or an AI assistant you have built"
   ],
   [
    "technical skills",
    80,
    "Docker and CI/CD",
    null,
    "missing",
    "Mention containerization and your CI/CD pipelines"
   ]
  ],
  "questions": [
   [
    "Experience",
    "You have integrated LLMs in production: how did you keep costs and answer quality under control?"
   ],
   [
    "Specific",
    "How would you design an HR assistant based on RAG from internal documents?"
   ],
   [
    "Skills",
    "Your cloud experience is on AWS: how would you approach a migration to Azure?"
   ],
   [
    "Skills",
    "Describe a REST API you made more robust. What measures did you take?"
   ],
   [
    "Motivation",
    "Why join a SaaS publisher for the public sector?"
   ]
  ],
  "answer": "On a production AI assistant, I added response caching and an evaluation set: 35% lower costs, and quality tracked on every release.",
  "strengths": [
   "Hands-on experience with LLMs in production",
   "Structured answers backed by figures",
   "Solid command of REST APIs"
  ],
  "improvements": [
   "Detail your RAG / vector database experience",
   "Show how you would ramp up on Azure"
  ],
  "letter": {
   "subject": "Subject: application for the Full Stack AI Developer position",
   "greeting": "Dear Hiring Manager,",
   "opening": "As a Full Stack developer, I have spent the last two years integrating generative AI models into production applications. Contributing to AI assistants that make HR teams' daily work easier in the public sector is exactly the challenge I am looking for.",
   "body": [
    "As a freelancer and then at a SaaS publisher, I designed REST APIs in Python and integrated LLMs into products used every day, with close attention to answer quality, performance and cost control.",
    "At a tech incubator, I built the authentication and profile management of a microservices platform with NestJS, React and Redis. Used to AWS, I am ready to ramp up quickly on Azure, LangChain and RAG."
   ],
   "closing": "I would be glad to discuss how I could contribute to your AI products in an interview.",
   "signoff": "Kind regards,",
   "signature": "Alex Moreau"
  }
 }
};
