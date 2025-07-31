import json
import google.generativeai as genai
import re
from typing import List, Dict, Any, Tuple
from app.config import settings
import torch
from transformers import AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import hashlib
import pickle
import os

class AIService:
    def __init__(self):
        # Configuration pour l'API Google (gardé pour l'extraction des compétences)
        try:
            genai.configure(api_key=settings.GOOGLE_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
            print("Modèle IA Google initialisé avec succès")
        except Exception as e:
            print(f"Erreur lors de l'initialisation du modèle IA: {e}")
            self.model = None
        
        # Configuration pour les modèles locaux - versions légères
        self._init_lightweight_models()
        
        # Cache pour les embeddings
        self.embedding_cache = {}
        self.cache_file = "embedding_cache.pkl"
        self._load_cache()
    
    def _init_lightweight_models(self):
        """Initialise les modèles locaux légers pour la comparaison sémantique"""
        try:
            # CamemBERT pour le français (modèle de base, plus léger)
            self.camembert_tokenizer = AutoTokenizer.from_pretrained('camembert-base')
            self.camembert_model = AutoModel.from_pretrained('camembert-base')
            
            # Sentence Transformer léger (all-MiniLM-L6-v2 au lieu de MPNet)
            self.sentence_transformer = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            
            # TF-IDF pour la comparaison lexicale (plus léger que les modèles neuronaux)
            self.tfidf_vectorizer = TfidfVectorizer(
                ngram_range=(1, 2),  # Réduit de (1,3) à (1,2)
                max_features=5000,    # Réduit de 10000 à 5000
                stop_words='english'
            )
            
            # Mode évaluation pour les modèles
            self.camembert_model.eval()
            
            # Optimisations mémoire
            if torch.cuda.is_available():
                # Utiliser CPU pour réduire la mémoire GPU
                self.camembert_model = self.camembert_model.cpu()
            
            print("Modèles légers chargés avec succès")
            
        except Exception as e:
            print(f"Erreur lors du chargement des modèles légers: {e}")
            self.camembert_tokenizer = None
            self.camembert_model = None
            self.sentence_transformer = None
            self.tfidf_vectorizer = None
    
    def _load_cache(self):
        """Charge le cache d'embeddings depuis le fichier"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'rb') as f:
                    self.embedding_cache = pickle.load(f)
                print(f"Cache chargé: {len(self.embedding_cache)} embeddings")
        except Exception as e:
            print(f"Erreur lors du chargement du cache: {e}")
            self.embedding_cache = {}
    
    def _save_cache(self):
        """Sauvegarde le cache d'embeddings"""
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(self.embedding_cache, f)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde du cache: {e}")
    
    def _get_cache_key(self, text: str, model_type: str) -> str:
        """Génère une clé de cache pour un texte et un type de modèle"""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        return f"{model_type}_{text_hash}"
    
    def _normalize_text(self, text: str) -> str:
        """Normalise le texte pour améliorer la comparaison"""
        # Nettoyage basique
        text = text.lower().strip()
        
        # Remplacement des caractères spéciaux
        text = re.sub(r'[^\w\s\-\.]', ' ', text)
        
        # Normalisation des espaces
        text = re.sub(r'\s+', ' ', text)
        
        # Normalisation des versions de technologies
        replacements = {
            'js': 'javascript',
            'reactjs': 'react',
            'vuejs': 'vue',
            'nodejs': 'node.js',
            'python3': 'python',
            'py': 'python',
            'aws lambda': 'aws',
            'amazon web services': 'aws',
            'docker container': 'docker',
            'kubernetes k8s': 'kubernetes',
            'git version control': 'git',
            'html5': 'html',
            'css3': 'css',
            'javascript es6': 'javascript',
            'javascript es7': 'javascript',
            'javascript es8': 'javascript',
            'javascript es9': 'javascript',
            'javascript es10': 'javascript',
            'javascript es11': 'javascript',
            'javascript es12': 'javascript',
            'javascript es13': 'javascript',
            'javascript es14': 'javascript',
            'javascript es15': 'javascript',
            'javascript es16': 'javascript',
            'javascript es17': 'javascript',
            'javascript es18': 'javascript',
            'javascript es19': 'javascript',
            'javascript es20': 'javascript',
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text.strip()
    
    def _get_embeddings_camembert(self, text: str) -> np.ndarray:
        """Génère les embeddings avec CamemBERT avec cache"""
        if not self.camembert_tokenizer or not self.camembert_model:
            return None
        
        # Normaliser le texte
        normalized_text = self._normalize_text(text)
        cache_key = self._get_cache_key(normalized_text, "camembert")
        
        # Vérifier le cache
        if cache_key in self.embedding_cache:
            return self.embedding_cache[cache_key]
        
        try:
            # Tokenisation avec padding et truncation réduite
            inputs = self.camembert_tokenizer(
                normalized_text, 
                return_tensors="pt", 
                padding=True, 
                truncation=True, 
                max_length=256  # Réduit de 512 à 256
            )
            
            # Génération des embeddings
            with torch.no_grad():
                outputs = self.camembert_model(**inputs)
                # Utiliser le dernier hidden state et faire une moyenne pondérée
                attention_mask = inputs['attention_mask']
                embeddings = (outputs.last_hidden_state * attention_mask.unsqueeze(-1)).sum(dim=1) / attention_mask.sum(dim=1, keepdim=True)
                result = embeddings.numpy()
                
                # Mettre en cache
                self.embedding_cache[cache_key] = result
                return result
                
        except Exception as e:
            print(f"Erreur lors de la génération d'embeddings CamemBERT: {e}")
            return None
    
    def _get_embeddings_sentence_transformer(self, text: str) -> np.ndarray:
        """Génère les embeddings avec Sentence Transformers avec cache"""
        if not self.sentence_transformer:
            return None
        
        # Normaliser le texte
        normalized_text = self._normalize_text(text)
        cache_key = self._get_cache_key(normalized_text, "sentence_transformer")
        
        # Vérifier le cache
        if cache_key in self.embedding_cache:
            return self.embedding_cache[cache_key]
        
        try:
            embeddings = self.sentence_transformer.encode([normalized_text])
            result = embeddings
            
            # Mettre en cache
            self.embedding_cache[cache_key] = result
            return result
            
        except Exception as e:
            print(f"Erreur lors de la génération d'embeddings Sentence Transformer: {e}")
            return None
    
    def _calculate_tfidf_similarity(self, text1: str, text2: str) -> float:
        """Calcule la similarité TF-IDF entre deux textes"""
        try:
            # Normaliser les textes
            norm_text1 = self._normalize_text(text1)
            norm_text2 = self._normalize_text(text2)
            
            # Créer la matrice TF-IDF
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([norm_text1, norm_text2])
            
            # Calculer la similarité cosinus
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(similarity)
            
        except Exception as e:
            print(f"Erreur lors du calcul TF-IDF: {e}")
            return 0.0
    
    def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calcule la similarité sémantique entre deux textes avec pondération optimisée"""
        
        similarities = []
        weights = []
        
        # 1. Similarité Sentence Transformer (plus léger, poids augmenté)
        emb1_st = self._get_embeddings_sentence_transformer(text1)
        emb2_st = self._get_embeddings_sentence_transformer(text2)
        
        if emb1_st is not None and emb2_st is not None:
            similarity = cosine_similarity(emb1_st, emb2_st)[0][0]
            similarities.append(float(similarity))
            weights.append(0.5)  # Augmenté de 0.3 à 0.5
        
        # 2. Similarité TF-IDF (léger, poids maintenu)
        tfidf_similarity = self._calculate_tfidf_similarity(text1, text2)
        similarities.append(tfidf_similarity)
        weights.append(0.3)  # Augmenté de 0.2 à 0.3
        
        # 3. Similarité basique (très léger, poids maintenu)
        basic_similarity = self._basic_similarity(text1, text2)
        similarities.append(basic_similarity)
        weights.append(0.2)  # Augmenté de 0.1 à 0.2
        
        # 4. CamemBERT (plus lourd, utilisé seulement si nécessaire)
        if len(similarities) < 2:  # Si pas assez de modèles disponibles
            emb1_camembert = self._get_embeddings_camembert(text1)
            emb2_camembert = self._get_embeddings_camembert(text2)
            
            if emb1_camembert is not None and emb2_camembert is not None:
                similarity = cosine_similarity(emb1_camembert, emb2_camembert)[0][0]
                similarities.append(float(similarity))
                weights.append(0.4)
        
        # Calculer la moyenne pondérée
        if similarities and weights:
            weighted_similarity = sum(s * w for s, w in zip(similarities, weights)) / sum(weights)
            return weighted_similarity
        
        # Fallback sur la comparaison basique
        return self._basic_similarity(text1, text2)
    
    def _enhance_similarity_with_context(self, similarity: float, text1: str, text2: str) -> float:
        """Améliore la similarité en tenant compte du contexte"""
        
        # Boost pour les correspondances exactes partielles
        norm_text1 = self._normalize_text(text1)
        norm_text2 = self._normalize_text(text2)
        
        # Vérifier les mots-clés communs
        words1 = set(norm_text1.split())
        words2 = set(norm_text2.split())
        common_words = words1.intersection(words2)
        
        if len(common_words) > 0:
            # Boost basé sur le nombre de mots communs
            word_overlap = len(common_words) / max(len(words1), len(words2))
            if word_overlap > 0.5:
                similarity = min(similarity * 1.2, 1.0)
            elif word_overlap > 0.3:
                similarity = min(similarity * 1.1, 1.0)
        
        # Boost pour les synonymes
        synonyms = self._get_synonyms()
        for key, syn_list in synonyms.items():
            if (key in norm_text1 or any(syn in norm_text1 for syn in syn_list)) and \
               (key in norm_text2 or any(syn in norm_text2 for syn in syn_list)):
                similarity = min(similarity * 1.15, 1.0)
                break
        
        # Boost pour les technologies liées
        tech_relations = self._get_tech_relations()
        for tech_group in tech_relations:
            if any(tech in norm_text1 for tech in tech_group) and \
               any(tech in norm_text2 for tech in tech_group):
                similarity = min(similarity * 1.1, 1.0)
                break
        
        return similarity
    
    def _get_tech_relations(self) -> List[List[str]]:
        """Retourne les relations entre technologies"""
        return [
            # Frontend
            ['react', 'vue', 'angular', 'svelte', 'frontend', 'javascript'],
            # Backend
            ['node.js', 'python', 'java', 'php', 'backend', 'api'],
            # Database
            ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'database'],
            # Cloud
            ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'cloud'],
            # DevOps
            ['git', 'ci/cd', 'jenkins', 'github', 'gitlab', 'devops'],
            # Mobile
            ['react native', 'flutter', 'ios', 'android', 'mobile'],
            # Design
            ['photoshop', 'illustrator', 'figma', 'sketch', 'design', 'ui', 'ux'],
            # Analytics
            ['google analytics', 'mixpanel', 'amplitude', 'analytics'],
            # Marketing
            ['seo', 'sem', 'google ads', 'facebook ads', 'marketing'],
        ]
    
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
        """Compare deux compétences sémantiquement avec les modèles locaux améliorés"""
        
        # Nettoyer et normaliser les textes
        offer_clean = offer_skill.lower().strip()
        cv_clean = cv_skill.lower().strip()
        
        # Vérifications basiques
        if offer_clean == cv_clean:
            return 1.0
        
        if offer_clean in cv_clean or cv_clean in offer_clean:
            return 0.95
        
        # Vérifier les mots-clés communs
        offer_words = set(offer_clean.split())
        cv_words = set(cv_clean.split())
        common_words = offer_words.intersection(cv_words)
        
        if len(common_words) > 0:
            total_words = len(offer_words.union(cv_words))
            similarity = len(common_words) / total_words
            if similarity > 0.3:
                return max(similarity, 0.7)
        
        # Vérifier les synonymes
        synonyms = self._get_synonyms()
        for key, syn_list in synonyms.items():
            if key in offer_clean or any(syn in offer_clean for syn in syn_list):
                if key in cv_clean or any(syn in cv_clean for syn in syn_list):
                    return 0.85
        
        # Utiliser les modèles locaux pour une comparaison sémantique
        semantic_similarity = self._calculate_semantic_similarity(offer_skill, cv_skill)
        
        # Améliorer avec le contexte
        enhanced_similarity = self._enhance_similarity_with_context(semantic_similarity, offer_skill, cv_skill)
        
        # Ajuster le score en fonction du contexte
        if enhanced_similarity > 0.8:
            return min(enhanced_similarity * 1.05, 1.0)
        elif enhanced_similarity > 0.6:
            return enhanced_similarity
        elif enhanced_similarity > 0.4:
            return enhanced_similarity * 0.9
        else:
            return enhanced_similarity * 0.8
    
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
        
        # Suggestions par défaut basées sur le type de compétence
        default_suggestions = self._get_default_suggestions(skill, status)
        
        prompt = f"""
        Pour cette exigence de l'offre d'emploi: "{skill}"
        
        Statut: {status}
        
        Génère 2-3 suggestions concrètes et pratiques pour améliorer cette compétence dans un CV.
        
        Format de réponse attendu:
        - Suggestion 1
        - Suggestion 2  
        - Suggestion 3
        
        Exemples de suggestions:
        - Ajouter des projets concrets utilisant cette compétence
        - Mentionner des certifications pertinentes
        - Décrire des expériences spécifiques
        - Inclure des outils ou technologies associés

        Exemple de réponse:
        - Ajouter des projets concrets utilisant cette compétence
        - Mentionner des certifications pertinentes
        - Décrire des expériences spécifiques
        - Inclure des outils ou technologies associés

        Réponds uniquement avec les suggestions, sans autre texte.
        Ne réponds pas avec des explications, des commentaires ou des phrases.
        Ne réponds pas avec des exemples de code ou des exemples de projets.
        Ne réponds pas avec des suggestions qui ne sont pas pertinentes pour améliorer la compétence.
        Ne réponds pas avec des suggestions qui ne sont pas concrètes et pratiques.
        """
        
        try:
            response = self.model.generate_content(prompt)
            
            # Nettoyer et parser la réponse
            suggestions = []
            lines = response.text.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if line and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                    # Enlever le préfixe et nettoyer
                    suggestion = line.lstrip('-•* ').strip()
                    if suggestion:
                        suggestions.append(suggestion)
                elif line and not line.startswith('Format') and not line.startswith('Exemples'):
                    # Si pas de préfixe mais ligne non vide
                    suggestions.append(line)
            
            # Si aucune suggestion générée par l'IA, utiliser les suggestions par défaut
            if not suggestions:
                suggestions = default_suggestions
            
            return suggestions[:3]  # Limiter à 3 suggestions max
            
        except Exception:
            return default_suggestions
    
    def _get_default_suggestions(self, skill: str, status: str) -> List[str]:
        """Génère des suggestions par défaut basées sur le type de compétence"""
        skill_lower = skill.lower()
        
        # Suggestions génériques
        generic_suggestions = [
            f"Ajouter des projets concrets utilisant {skill}",
            f"Mentionner des expériences professionnelles avec {skill}",
            f"Inclure des certifications ou formations en {skill}"
        ]
        
        # Suggestions spécifiques par type de compétence
        if any(tech in skill_lower for tech in ['python', 'javascript', 'java', 'c++', 'c#', 'php', 'ruby', 'go', 'rust']):
            return [
                f"Créer des projets GitHub utilisant {skill}",
                f"Mentionner des frameworks populaires avec {skill}",
                f"Ajouter des exemples de code {skill} dans votre portfolio"
            ]
        elif any(tech in skill_lower for tech in ['react', 'vue', 'angular', 'svelte']):
            return [
                f"Développer des applications web avec {skill}",
                f"Mentionner des projets frontend utilisant {skill}",
                f"Inclure des compétences en responsive design avec {skill}"
            ]
        elif any(tech in skill_lower for tech in ['docker', 'kubernetes', 'aws', 'azure', 'gcp']):
            return [
                f"Documenter des déploiements avec {skill}",
                f"Mentionner des projets cloud utilisant {skill}",
                f"Ajouter des certifications cloud avec {skill}"
            ]
        elif any(tech in skill_lower for tech in ['sql', 'mysql', 'postgresql', 'mongodb', 'redis']):
            return [
                f"Créer des bases de données avec {skill}",
                f"Mentionner des projets utilisant {skill}",
                f"Inclure des compétences en optimisation {skill}"
            ]
        elif any(tech in skill_lower for tech in ['git', 'github', 'gitlab', 'bitbucket']):
            return [
                f"Maintenir un portfolio GitHub avec {skill}",
                f"Mentionner des contributions open source",
                f"Documenter des workflows {skill} dans vos projets"
            ]
        elif any(tech in skill_lower for tech in ['agile', 'scrum', 'kanban']):
            return [
                f"Mentionner des expériences en méthodologie {skill}",
                f"Ajouter des certifications {skill}",
                f"Inclure des exemples de gestion de projet {skill}"
            ]
        elif any(lang in skill_lower for lang in ['français', 'anglais', 'espagnol', 'allemand', 'chinois']):
            return [
                f"Mentionner votre niveau de maîtrise en {skill}",
                f"Ajouter des expériences internationales avec {skill}",
                f"Inclure des certifications linguistiques en {skill}"
            ]
        else:
            return generic_suggestions 

    def generate_interview_questions(self, cv_text: str, job_offer_text: str, num_questions: int = 10) -> List[Dict[str, str]]:
        """
        Génère des questions d'entretien personnalisées basées sur le CV et l'offre d'emploi.
        
        Args:
            cv_text: Le texte du CV
            job_offer_text: Le texte de l'offre d'emploi
            num_questions: Nombre de questions à générer (défaut: 10)
            
        Returns:
            Liste de dictionnaires contenant les questions avec leurs catégories
        """
        try:
            # Extraire les compétences du CV et de l'offre
            cv_skills = self.extract_skills(cv_text)
            job_skills = self.extract_skills(job_offer_text)
            
            # Créer le prompt pour l'IA
            prompt = f"""
            En tant qu'expert en recrutement, génère exactement {num_questions} questions d'entretien pertinentes 
            pour un candidat basées sur les informations suivantes :
            
            CV du candidat (compétences identifiées) : {', '.join(cv_skills[:10])}
            Offre d'emploi (exigences) : {', '.join(job_skills[:10])}
            
            Génère des questions variées couvrant :
            - Expérience technique (30%)
            - Compétences comportementales (25%)
            - Motivation et projet professionnel (20%)
            - Résolution de problèmes (15%)
            - Questions spécifiques au poste (10%)
            
            IMPORTANT: Retourne UNIQUEMENT un JSON valide avec la structure suivante :
            [
                {{
                    "text": "Question complète",
                    "category": "Catégorie (Expérience/Compétences/Motivation/Problème/Spécifique)"
                }}
            ]
            
            Les questions doivent être :
            - Spécifiques au profil du candidat
            - Adaptées aux exigences du poste
            - Variées en difficulté
            - Professionnelles et pertinentes
            
            Assure-toi que le JSON est valide et contient exactement {num_questions} questions.
            """
            
            print("Envoi de la requête à l'IA...")
            
            # Générer les questions avec l'IA
            response = self.model.generate_content(prompt)
            
            # Parser la réponse JSON
            import json
            try:
                # Nettoyer la réponse pour extraire le JSON
                response_text = response.text.strip()
                
                # Chercher le JSON dans la réponse
                start_idx = response_text.find('[')
                end_idx = response_text.rfind(']') + 1
                
                if start_idx != -1 and end_idx > start_idx:
                    json_str = response_text[start_idx:end_idx]
                    questions = json.loads(json_str)
                    
                    if isinstance(questions, list) and len(questions) > 0:
                        print(f"Questions générées avec succès: {len(questions)}")
                        return questions[:num_questions]
                    else:
                        print("La réponse JSON ne contient pas de liste valide")
                else:
                    print("Aucun JSON trouvé dans la réponse")
                    
            except json.JSONDecodeError as e:
                print(f"Erreur de parsing JSON: {e}")
                print(f"Réponse problématique: {response.text}")
            
            # Si on arrive ici, utiliser les questions de fallback
            print("Utilisation des questions de fallback")
            return self._get_fallback_questions(cv_skills, job_skills, num_questions)
            
        except Exception as e:
            print(f"Erreur lors de la génération des questions d'entretien: {e}")
            # Retourner des questions de fallback en cas d'erreur
            return self._get_fallback_questions([], [], num_questions)

    def _get_fallback_questions(self, cv_skills: List[str], job_skills: List[str], num_questions: int) -> List[Dict[str, str]]:
        """
        Génère des questions de fallback en cas d'échec de l'IA.
        """
        print("Génération de questions de fallback...")
        
        # Questions génériques de base
        base_questions = [
            {
                "text": "Pouvez-vous vous présenter et me parler de votre parcours professionnel ?",
                "category": "Expérience"
            },
            {
                "text": "Quelles sont vos principales compétences techniques ?",
                "category": "Compétences"
            },
            {
                "text": "Pourquoi souhaitez-vous rejoindre notre entreprise ?",
                "category": "Motivation"
            },
            {
                "text": "Décrivez une situation difficile que vous avez rencontrée et comment vous l'avez résolue.",
                "category": "Problème"
            },
            {
                "text": "Quels sont vos objectifs professionnels à court et moyen terme ?",
                "category": "Motivation"
            },
            {
                "text": "Comment gérez-vous le stress et les délais serrés ?",
                "category": "Compétences"
            },
            {
                "text": "Pouvez-vous me donner un exemple de projet sur lequel vous êtes particulièrement fier ?",
                "category": "Expérience"
            },
            {
                "text": "Comment vous tenez-vous à jour dans votre domaine d'expertise ?",
                "category": "Compétences"
            },
            {
                "text": "Quelle est votre approche du travail en équipe ?",
                "category": "Compétences"
            },
            {
                "text": "Avez-vous des questions sur le poste ou l'entreprise ?",
                "category": "Spécifique"
            }
        ]
        
        # Personnaliser les questions avec les compétences extraites
        personalized_questions = []
        
        if cv_skills and job_skills:
            # Questions basées sur les compétences du CV
            if len(cv_skills) > 0:
                cv_skill = cv_skills[0]
                personalized_questions.append({
                    "text": f"Pouvez-vous me parler de votre expérience avec {cv_skill} ?",
                    "category": "Expérience"
                })
            
            # Questions basées sur les exigences du job
            if len(job_skills) > 0:
                job_skill = job_skills[0]
                personalized_questions.append({
                    "text": f"Quelle est votre expérience avec {job_skill} ?",
                    "category": "Compétences"
                })
        
        # Combiner les questions personnalisées avec les questions de base
        all_questions = personalized_questions + base_questions
        
        # Retourner le nombre demandé de questions
        return all_questions[:num_questions]

    def analyze_interview_responses(self, questions: List[Dict[str, str]], answers: List[Dict[str, str]], cv_text: str, job_text: str) -> Dict[str, Any]:
        """
        Analyse les réponses d'entretien et génère des suggestions personnalisées.
        
        Args:
            questions: Liste des questions posées
            answers: Liste des réponses données
            cv_text: Texte du CV
            job_text: Texte de l'offre d'emploi
            
        Returns:
            Dictionnaire contenant l'analyse et les suggestions
        """
        try:
            # Vérifier que le modèle est disponible
            if not hasattr(self, 'model') or self.model is None:
                print("Modèle IA non disponible, utilisation du fallback")
                return self._get_fallback_analysis()
            
            # Préparer les données pour l'analyse
            try:
                cv_skills = self.extract_skills(cv_text)[:10]  # Top 10 compétences du CV
                job_skills = self.extract_skills(job_text)[:10]  # Top 10 exigences du job
            except Exception as e:
                print(f"Erreur lors de l'extraction des compétences: {e}")
                cv_skills = ["Compétences techniques", "Expérience professionnelle"]
                job_skills = ["Compétences requises", "Exigences du poste"]
            
            # Construire le prompt pour l'analyse
            prompt = f"""
            En tant qu'expert en recrutement et coach en entretien, analyse les réponses d'entretien suivantes 
            et fournis des suggestions d'amélioration personnalisées.
            
            CONTEXTE:
            - CV du candidat (compétences principales): {', '.join(cv_skills)}
            - Offre d'emploi (exigences): {', '.join(job_skills)}
            
            QUESTIONS ET RÉPONSES:
            """
            
            for i, (question, answer) in enumerate(zip(questions, answers)):
                prompt += f"""
                Question {i+1} ({question.get('category', 'Général')}): {question.get('text', '')}
                Réponse: {answer.get('answer', 'Aucune réponse')}
                """
            
            prompt += """
            
            ANALYSE REQUISE:
            1. Évalue la qualité globale des réponses (1-10)
            2. Identifie les points forts du candidat
            3. Identifie les points d'amélioration
            4. Fournis 3-5 suggestions concrètes et personnalisées
            5. Donne des conseils spécifiques pour améliorer les réponses faibles
            
            Format de réponse JSON:
            {{
                "score_global": 7,
                "points_forts": ["Point fort 1", "Point fort 2"],
                "points_amelioration": ["Point d'amélioration 1", "Point d'amélioration 2"],
                "suggestions": [
                    {{
                        "titre": "Suggestion 1",
                        "description": "Description détaillée",
                        "priorite": "haute/moyenne/basse"
                    }}
                ],
                "conseils_specifiques": [
                    {{
                        "question": "Question concernée",
                        "conseil": "Conseil spécifique"
                    }}
                ]
            }}
            
            Assure-toi que le JSON est valide et contient exactement {num_questions} questions.
            Ne retourne pas de commentaire ou de texte superflu.
            Génère uniquement le JSON, rien d'autre.
            """
            
            # Générer l'analyse avec l'IA
            try:
                response = self.model.generate_content(prompt)
                
                if not response or not response.text:
                    print("Réponse vide de l'IA, utilisation du fallback")
                    return self._get_fallback_analysis()
                
                # Essayer de parser la réponse JSON
                response_text = response.text.strip()
                print(f"Réponse brute de l'IA (analyse): {response_text[:200]}...")
                
                # Chercher le JSON dans la réponse
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                
                if start_idx != -1 and end_idx > start_idx:
                    json_str = response_text[start_idx:end_idx]
                    analysis_result = json.loads(json_str)
                    return {
                        "success": True,
                        "analysis": analysis_result
                    }
                else:
                    print("Réponse vide de l'IA, utilisation du fallback")
                    return self._get_fallback_analysis()
                    
            except json.JSONDecodeError as e:
                print(f"Erreur de parsing JSON: {e}")
                print(f"Réponse problématique: {response.text if response else 'None'}")
                return self._get_fallback_analysis()
            except Exception as e:
                print(f"Erreur lors de l'appel à l'IA: {e}")
                return self._get_fallback_analysis()
                
        except Exception as e:
            print(f"Erreur générale dans analyze_interview_responses: {e}")
            return self._get_fallback_analysis()
    
    def _get_fallback_analysis(self) -> Dict[str, Any]:
        """Retourne une analyse de fallback en cas d'erreur"""
        return {
            "success": True,
            "analysis": {
                "score_global": 6,
                "points_forts": ["Réponses structurées", "Expérience pertinente"],
                "points_amelioration": ["Préparation des exemples", "Concision"],
                "suggestions": [
                    {
                        "titre": "Préparez des exemples concrets",
                        "description": "Préparez 3-5 exemples spécifiques de vos réalisations",
                        "priorite": "haute"
                    },
                    {
                        "titre": "Améliorez la concision",
                        "description": "Gardez vos réponses entre 1-2 minutes",
                        "priorite": "moyenne"
                    },
                    {
                        "titre": "Pratiquez régulièrement",
                        "description": "Utilisez ce simulateur pour vous entraîner",
                        "priorite": "haute"
                    }
                ],
                "conseils_specifiques": []
            }
        } 