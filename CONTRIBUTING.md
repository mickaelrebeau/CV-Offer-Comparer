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
- Schéma de base : toute modification d'un modèle SQLAlchemy s'accompagne d'une migration Alembic (voir ci-dessous)

### Migrations de base de données (Alembic)

Les migrations sont appliquées automatiquement au démarrage de l'API (`app/migrations.py`, sous verrou PostgreSQL). Depuis `backend/`, avec `DATABASE_URL` défini :

```bash
# Après avoir modifié ou ajouté un modèle (pensez à l'importer dans app/models/tables.py)
alembic revision --autogenerate --rev-id 0003 -m "ajout de la colonne x"
# Relire le fichier généré dans migrations/versions/, puis :
alembic upgrade head      # appliquer
alembic check             # vérifier que le schéma correspond aux modèles
alembic downgrade -1      # annuler la dernière migration
```

- Numérotez les révisions à la suite (`0003`, `0004`…) ; une seule tête de migration (`tests/test_migrations.py` le vérifie).
- Écrivez toujours le `downgrade()` et relisez l'autogénération (index partiels, valeurs par défaut, renommages détectés comme suppression + ajout).
- Une migration ne modifie jamais une révision déjà mergée : ajoutez-en une nouvelle.

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

## Langues (i18n)

Contrat de locale : **aucun texte visible en dur**, côté front comme côté API.

**Frontend**

- Ajouter chaque texte dans `frontend/src/locales/fr.json` **et** `en.json` (mêmes clés, mêmes paramètres `{nom}`), puis l’utiliser via `t('section.cle')` (`useI18n()` dans les composants, `t` de `@/i18n` dans les stores et `lib/api`).
- Liens et redirections : `localePath()` / `push()` / `replace()` de `useLocale()` (jamais de chemin `'/…'` en dur).
- Dates et nombres : `formatDate`, `formatNumber`, `formatPercent` de `useLocale()`.
- Caractères réservés de vue-i18n : écrire `{'@'}` pour un « @ » littéral, éviter `|`.
- Nouvelle page publique : route dans `src/router/index.ts` (clé `seo`), traduite par défaut ; `translated: false` tant que le contenu n’existe qu’en français. Ajouter les chemins à prégénérer dans `prerender-routes.ts`.
- `pnpm test:locales` vérifie la cohérence des catalogues et les clés utilisées ; `pnpm test:prerender` vérifie `lang`, canonical et `hreflang` des pages générées.

**Backend**

- Message exposé au client : `raise ApiError(status, "domaine.code", **params)` avec le texte fr/en dans `backend/app/i18n.py` (`MESSAGES`). La réponse contient `detail` (traduit selon `Accept-Language`) et `code` (stable, pour la logique côté client).
- Messages de réponse (`message`, statuts SSE, e-mails) : dépendance `locale: str = Depends(request_locale)` puis `t(code, locale)`.
- Ne jamais renvoyer `str(exception)` au client : journaliser le détail, renvoyer un code générique.

## PWA (webapp installable)

- Manifeste : `frontend/public/manifest.webmanifest` ; icônes dans `frontend/public/icons/` (192/512 `any` + `maskable`, `apple-touch-icon` 180).
- Service worker : modèle `frontend/pwa/sw.template.js`, généré au build dans `dist/sw.js` (liste de précache + version calculée sur le contenu). Pages : réseau d’abord, repli cache puis shell SPA hors ligne ; assets versionnés : cache d’abord ; Google Fonts : stale-while-revalidate. **Jamais** de cache pour l’API, les vidéos ou les documents utilisateur.
- Actif uniquement en production (`pnpm build` + `serve dist`), pas avec `pnpm dev`.
- `pnpm test:pwa` (CI) vérifie manifeste, icônes, service worker actif, précache sans API et navigation hors ligne.

**Smoke Lighthouse / installabilité (manuel, avant une release touchant la PWA)**

1. `pnpm build && npx serve@14 dist -l 4173` (localhost compte comme contexte sécurisé ; en production, HTTPS est fourni par Railway).
2. Chrome DevTools → **Application** → *Manifest* : aucune erreur d’installabilité, icônes maskables correctes (aperçu « Show only the minimum safe area »). *Service workers* : `sw.js` activé ; cocher *Offline* puis recharger `/`, `/en/login` et `/compare?history=…` (shell + bandeau hors ligne).
3. Lighthouse : la catégorie PWA a été retirée de Lighthouse 12 ; utiliser `npx lighthouse@11 http://localhost:4173 --only-categories=pwa --view` (attendu : *Installable* et *PWA Optimized* au vert), ou l’onglet Application ci-dessus.
4. Android / Chrome desktop : le bouton « Installer l’app » apparaît (en-tête, profil, pied de page de la landing) quand `beforeinstallprompt` est émis. iOS : partage → « Sur l’écran d’accueil ».

## Pull Requests

Une bonne PR :

- [ ] se concentre sur **un** sujet
- [ ] inclut une description et un plan de test
- [ ] ne casse pas le flux auth / compare de base
- [ ] met à jour la doc si le comportement change

Les mainteneurs pourront demander des ajustements avant merge.

## Licence

En contribuant, vous acceptez que vos contributions soient licenciées sous la [licence MIT](LICENSE) du projet.
