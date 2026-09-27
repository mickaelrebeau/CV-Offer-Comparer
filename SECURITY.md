# Politique de sécurité

## Versions supportées

Les correctifs de sécurité sont appliqués en priorité sur la branche `main` (dernière version déployée).

## Signaler une vulnérabilité

**Ne créez pas d’issue publique** pour une faille de sécurité.

Contactez le mainteneur en privé :

- Email : [rebeau.mickael@gmail.com](mailto:rebeau.mickael@gmail.com)
- Ou [GitHub Security Advisories](https://github.com/mickaelrebeau/CV-Offer-Comparer/security/advisories/new) sur ce dépôt

Incluez si possible :

- description de la vulnérabilité
- impact potentiel
- étapes de reproduction / PoC
- versions concernées

Nous accuserons réception sous 72 h ouvrées et travaillerons à un correctif ou une mitigation.

## Endpoints de debug

Les routes suivantes servent uniquement au développement local :

- `POST /api/reset-free-analysis` (réinitialise l’essai gratuit)
- `GET /api/free-analysis-stats`
- `GET /api/test-stream`
- `GET /api/interview/test`

Elles répondent `404` et sont absentes du schéma OpenAPI, sauf si `ENABLE_DEBUG_ENDPOINTS=true` **et** `ENVIRONMENT` ≠ `production`. En production, elles restent désactivées même si le flag est activé par erreur.

## Clés API personnelles (BYOK)

Les comptes connectés peuvent enregistrer leurs propres clés LLM (Gemini, OpenAI, Anthropic, DeepSeek, Qwen, Kimi, endpoint compatible OpenAI). Mesures en place :

- **Chiffrement au repos** : Fernet (AES-128-CBC + HMAC-SHA256) avec `LLM_ENCRYPTION_KEYS`, secret hors dépôt ; rotation via `python -m app.scripts.rotate_llm_keys` (voir `documentation/STARTUP.md`). Sans ce secret, le BYOK est désactivé.
- **Non-exposition** : l’API ne renvoie jamais la clé, seulement un indice masqué (`sk-••••abcd`). Les journaux ne contiennent que le provider, le statut HTTP et un code d’erreur normalisé ; les événements PostHog ne contiennent ni clé ni indice. La clé n’est jamais conservée dans le navigateur (ni `localStorage`, ni champ prérempli).
- **Transit** : HTTPS vers l’API Talento et vers les fournisseurs ; la clé voyage dans le corps JSON ou un en-tête d’autorisation, jamais dans une URL.
- **Purge** : `DELETE /api/profile/llm-credentials/{id}` et la suppression du compte effacent physiquement le chiffré (`ON DELETE CASCADE`).
- **Isolation** : chaque requête filtre par utilisateur ; une seule configuration active par compte (index unique partiel).

### Modèle de menace (résumé)

| Menace | Impact | Mitigation |
|---|---|---|
| **SSRF** via `base_url` (endpoint OpenAI-compatible ou proxy) | Requêtes du serveur vers le réseau interne (métadonnées cloud, Redis, Postgres) | HTTPS obligatoire, pas d’identifiants dans l’URL, suffixes internes refusés, **résolution DNS : IP publiques uniquement**, revalidation avant chaque appel (DNS rebinding), redirections non suivies. Exception `LLM_ALLOW_PRIVATE_BASE_URLS` réservée au dev, ignorée en production |
| **Fuite de la base** | Clés utilisateur exposées | Seul le chiffré est stocké ; le secret de chiffrement vit dans l’environnement, pas en base |
| **XSS sur le profil** | Vol de clé saisie ou de session | Clé jamais réaffichée ni stockée côté client ; rendu Vue échappé, aucun `v-html` sur ces données |
| **Abus de la vérification de clé** | Sondage d’endpoints, coût | Limitation par minute et quota journalier `DAILY_QUOTA_LLM_CREDENTIALS` |
| **Journaux / analytics** | Clé dans des logs tiers | Aucun log du corps des requêtes ni des erreurs provider ; événements PostHog sans valeur sensible |

Limite connue : entre la validation DNS et la connexion, une fenêtre de rebinding très courte subsiste. Pour une instance exposée, préférez en plus un filtrage réseau sortant (egress) côté hébergeur.

## Bonnes pratiques pour les contributeurs

- Ne jamais committer `.env`, clés API, tokens OAuth, dumps DB
- Tourner les secrets exposés par erreur
- Valider les entrées utilisateur côté API (uploads, prompts, CORS)
