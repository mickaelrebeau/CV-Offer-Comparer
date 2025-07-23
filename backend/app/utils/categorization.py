def categorize_requirement(text: str) -> str:
    """Catégorise une exigence"""
    text_lower = text.lower()
    
    categories = {
        "compétences techniques": [
            "programmation", "langage", "framework", "outil", "technologie",
            "javascript", "python", "java", "react", "vue", "angular",
            "node.js", "php", "sql", "mongodb", "aws", "docker",
            "git", "api", "html", "css", "photoshop", "illustrator",
            "figma", "sketch", "excel", "sap", "sage", "crm"
        ],
        "expérience": [
            "années", "expérience", "senior", "junior", "expert",
            "débutant", "confirmé", "expert", "advanced", "entry-level"
        ],
        "formation": [
            "diplôme", "bac", "master", "école", "université",
            "formation", "certification", "licence", "doctorat"
        ],
        "soft skills": [
            "communication", "travail d'équipe", "leadership", "autonomie",
            "créativité", "organisation", "rigueur", "adaptabilité",
            "collaboration", "management", "teamwork"
        ],
        "langues": [
            "français", "anglais", "espagnol", "allemand", "chinois",
            "bilingue", "courant", "notions", "fluent", "francophone",
            "anglophone"
        ],
        "domaine métier": [
            "marketing", "vente", "finance", "rh", "logistique",
            "santé", "éducation", "consultant", "manager", "ingénieur",
            "design", "développeur", "commercial", "comptabilité"
        ]
    }
    
    for category, keywords in categories.items():
        if any(keyword in text_lower for keyword in keywords):
            return category
    
    return "autres" 