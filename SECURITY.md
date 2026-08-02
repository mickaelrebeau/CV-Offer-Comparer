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

## Bonnes pratiques pour les contributeurs

- Ne jamais committer `.env`, clés API, tokens OAuth, dumps DB
- Tourner les secrets exposés par erreur
- Valider les entrées utilisateur côté API (uploads, prompts, CORS)
