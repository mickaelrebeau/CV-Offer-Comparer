# 🚀 Guide de démarrage - Comparateur CV ↔ Offre d'emploi

## ✅ Installation terminée !

Votre application est maintenant prête à être utilisée. Voici les étapes finales :

## 🔧 Configuration des variables d'environnement

### 1. Frontend (.env à la racine)
```bash
cp env.example .env
```

Éditez `.env` avec vos clés Supabase :
```
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### 2. Backend (backend/.env)
```bash
cd backend
cp env.example .env
```

Éditez `backend/.env` avec vos clés :
```
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_supabase_service_key
GOOGLE_API_KEY=your_google_api_key
```

## 🔑 Obtenir vos clés

### Supabase
1. Allez sur [supabase.com](https://supabase.com)
2. Créez un nouveau projet
3. Dans Settings > API, copiez :
   - Project URL → `SUPABASE_URL`
   - anon public → `VITE_SUPABASE_ANON_KEY`
   - service_role → `SUPABASE_SERVICE_KEY`

### Google AI
1. Allez sur [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Créez une nouvelle clé API
3. Copiez la clé → `GOOGLE_API_KEY`

## 🚀 Démarrage de l'application

### Terminal 1 - Frontend
```bash
npm run dev
```
→ http://localhost:3000

### Terminal 2 - Backend
```bash
cd backend
venv\Scripts\activate
uvicorn main:app --reload
```
→ http://localhost:8000

## 🎯 Test de l'application

1. **Ouvrez** http://localhost:3000
2. **Créez un compte** ou connectez-vous
3. **Allez sur** "Comparer CV et Offre"
4. **Collez** une offre d'emploi et votre CV
5. **Cliquez** sur "Comparer CV et Offre"

## 📊 Fonctionnalités

- **🟢 Vert** : Correspondances trouvées
- **🔴 Rouge** : Éléments manquants
- **🟡 Jaune** : Points confus/imprécis
- **Suggestions** : Conseils pour améliorer votre CV

## 🆘 Dépannage

### Erreur de connexion
- Vérifiez vos clés Supabase dans `.env`
- Assurez-vous que le backend tourne sur le port 8000

### Erreur d'IA
- Vérifiez votre clé Google AI
- Assurez-vous d'avoir des crédits Google AI

### Erreur de serveur
- Redémarrez avec `uvicorn main:app --reload`
- Vérifiez que l'environnement virtuel est activé

## 📞 Support

- **Documentation** : Voir `README.md`
- **Guide rapide** : Voir `QUICKSTART.md`
- **Issues** : Ouvrez une issue sur GitHub

---

🎉 **Votre comparateur CV ↔ Offre d'emploi est prêt !** 