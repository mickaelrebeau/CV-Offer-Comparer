import google.generativeai as genai
import re
from typing import List, Dict, Any
from app.config import settings

class AIService:
    def __init__(self):
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
    
    def extract_skills(self, text: str, job_category: str = None) -> List[str]:
        """Extrait les compétences d'un texte en utilisant l'IA"""
        
        # Déterminer le contexte métier
        job_context = self._get_job_context(job_category)
        
        prompt = f"""
        Analyse ce texte et extrait les compétences, expériences et exigences mentionnées.
        
        Contexte métier: {job_context}
        
        Sois très spécifique et détaillé. Inclus:
        - Les langues avec leur niveau (français, anglais, etc.)
        - Les compétences techniques spécifiques au métier
        - Les outils et logiciels utilisés
        - Les soft skills (communication, leadership, etc.)
        - Les expériences et niveaux (senior, junior, expert)
        - Les certifications et formations
        - Les domaines d'expertise
        
        Retourne uniquement une liste de compétences, une par ligne.
        
        Texte: {text[:2000]}
        
        Exemple de format attendu:
        - Français courant
        - Anglais B2
        - [Compétence technique spécifique]
        - [Outil/logiciel]
        - [Soft skill]
        - [Certification]
        """
        
        try:
            print(f"Extraction des compétences pour le métier: {job_category or 'général'}")
            response = self.model.generate_content(prompt)
            print(f"Réponse de l'IA: {response.text}")
            
            skills = [skill.strip() for skill in response.text.split('\n') if skill.strip()]
            cleaned_skills = []
            
            for skill in skills:
                cleaned = skill.lstrip('- ').lstrip('• ').lstrip('* ').strip()
                if cleaned and len(cleaned) > 2:
                    cleaned_skills.append(cleaned)
            
            print(f"Compétences extraites: {cleaned_skills}")
            return cleaned_skills
            
        except Exception as e:
            print(f"Erreur lors de l'extraction des compétences: {e}")
            return self._extract_basic_skills(text, job_category)
    
    def _get_job_context(self, job_category: str = None) -> str:
        """Retourne le contexte métier pour l'extraction"""
        contexts = {
            "developpeur": "Développement informatique, programmation, technologies web et mobiles",
            "designer": "Design graphique, UX/UI, création visuelle, outils de design",
            "marketing": "Marketing digital, communication, stratégie commerciale, analytics",
            "vente": "Commercial, vente, relation client, négociation",
            "finance": "Finance, comptabilité, gestion, analyse financière",
            "rh": "Ressources humaines, recrutement, formation, gestion des talents",
            "logistique": "Logistique, transport, supply chain, gestion des stocks",
            "sante": "Santé, médical, soins, paramédical",
            "education": "Enseignement, formation, pédagogie, éducation",
            "consultant": "Conseil, stratégie, analyse, accompagnement",
            "manager": "Management, leadership, gestion d'équipe, pilotage de projet",
            "ingenieur": "Ingénierie, technique, innovation, développement de produits"
        }
        
        if job_category and job_category.lower() in contexts:
            return contexts[job_category.lower()]
        
        return "Métier général - compétences transversales et spécifiques"
    
    def _extract_basic_skills(self, text: str, job_category: str = None) -> List[str]:
        """Extraction basique de compétences basée sur des mots-clés"""
        
        # Mots-clés génériques
        generic_keywords = [
            "français", "anglais", "espagnol", "allemand", "chinois",
            "communication", "leadership", "travail d'équipe", "autonomie",
            "créativité", "organisation", "rigueur", "adaptabilité",
            "senior", "junior", "expert", "débutant", "confirmé",
            "bilingue", "courant", "notions", "fluent"
        ]
        
        # Mots-clés par métier
        job_keywords = {
            "developpeur": [
                "javascript", "python", "java", "react", "vue", "angular",
                "node.js", "php", "sql", "mongodb", "aws", "docker",
                "git", "agile", "scrum", "api", "html", "css"
            ],
            "designer": [
                "photoshop", "illustrator", "figma", "sketch", "invision",
                "ux", "ui", "design", "typographie", "couleur", "layout",
                "wireframe", "prototype", "branding", "identité visuelle"
            ],
            "marketing": [
                "google ads", "facebook ads", "seo", "sem", "analytics",
                "emailing", "social media", "content marketing", "crm",
                "conversion", "acquisition", "retention", "roi"
            ],
            "vente": [
                "prospection", "négociation", "relation client", "crm",
                "objectifs", "quota", "pipeline", "closing", "présentation",
                "argumentaire", "fidélisation", "cross-selling"
            ],
            "finance": [
                "comptabilité", "analyse financière", "budget", "trésorerie",
                "excel", "sap", "sage", "audit", "contrôle de gestion",
                "reporting", "consolidation", "tableaux de bord"
            ],
            "rh": [
                "recrutement", "formation", "gestion des talents", "paie",
                "évaluation", "entretien", "onboarding", "planning",
                "convention collective", "droit social", "sirh"
            ]
        }
        
        found_skills = []
        text_lower = text.lower()
        
        # Chercher les mots-clés génériques
        for keyword in generic_keywords:
            if keyword.lower() in text_lower:
                found_skills.append(keyword)
        
        # Chercher les mots-clés spécifiques au métier
        if job_category and job_category.lower() in job_keywords:
            for keyword in job_keywords[job_category.lower()]:
                if keyword.lower() in text_lower:
                    found_skills.append(keyword)
        
        print(f"Compétences basiques trouvées: {found_skills}")
        return found_skills
    
    def compare_semantic(self, offer_skill: str, cv_skill: str) -> float:
        """Compare deux compétences sémantiquement"""
        
        # Nettoyer et normaliser les textes
        offer_clean = offer_skill.lower().strip()
        cv_clean = cv_skill.lower().strip()
        
        # Vérifications basiques
        if offer_clean == cv_clean:
            return 1.0
        
        if offer_clean in cv_clean or cv_clean in offer_clean:
            return 0.9
        
        # Vérifier les mots-clés communs
        offer_words = set(offer_clean.split())
        cv_words = set(cv_clean.split())
        common_words = offer_words.intersection(cv_words)
        
        if len(common_words) > 0:
            total_words = len(offer_words.union(cv_words))
            similarity = len(common_words) / total_words
            if similarity > 0.3:
                return max(similarity, 0.6)
        
        # Vérifier les synonymes
        synonyms = self._get_synonyms()
        for key, syn_list in synonyms.items():
            if key in offer_clean or any(syn in offer_clean for syn in syn_list):
                if key in cv_clean or any(syn in cv_clean for syn in syn_list):
                    return 0.8
        
        # Utiliser l'IA pour une comparaison plus fine
        prompt = f"""
        Compare ces deux compétences et donne un score de similarité entre 0 et 1.
        Réponds uniquement avec le nombre (ex: 0.85).
        
        Compétence de l'offre: "{offer_skill}"
        Compétence du CV: "{cv_skill}"
        
        Considère:
        - Les synonymes et variations
        - Les niveaux de compétence (débutant/expert)
        - Les technologies similaires
        - Les domaines connexes
        """
        
        try:
            response = self.model.generate_content(prompt)
            score_text = response.text.strip()
            score_match = re.search(r'0\.\d+', score_text)
            if score_match:
                score = float(score_match.group())
                return min(score * 1.2, 1.0)
            else:
                return self._basic_similarity(offer_skill, cv_skill)
        except Exception:
            return self._basic_similarity(offer_skill, cv_skill)
    
    def _get_synonyms(self) -> Dict[str, List[str]]:
        """Retourne le dictionnaire de synonymes"""
        return {
            'français': ['francais', 'francophone', 'bilingue'],
            'anglais': ['english', 'anglophone'],
            'espagnol': ['espagnol', 'espagnolophone'],
            'allemand': ['allemand', 'allemandophone'],
            'chinois': ['chinois', 'chinoisophone'],
            'japonais': ['japonais', 'japonaisophone'],
            'portugais': ['portugais', 'portugaisophone'],
            'italien': ['italien', 'italienophone'],
            'arabe': ['arabe', 'arabeophone'],
            'linux': ['linux', 'linux-based', 'debian', 'ubuntu', 'fedora', 'arch', 'mint'],
            'windows': ['windows', 'windows-based'],
            'macos': ['macos', 'mac-based'],
            'ios': ['ios', 'apple-based'],
            'android': ['android', 'google-based'],
            'javascript': ['js', 'ecmascript', 'es6', 'es7', 'es8', 'es9', 'es10', 'es11', 'es12', 'es13', 'es14', 'es15', 'es16', 'es17', 'es18', 'es19', 'es20'],
            'python': ['py', 'python3', 'python2', 'python3.10', 'python3.11', 'python3.12', 'python3.13', 'python3.14', 'python3.15', 'python3.16', 'python3.17', 'python3.18', 'python3.19', 'python3.20'],
            'react': ['reactjs', 'react.js'],
            'react-native': ['react-native', 'react-native-web', 'react-native-windows', 'react-native-macos', 'react-native-ios', 'react-native-android'],
            'vue': ['vuejs', 'vue.js', 'vue-native'],
            'node': ['nodejs', 'node.js'],
            'aws': ['amazon web services', 'aws lambda', 'aws ec2', 'aws s3', 'aws rds', 'aws redshift', 'aws aurora', 'aws aurora mysql', 'aws aurora postgresql', 'aws aurora mariadb', 'aws aurora mssql', 'aws aurora oracle', 'aws aurora sqlserver', 'aws aurora mysql', 'aws aurora postgresql', 'aws aurora mariadb', 'aws aurora mssql', 'aws aurora oracle', 'aws aurora sqlserver'],
            'docker': ['containerization'],
            'git': ['version control'],
            'sql': ['database', 'mysql', 'postgresql'],
            'html': ['hypertext markup language'],
            'css': ['cascading style sheets'],
            'api': ['rest', 'graphql'],
            'agile': ['scrum', 'kanban'],
            'devops': ['ci/cd', 'continuous integration'],
            'fullstack': ['full stack', 'full-stack'],
            'frontend': ['front-end', 'client-side'],
            'backend': ['back-end', 'server-side'],
            'senior': ['expert', 'advanced'],
            'junior': ['beginner', 'entry-level'],
            'leadership': ['management', 'team lead'],
            'communication': ['collaboration', 'teamwork'],
            'autonomie': ['autonomous', 'independent'],
            'créativité': ['creative', 'innovation'],
            'photoshop': ['ps', 'photoshop'],
            'illustrator': ['ai', 'illustrator'],
            'figma': ['figma'],
            'sketch': ['sketch'],
            'invision': ['invision'],
            'ux': ['user experience'],
            'ui': ['user interface'],   
            'design': ['design', 'designing'],
            'typographie': ['typography', 'typographie'],
            'couleur': ['color', 'colors'],
            'layout': ['layout', 'layouts'],
            'wireframe': ['wireframe', 'wireframes'],
            'prototype': ['prototype', 'prototypes'],
            'branding': ['branding', 'brandings'],
        }
    
    def _basic_similarity(self, text1: str, text2: str) -> float:
        """Comparaison basique basée sur les mots communs"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def generate_suggestions(self, skill: str, status: str) -> List[str]:
        """Génère des suggestions pour améliorer une compétence"""
        if status not in ["missing", "unclear"]:
            return []
        
        prompt = f"""
        Pour cette exigence: "{skill}"
        Donne 2-3 suggestions concrètes pour l'améliorer dans un CV.
        Réponses courtes et pratiques.
        """
        
        try:
            response = self.model.generate_content(prompt)
            suggestions = [s.strip() for s in response.text.split('\n') if s.strip()]
            return suggestions
        except Exception:
            return [] 