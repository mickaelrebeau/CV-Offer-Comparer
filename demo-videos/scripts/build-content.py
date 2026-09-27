"""Génère assets/content.js : libellés réels de l'app (locales FR/EN) + données anonymisées.

Relancer après une modification des locales du frontend :
    python3 scripts/build-content.py
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCALES = ROOT.parent / "frontend" / "src" / "locales"
INPUTS = json.loads((ROOT / "data" / "inputs.json").read_text())

# Clés i18n de l'app utilisées dans les vidéos (valeurs copiées telles quelles)
KEYS = [
    "nav.dashboard", "nav.compare", "nav.simulator", "nav.coverLetter", "nav.profile", "nav.signOut",
    "common.pdf", "common.text", "common.copy",
    "cvInput.offerHeader", "cvInput.cvHeader",
    "compare.label", "compare.title", "compare.description",
    "comparison.run", "comparison.report", "comparison.confidence", "comparison.cvExcerpt", "comparison.rewrites",
    "comparison.stats.matches", "comparison.stats.missing", "comparison.stats.unclear", "comparison.stats.score",
    "comparison.status.match", "comparison.status.missing", "comparison.status.partial",
    "interview.label", "interview.title", "interview.description", "interview.generate", "interview.changeTopic",
    "interview.start", "interview.estimate", "interview.questionOf", "interview.answerLabel", "interview.next",
    "interview.previous", "interview.pause", "interview.progress", "interview.questionN", "interview.getReport",
    "results.label", "results.title", "results.description", "results.globalScore", "results.questions",
    "results.duration", "results.strengths", "results.improvements", "results.score.good",
    "coverLetter.label", "coverLetter.title", "coverLetter.description", "coverLetter.cvFile",
    "coverLetter.options.header", "coverLetter.options.tone", "coverLetter.options.length", "coverLetter.options.language",
    "coverLetter.tones.professional", "coverLetter.tones.warm", "coverLetter.tones.confident", "coverLetter.tones.formal",
    "coverLetter.lengths.short", "coverLetter.lengths.standard", "coverLetter.lengths.detailed",
    "coverLetter.languages.auto", "coverLetter.languages.fr", "coverLetter.languages.en",
    "coverLetter.run", "coverLetter.result", "coverLetter.copied", "coverLetter.reviewHint",
    "landing.hero.title", "landing.footer.slogan", "landing.nav.analyze",
    "dashboard.modules.compare.features", "dashboard.modules.interview.features", "dashboard.modules.coverLetter.features",
    "dashboard.modules.interview.cta", "dashboard.modules.coverLetter.cta",
]

# Messages de statut SSE du backend (backend/app/i18n.py)
BACKEND = {
    "fr": {
        "analysisStart": "Début de l'analyse…",
        "analysisGemini": "Analyse ATS par Gemini (extraction + matching)…",
        "analysisStreaming": "Exigences analysées : 10 — diffusion des résultats…",
        "letterStart": "Lecture du CV et de l'offre…",
        "letterGemini": "Rédaction de la lettre par Gemini…",
        "letterWriting": "Mise en forme de la lettre…",
    },
    "en": {
        "analysisStart": "Starting the analysis…",
        "analysisGemini": "ATS analysis by Gemini (extraction + matching)…",
        "analysisStreaming": "Requirements analyzed: 10 — streaming results…",
        "letterStart": "Reading the resume and the job offer…",
        "letterGemini": "Gemini is writing the letter…",
        "letterWriting": "Formatting the letter…",
    },
}

# Accroche de l'entretien : début de dashboard.modules.interview.description
HOOK_INTERVIEW = {"fr": "Préparez l'étape décisive.", "en": "Prepare for the decisive step."}

# Résultats calculés par l'app sur le couple anonymisé (capture/fr/*.png), traduits pour l'EN
DATA = {
    "fr": {
        "items": [
            ["compétences techniques", 95, "Python et API REST", "Python, API REST — freelance et éditeur SaaS", "match", None],
            ["compétences techniques", 92, "Intégration de LLM (IA générative)", "Intégration de LLM en production (freelance, éditeur SaaS)", "match", None],
            ["compétences techniques", 86, "NestJS / Node.js", "NestJS et Redis — incubateur tech", "match", None],
            ["expérience et niveau", 90, "Expérience significative en Full Stack", "Développeur Full Stack depuis 2023", "match", None],
            ["formation et certification", 88, "Formation Bac+3 à Bac+5", "Titre Concepteur développeur d'applications", "match", None],
            ["compétences techniques", 64, "React et TypeScript", "React (incubateur tech) ; Vue.js au quotidien", "unclear", "Mettez en avant vos projets React et l'usage de TypeScript"],
            ["compétences techniques", 58, "Cloud Azure", "AWS en production", "unclear", "Précisez les services AWS utilisés et leurs équivalents Azure"],
            ["compétences techniques", 90, "Next.js", None, "missing", "Ajoutez un projet Next.js, même personnel"],
            ["compétences techniques", 87, "LangChain, RAG et bases vectorielles", None, "missing", "Décrivez un pipeline RAG ou un assistant IA que vous avez construit"],
            ["compétences techniques", 80, "Docker et CI/CD", None, "missing", "Mentionnez la conteneurisation et vos pipelines CI/CD"],
        ],
        "questions": [
            ["Expérience", "Vous avez intégré des LLM en production : comment avez-vous maîtrisé les coûts et la qualité des réponses ?"],
            ["Spécifique", "Comment concevriez-vous un assistant RH basé sur le RAG à partir de documents internes ?"],
            ["Compétences", "Votre expérience cloud est sur AWS : comment aborderiez-vous une migration vers Azure ?"],
            ["Compétences", "Décrivez une API REST que vous avez rendue plus robuste. Quelles mesures avez-vous prises ?"],
            ["Motivation", "Pourquoi rejoindre un éditeur SaaS du secteur public ?"],
        ],
        "answer": "Sur un assistant IA en production, j'ai mis en place un cache des réponses et un jeu d'évaluation : –35 % de coûts, et un suivi de la qualité à chaque livraison.",
        "strengths": ["Expérience concrète des LLM en production", "Réponses structurées et chiffrées", "Bonne maîtrise des API REST"],
        "improvements": ["Préciser l'expérience RAG / bases vectorielles", "Illustrer la montée en compétence sur Azure"],
        "letter": {
            "subject": "Objet : candidature au poste de Développeur Full Stack IA",
            "greeting": "Madame, Monsieur,",
            "opening": "Développeur Full Stack, j'intègre depuis deux ans des modèles d'IA générative dans des applications en production. Contribuer à des assistants IA qui simplifient le quotidien des services RH du secteur public est exactement le défi que je recherche.",
            "body": [
                "En freelance puis chez un éditeur SaaS, j'ai conçu des API REST en Python et intégré des LLM dans des produits utilisés au quotidien, en veillant à la qualité des réponses, à la performance et à la maîtrise des coûts.",
                "Au sein d'un incubateur tech, j'ai développé l'authentification et la gestion des profils d'une plateforme en micro-services avec NestJS, React et Redis. Habitué à AWS, je suis prêt à monter rapidement en compétence sur Azure, LangChain et le RAG.",
            ],
            "closing": "Je serais heureux d'échanger avec vous sur la façon dont je pourrais contribuer à vos produits IA lors d'un entretien.",
            "signoff": "Je vous prie d'agréer, Madame, Monsieur, l'expression de mes salutations distinguées.",
            "signature": "Alex Moreau",
        },
    },
    "en": {
        "items": [
            ["technical skills", 95, "Python and REST APIs", "Python, REST APIs — freelance and SaaS publisher", "match", None],
            ["technical skills", 92, "LLM integration (generative AI)", "LLMs integrated in production (freelance, SaaS publisher)", "match", None],
            ["technical skills", 86, "NestJS / Node.js", "NestJS and Redis — tech incubator", "match", None],
            ["experience and seniority", 90, "Significant Full Stack experience", "Full Stack developer since 2023", "match", None],
            ["education and certification", 88, "Bachelor's to master's degree", "Application Designer & Developer degree", "match", None],
            ["technical skills", 64, "React and TypeScript", "React (tech incubator); Vue.js day to day", "unclear", "Highlight your React projects and your use of TypeScript"],
            ["technical skills", 58, "Azure cloud", "AWS in production", "unclear", "Name the AWS services you used and their Azure equivalents"],
            ["technical skills", 90, "Next.js", None, "missing", "Add a Next.js project, even a personal one"],
            ["technical skills", 87, "LangChain, RAG and vector databases", None, "missing", "Describe a RAG pipeline or an AI assistant you have built"],
            ["technical skills", 80, "Docker and CI/CD", None, "missing", "Mention containerization and your CI/CD pipelines"],
        ],
        "questions": [
            ["Experience", "You have integrated LLMs in production: how did you keep costs and answer quality under control?"],
            ["Specific", "How would you design an HR assistant based on RAG from internal documents?"],
            ["Skills", "Your cloud experience is on AWS: how would you approach a migration to Azure?"],
            ["Skills", "Describe a REST API you made more robust. What measures did you take?"],
            ["Motivation", "Why join a SaaS publisher for the public sector?"],
        ],
        "answer": "On a production AI assistant, I added response caching and an evaluation set: 35% lower costs, and quality tracked on every release.",
        "strengths": ["Hands-on experience with LLMs in production", "Structured answers backed by figures", "Solid command of REST APIs"],
        "improvements": ["Detail your RAG / vector database experience", "Show how you would ramp up on Azure"],
        "letter": {
            "subject": "Subject: application for the Full Stack AI Developer position",
            "greeting": "Dear Hiring Manager,",
            "opening": "As a Full Stack developer, I have spent the last two years integrating generative AI models into production applications. Contributing to AI assistants that make HR teams' daily work easier in the public sector is exactly the challenge I am looking for.",
            "body": [
                "As a freelancer and then at a SaaS publisher, I designed REST APIs in Python and integrated LLMs into products used every day, with close attention to answer quality, performance and cost control.",
                "At a tech incubator, I built the authentication and profile management of a microservices platform with NestJS, React and Redis. Used to AWS, I am ready to ramp up quickly on Azure, LangChain and RAG.",
            ],
            "closing": "I would be glad to discuss how I could contribute to your AI products in an interview.",
            "signoff": "Kind regards,",
            "signature": "Alex Moreau",
        },
    },
}


def get(d, key):
    for part in key.split("."):
        d = d[part]
    return d


out = {}
for lang in ("fr", "en"):
    catalog = json.loads((LOCALES / f"{lang}.json").read_text())
    out[lang] = {
        "ui": {key: get(catalog, key) for key in KEYS},
        "status": BACKEND[lang],
        "hookInterview": HOOK_INTERVIEW[lang],
        "email": "alex.moreau@example.com",
        "inputs": INPUTS[lang],
        **DATA[lang],
    }

js = (
    "// Généré par scripts/build-content.py — ne pas éditer à la main.\n"
    "// Libellés : frontend/src/locales/{fr,en}.json ; données : couple CV / offre anonymisé.\n"
    f"window.TALENTO_CONTENT = {json.dumps(out, ensure_ascii=False, indent=1)};\n"
)
(ROOT / "assets" / "content.js").write_text(js)
print("assets/content.js", len(js), "octets")
