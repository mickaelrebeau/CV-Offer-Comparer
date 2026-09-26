# Contribuer à Talento

Merci de vouloir contribuer ! Ce guide explique comment participer efficacement.

## Code of Conduct

En participant, vous acceptez le [Code of Conduct](CODE_OF_CONDUCT.md).

## Comment contribuer

### Signaler un bug

1. Vérifiez qu’il n’existe pas déjà une [issue](https://github.com/mickaelrebeau/CV-Offer-Comparer/issues) similaire.
2. Ouvrez un **Bug report** avec :
   - étapes de reproduction
   - comportement attendu vs observé
   - environnement (OS, navigateur, versions Node/Python)
   - logs pertinents (sans secrets)

### Proposer une fonctionnalité

Ouvrez un **Feature request** en décrivant le besoin, le bénéfice utilisateur, et des alternatives envisagées.

### Améliorer la documentation

Corrections de typos, clarifications du README / guides de démarrage : PRs bienvenues, même petites.

## Setup de développement

Voir le [README](README.md) et [documentation/STARTUP.md](documentation/STARTUP.md).

Résumé :

```bash
# Backend
cd backend && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp env.example .env   # remplir les valeurs
uvicorn main:app --reload

# Frontend (autre terminal)
cd frontend && pnpm install && cp env.example .env
pnpm dev
```

Ne committez jamais de fichiers `.env` ni de clés API.

## Workflow Git

1. Forkez le dépôt (ou créez une branche si vous avez les droits).
2. Créez une branche descriptive :

   ```bash
   git checkout -b feat/ma-feature
   # ou fix/description-du-bug
   ```

3. Committez avec des messages clairs (style conventionnel apprécié) :

   ```
   feat: add comparison history endpoint
   fix: prevent auth callback remount loop
   docs: update local OAuth setup
   ```

4. Poussez et ouvrez une **Pull Request** vers `main`.
5. Décrivez le *pourquoi*, comment tester, et liez l’issue (`Fixes #123`).

## Conventions de code

### Backend (Python / FastAPI)

- Python 3.11+
- Typage et modèles Pydantic quand c’est pertinent
- Pas de dépendances lourdes inutiles (l’IA passe par Gemini uniquement)
- Garder les endpoints SSE non bloquants (`asyncio.to_thread` pour les appels Gemini)

### Frontend (Vue 3 / TypeScript)

- Composition API + `<script setup>`
- Pinia pour l’état
- Respecter le design system / styles existants
- `VITE_*` uniquement pour les variables publiques (jamais de secrets)

### Secrets & sécurité

- Utiliser `env.example` comme référence
- Pas de credentials dans les issues / PRs / screenshots

## Branding

Le produit s’appelle **Talento**. Le dépôt GitHub garde son nom historique `CV-Offer-Comparer` : les URL du dépôt (issues, clone, badges) restent inchangées.

Avant d’ouvrir une PR qui ajoute du texte visible, des métadonnées ou des clés techniques :

- [ ] Textes UI, titres de page, e-mails et messages d’API utilisent « Talento » (jamais « CV-Offer-Comparer » ni « Comparateur CV ↔ Offre » comme nom de produit)
- [ ] Titre et description OpenAPI (`backend/app/main.py`) et réponse de `/api/health` cohérents
- [ ] Nouvelles clés `localStorage` préfixées `talento_` et déclarées dans `frontend/src/lib/storageKeys.ts`
- [ ] Renommage d’une clé existante : ajouter l’ancienne dans `LEGACY_KEYS` (migration douce, pas de déconnexion)
- [ ] Nouvelles origines CORS : uniquement des domaines actifs (`ALLOWED_ORIGINS`, `backend/env.example`)
- [ ] Métadonnées SEO et JSON-LD via `frontend/src/lib/site.ts` (`SITE_NAME`, `SITE_URL`)

Clés historiques migrées automatiquement côté front :

| Ancienne clé | Nouvelle clé |
|---|---|
| `cv_offer_access_token` | `talento_access_token` |
| `cv-offer-compare-free-analysis-used` | `talento_free_analysis_used` |

## Pull Requests

Une bonne PR :

- [ ] se concentre sur **un** sujet
- [ ] inclut une description et un plan de test
- [ ] ne casse pas le flux auth / compare de base
- [ ] met à jour la doc si le comportement change

Les mainteneurs pourront demander des ajustements avant merge.

## Licence

En contribuant, vous acceptez que vos contributions soient licenciées sous la [licence MIT](LICENSE) du projet.
