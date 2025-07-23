# Comparateur CV ↔ Offre d'emploi

Une application web intelligente qui compare automatiquement un CV avec une offre d'emploi en utilisant l'intelligence artificielle pour identifier les correspondances, les lacunes et fournir des suggestions d'amélioration.

## 🚀 Fonctionnalités

### ✨ **Analyse intelligente multi-métiers**
- **Support de tous les métiers** : Développement, Design, Marketing, Vente, Finance, RH, Logistique, Santé, Éducation, etc.
- **Extraction automatique** : Compétences techniques, soft skills, langues, expériences
- **Comparaison sémantique** : Reconnaissance des synonymes et variations
- **Suggestions personnalisées** : Conseils pour améliorer le CV

### 🎯 **Interface moderne et intuitive**
- **Upload PDF** : Extraction automatique du texte des CV
- **Saisie manuelle** : Possibilité de coller directement le texte
- **Résultats en temps réel** : Streaming des résultats avec progression
- **Interface responsive** : Compatible desktop et mobile

### 🔒 **Sécurité et authentification**
- **Authentification Supabase** : Connexion sécurisée
- **Persistance de session** : Reste connecté après rechargement
- **Protection des données** : Chiffrement et sécurité

## 🏗️ Architecture

### **Frontend (Vue.js 3 + TypeScript)**
```
src/
├── components/          # Composants réutilisables
│   ├── ComparisonView.vue
│   ├── PDFUpload.vue
│   └── ui/             # Composants UI
├── stores/             # Gestion d'état (Pinia)
│   ├── auth.ts
│   └── compare.ts
├── views/              # Pages de l'application
├── router/             # Configuration des routes
└── lib/                # Utilitaires et configurations
```

### **Backend (FastAPI + Python)**
```
backend/
├── app/
│   ├── models/         # Modèles Pydantic
│   ├── services/       # Logique métier
│   │   ├── ai_service.py      # Service IA
│   │   ├── comparison_service.py
│   │   ├── upload_service.py
│   │   └── auth_service.py
│   ├── routers/        # Endpoints API
│   └── utils/          # Utilitaires
├── main.py         # Point d'entrée
└── requirements.txt
```

## 🛠️ Technologies utilisées

### **Frontend**
- **Vue.js 3** : Framework progressif
- **TypeScript** : Typage statique
- **Pinia** : Gestion d'état
- **Vue Router** : Navigation
- **Tailwind CSS** : Styling
- **Lucide Icons** : Icônes
- **Axios** : Client HTTP

### **Backend**
- **FastAPI** : Framework web moderne
- **Python 3.11+** : Langage principal
- **Google Gemini AI** : Intelligence artificielle
- **Supabase** : Authentification et base de données
- **PyPDF2/pdfplumber** : Extraction de texte PDF
- **Pydantic** : Validation de données

### **IA et ML**
- **Google Gemini 2.5 Flash Lite** : Modèle de langage
- **Comparaison sémantique** : Analyse de similarité
- **Extraction de compétences** : Reconnaissance automatique
- **Génération de suggestions** : Conseils personnalisés

## 📦 Installation

### **Prérequis**
- Node.js 18+ et npm/pnpm
- Python 3.11+
- Compte Google Cloud (pour Gemini AI)
- Compte Supabase

### **1. Cloner le repository**
```bash
git clone https://github.com/votre-username/cv-offer-compare.git
cd cv-offer-compare
```

### **2. Configuration Frontend**
```bash
# Installer les dépendances
npm install
# ou
pnpm install

# Copier le fichier d'environnement
cp env.example .env.local
```

### **3. Configuration Backend**
```bash
cd backend

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt

# Copier le fichier d'environnement
cp env.example .env
```

### **4. Configuration des variables d'environnement**

#### **Frontend (.env.local)**
```env
VITE_SUPABASE_URL=votre_url_supabase
VITE_SUPABASE_ANON_KEY=votre_clé_anon_supabase
```

#### **Backend (.env)**
```env
SUPABASE_URL=votre_url_supabase
SUPABASE_SERVICE_KEY=votre_clé_service_supabase
GOOGLE_API_KEY=votre_clé_api_google_gemini
```

### **5. Lancer l'application**

#### **Développement**
```bash
# Terminal 1 - Frontend
npm run dev

# Terminal 2 - Backend
cd backend
python main.py
```

#### **Production**
```bash
# Build frontend
npm run build

# Lancer backend
cd backend
python main.py
```

## 🎯 Utilisation

### **1. Connexion**
- Créez un compte ou connectez-vous
- L'authentification est gérée par Supabase

### **2. Comparaison**
- **Collez l'offre d'emploi** dans le champ dédié
- **Uploadez votre CV** en PDF ou saisissez le texte manuellement
- **Cliquez sur "Comparer"** pour lancer l'analyse

### **3. Résultats**
- **Correspondances** : Compétences trouvées (vert)
- **Lacunes** : Compétences manquantes (rouge)
- **Confus** : Correspondances partielles (jaune)
- **Suggestions** : Conseils d'amélioration

## 🔧 Métiers supportés

### **Développement**
- Langages : JavaScript, Python, Java, PHP, etc.
- Frameworks : React, Vue, Angular, Node.js, etc.
- Outils : Git, Docker, AWS, etc.

### **Design**
- Outils : Photoshop, Illustrator, Figma, Sketch
- Compétences : UX/UI, Typographie, Branding
- Domaines : Web, Print, Mobile

### **Marketing**
- Digital : Google Ads, Facebook Ads, SEO, SEM
- Analytics : Google Analytics, Conversion
- Content : Social Media, Email Marketing

### **Vente**
- Techniques : Prospection, Négociation, CRM
- Soft skills : Relation client, Présentation
- Outils : Salesforce, HubSpot, etc.

### **Finance**
- Domaines : Comptabilité, Analyse financière
- Outils : Excel, SAP, Sage, Tableaux de bord
- Compétences : Audit, Contrôle de gestion

### **Ressources Humaines**
- Fonctions : Recrutement, Formation, Paie
- Outils : SIRH, ATS, Évaluation
- Compétences : Droit social, Gestion des talents

### **Autres métiers**
- **Logistique** : Supply chain, Transport, Stocks
- **Santé** : Médical, Soins, Paramédical
- **Éducation** : Enseignement, Formation
- **Consultant** : Conseil, Stratégie
- **Manager** : Leadership, Gestion d'équipe
- **Ingénieur** : Technique, Innovation

## 🚀 Déploiement

### **Frontend (Vercel/Netlify)**
```bash
npm run build
# Déployer le dossier dist/
```

### **Backend (Railway/Heroku)**
```bash
# Configurer les variables d'environnement
# Déployer le dossier backend/
```

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🙏 Remerciements

- **Google Gemini** pour l'IA
- **Supabase** pour l'authentification
- **Vue.js** pour le framework frontend
- **FastAPI** pour le framework backend
- **Tailwind CSS** pour le styling

## 📞 Support

Pour toute question ou problème :
- Ouvrir une issue sur GitHub
- Contacter l'équipe de développement

---

**Développé avec ❤️ pour simplifier la recherche d'emploi** 