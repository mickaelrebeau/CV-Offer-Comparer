# 🚀 Guide de démarrage rapide

## ✅ Problème résolu !

L'erreur `huggingface_hub` a été corrigée en remplaçant `sentence-transformers` par une approche basée uniquement sur Google Gemini.

## 🆕 Nouvelle fonctionnalité : Upload PDF

Vous pouvez maintenant **uploader votre CV au format PDF** au lieu de copier-coller le texte !

### Fonctionnalités upload PDF :
- ✅ **Drag & Drop** : Glissez votre PDF directement
- ✅ **Extraction automatique** : Le texte est extrait automatiquement
- ✅ **Aperçu du texte** : Voir le texte extrait avant comparaison
- ✅ **Validation** : Seuls les PDF jusqu'à 10MB sont acceptés

## 🔧 Configuration finale

### 1. Variables d'environnement

**Frontend** (`.env` à la racine) :
```bash
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

**Backend** (`backend/.env`) :
```bash
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_supabase_service_key
GOOGLE_API_KEY=your_google_api_key
```

### 2. Démarrage

**Terminal 1 - Frontend** :
```bash
npm run dev
```

**Terminal 2 - Backend** :
```bash
cd backend
venv\Scripts\activate
uvicorn main:app --reload
```

## 🎯 Test rapide

1. Ouvrez http://localhost:3000
2. Créez un compte
3. Allez sur "Comparer CV et Offre"
4. **Nouveau** : Uploadez votre CV PDF ou utilisez la saisie manuelle
5. Collez l'offre d'emploi
6. Cliquez sur "Comparer CV et Offre"

## 📊 Fonctionnalités

- **🟢 Vert** : Correspondances trouvées
- **🔴 Rouge** : Éléments manquants  
- **🟡 Jaune** : Points confus
- **💡 Suggestions** : Conseils d'amélioration
- **📄 Upload PDF** : Extraction automatique du texte

## 🆘 En cas de problème

- **Erreur de connexion** : Vérifiez vos clés Supabase
- **Erreur d'IA** : Vérifiez votre clé Google AI
- **Serveur ne démarre pas** : Redémarrez avec `uvicorn main:app --reload`
- **PDF non lu** : Utilisez la saisie manuelle ou vérifiez le format

---

🎉 **Votre comparateur est prêt avec upload PDF !** 