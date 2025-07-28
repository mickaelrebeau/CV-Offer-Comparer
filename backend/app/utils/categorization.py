import re

def categorize_requirement(text: str) -> str:
    """Catégorise une exigence avec une logique améliorée"""
    text_lower = text.lower().strip()
    
    # Nettoyer le texte
    text_lower = re.sub(r'[^\w\s]', ' ', text_lower)
    text_lower = re.sub(r'\s+', ' ', text_lower)
    
    # Catégories avec mots-clés pondérés
    categories = {
        "langues": {
            "keywords": [
                "français", "anglais", "espagnol", "allemand", "chinois", "japonais", "portugais", "italien", "arabe",
                "bilingue", "courant", "notions", "fluent", "francophone", "anglophone", "espagnolophone",
                "niveau", "maîtrise", "parlé", "écrit", "compréhension", "expression"
            ],
            "weight": 10,
            "priority": 1
        },
        "soft skills": {
            "keywords": [
                "communication", "travail d'équipe", "leadership", "autonomie", "créativité", "organisation", 
                "rigueur", "adaptabilité", "collaboration", "management", "teamwork", "empathie", "écoute",
                "négociation", "persuasion", "résolution de problèmes", "pensée critique", "flexibilité",
                "gestion du stress", "motivation", "initiative", "curiosité", "apprentissage continu"
            ],
            "weight": 8,
            "priority": 2
        },
        "expérience et niveau": {
            "keywords": [
                "années", "expérience", "senior", "junior", "expert", "débutant", "confirmé", "advanced", 
                "entry-level", "intermédiaire", "chef de projet", "lead", "manager", "directeur",
                "plus de", "minimum", "au moins", "débutant", "expérimenté", "expertise"
            ],
            "weight": 7,
            "priority": 3
        },
        "formation et certification": {
            "keywords": [
                "diplôme", "bac", "master", "école", "université", "formation", "certification", 
                "licence", "doctorat", "bachelor", "phd", "mooc", "cours", "formation continue",
                "certifié", "accrédité", "reconnu", "officiel", "professionnel"
            ],
            "weight": 6,
            "priority": 4
        },
        "domaine métier": {
            "keywords": [
                "marketing", "vente", "finance", "rh", "logistique", "santé", "éducation", "consultant", 
                "manager", "ingénieur", "design", "développeur", "commercial", "comptabilité", "audit",
                "conseil", "stratégie", "analyse", "recherche", "innovation", "produit", "service"
            ],
            "weight": 5,
            "priority": 5
        },
        "compétences techniques": {
            "keywords": [
                # Langages de programmation
                "javascript", "python", "java", "c++", "c#", "php", "ruby", "go", "rust", "swift", "kotlin",
                "typescript", "coffeescript", "dart", "scala", "perl", "r", "matlab", "vba",
                
                # Frameworks et bibliothèques
                "react", "vue", "angular", "svelte", "ember", "backbone", "jquery", "bootstrap", "tailwind",
                "node.js", "express", "django", "flask", "spring", "laravel", "symfony", "asp.net",
                "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy", "matplotlib",
                
                # Bases de données
                "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "cassandra", "oracle",
                "sqlite", "mariadb", "neo4j", "dynamodb", "firebase", "supabase",
                
                # Cloud et DevOps
                "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "gitlab", "github", "bitbucket",
                "terraform", "ansible", "chef", "puppet", "vagrant", "virtualbox", "vmware",
                
                # Outils de développement
                "git", "svn", "mercurial", "vscode", "intellij", "eclipse", "vim", "emacs", "sublime",
                "webpack", "babel", "eslint", "prettier", "jest", "mocha", "cypress", "selenium",
                
                # Protocoles et APIs
                "api", "rest", "graphql", "soap", "grpc", "websocket", "http", "https", "tcp", "udp",
                
                # Langages de balisage et styles
                "html", "css", "xml", "json", "yaml", "toml", "markdown", "sass", "less", "stylus",
                
                # Outils de design
                "photoshop", "illustrator", "figma", "sketch", "invision", "adobe xd", "balsamiq",
                "canva", "gimp", "affinity", "procreate", "blender", "cinema 4d",
                
                # Outils métier
                "excel", "sap", "sage", "crm", "salesforce", "hubspot", "zendesk", "jira", "confluence",
                "trello", "asana", "monday", "notion", "slack", "teams", "zoom", "webex",
                
                # Analytics et marketing
                "google analytics", "mixpanel", "amplitude", "hotjar", "optimizely", "google ads",
                "facebook ads", "linkedin ads", "seo", "sem", "emailing", "automation",
                
                # Mots génériques techniques
                "programmation", "développement", "coding", "scripting", "debugging", "testing",
                "architecture", "design pattern", "algorithm", "data structure", "optimization",
                "performance", "scalability", "security", "encryption", "authentication"
            ],
            "weight": 4,
            "priority": 6
        }
    }
    
    # Calculer le score pour chaque catégorie
    category_scores = {}
    
    for category, config in categories.items():
        score = 0
        matched_keywords = []
        
        for keyword in config["keywords"]:
            if keyword in text_lower:
                # Score basé sur la longueur du mot-clé (plus spécifique = plus de points)
                keyword_score = len(keyword) * config["weight"]
                score += keyword_score
                matched_keywords.append(keyword)
        
        if score > 0:
            category_scores[category] = {
                "score": score,
                "priority": config["priority"],
                "matched_keywords": matched_keywords
            }
    
    # Si aucune catégorie trouvée, essayer une détection basée sur le contexte
    if not category_scores:
        return _categorize_by_context(text_lower)
    
    # Trouver la meilleure catégorie (score le plus élevé, puis priorité la plus élevée)
    best_category = max(category_scores.items(), 
                       key=lambda x: (x[1]["score"], -x[1]["priority"]))
    
    return best_category[0]

def _categorize_by_context(text: str) -> str:
    """Catégorise par contexte quand aucun mot-clé n'est trouvé"""
    
    # Détection basée sur les patterns
    patterns = {
        "langues": [
            r"\b[a-z]{2,}\s+(courant|fluent|notions|bilingue)\b",
            r"\b(courant|fluent|notions|bilingue)\s+en\s+[a-z]{2,}\b"
        ],
        "expérience et niveau": [
            r"\b\d+\s+ans?\b",
            r"\b(senior|junior|expert|débutant|confirmé)\b",
            r"\b(plus de|au moins|minimum)\s+\d+\b"
        ],
        "formation et certification": [
            r"\b(bac|master|licence|doctorat|phd)\b",
            r"\b(certifié|accrédité|formation)\b"
        ],
        "soft skills": [
            r"\b(communication|leadership|autonomie|créativité|organisation)\b",
            r"\b(travail d'équipe|collaboration|management)\b"
        ]
    }
    
    import re
    for category, pattern_list in patterns.items():
        for pattern in pattern_list:
            if re.search(pattern, text):
                return category
    
    # Détection basée sur la structure du texte
    words = text.split()
    
    # Si le texte contient des mots courts (probablement des langues)
    if len(words) <= 3 and all(len(word) <= 8 for word in words):
        return "langues"
    
    # Si le texte contient des mots liés à la personnalité
    personality_words = ["autonomie", "créativité", "organisation", "adaptabilité", "rigueur"]
    if any(word in text for word in personality_words):
        return "soft skills"
    
    # Si le texte contient des mots techniques
    tech_words = ["développement", "programmation", "technologie", "système", "application"]
    if any(word in text for word in tech_words):
        return "compétences techniques"
    
    # Par défaut
    return "autres"

def get_category_description(category: str) -> str:
    """Retourne une description de la catégorie"""
    descriptions = {
        "langues": "Compétences linguistiques et maîtrise des langues étrangères",
        "soft skills": "Compétences comportementales et relationnelles",
        "expérience et niveau": "Niveau d'expérience et ancienneté professionnelle",
        "formation et certification": "Diplômes, formations et certifications",
        "domaine métier": "Domaines d'expertise et secteurs d'activité",
        "compétences techniques": "Technologies, outils et compétences techniques",
        "autres": "Autres types de compétences ou exigences"
    }
    return descriptions.get(category, "Catégorie non définie")

def get_category_color(category: str) -> str:
    """Retourne une couleur pour la catégorie"""
    colors = {
        "langues": "#3B82F6",  # Bleu
        "soft skills": "#10B981",  # Vert
        "expérience et niveau": "#F59E0B",  # Orange
        "formation et certification": "#8B5CF6",  # Violet
        "domaine métier": "#EF4444",  # Rouge
        "compétences techniques": "#6B7280",  # Gris
        "autres": "#9CA3AF"  # Gris clair
    }
    return colors.get(category, "#9CA3AF") 