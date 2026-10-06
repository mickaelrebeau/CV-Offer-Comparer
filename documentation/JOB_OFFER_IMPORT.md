# Import d'une offre depuis son URL

`POST /api/job-offers/import` `{ "url": "…", "ai_cleanup": false }` (authentifié) renvoie
`{ title, company, location, text, source_url, method, cached }`.

## Extraction

| Ordre | Méthode (`method`) | Source |
| --- | --- | --- |
| 1 | `json-ld` | Données structurées `schema.org/JobPosting` de la page (utilisées par Google for Jobs) |
| 2 | `html` | Contenu principal de la page ([trafilatura](https://trafilatura.readthedocs.io)), sans menus, cookies ni « offres similaires » |
| 3 | `api` | API publique de l'ATS quand la page est rendue en JavaScript (Workable) |
| — | `paste` | Sites qui bloquent les serveurs : page copiée-collée par l'utilisateur (`POST /api/job-offers/parse`) |
| — | `ai` | Optionnel (`ai_cleanup: true`, bouton « Nettoyer avec l'IA ») : nettoyage par le provider IA actif de l'utilisateur (BYOK) ou la plateforme. Compte vérifié requis |

Résultat mis en cache 15 min par URL (Redis, empreinte SHA-256 de l'URL). Quota : `DAILY_QUOTA_JOB_OFFER_IMPORT` (50 / jour / utilisateur) en plus de la limite par minute.

## Sécurité (SSRF)

Le serveur télécharge une URL choisie par l'utilisateur (`app/services/job_offers/fetch.py`) :

- schémas `http` / `https`, ports 80 / 443, pas d'identifiants dans l'URL ;
- l'hôte doit résoudre **uniquement** vers des IP publiques (loopback, réseaux privés, link-local / métadonnées cloud `169.254.169.254`, IPv6 locales et IPv4 encapsulées refusés) ;
- contrôle refait **au moment de la connexion** (backend réseau httpcore) : un DNS qui change entre la vérification et la connexion (rebinding) ne contourne pas la règle ;
- redirections suivies à la main et revalidées une à une (5 au maximum) ;
- délai 10 s (connexion 5 s), 3 Mo maximum après décompression, `Content-Type` HTML uniquement (JSON pour les API d'ATS), proxys de l'environnement ignorés.

L'URL conservée dans l'historique (`offer_url`) n'est acceptée qu'en `http(s)` (jamais `javascript:`).

## Sites testés

Vérifiés le 6 octobre 2026 sur des offres réelles :

| Site / ATS | Résultat | Méthode |
| --- | --- | --- |
| HelloWork (`hellowork.com`) | ✅ poste, entreprise, lieu, description | `json-ld` |
| WeLoveDevs (`welovedevs.com/app/…/job/…`) | ✅ poste, entreprise, lieu, description | `json-ld` |
| Ashby (`jobs.ashbyhq.com`) | ✅ poste, entreprise, lieu, description | `json-ld` |
| Lever (`jobs.lever.co`) | ✅ poste, entreprise, lieu, description | `json-ld` |
| Workable (`apply.workable.com`) | ✅ poste, lieu, description (entreprise = identifiant du compte) | `api` |
| Greenhouse (`job-boards.greenhouse.io`) | ✅ poste et description (entreprise et lieu à compléter) | `html` |
| Recruitee (sites carrières `*.recruitee.com` / domaine propre) | ✅ poste et description | `html` |
| France Travail (`candidat.francetravail.fr`) | ✅ poste et description | `html` |

En `html`, le titre provient de la page (`og:title`) et peut contenir le nom du site : l'aperçu est éditable avant l'analyse, et « Nettoyer avec l'IA » le corrige.

## Sites qui bloquent les serveurs : lecture depuis le navigateur

Indeed, LinkedIn, Welcome to the Jungle, Glassdoor et Monster refusent les requêtes serveur
(Indeed : challenge Cloudflare 403 / 401 sur chaque page ; Welcome to the Jungle : 503 puis délais
dépassés ; LinkedIn : connexion requise). Ils ne sont **jamais appelés** par le serveur
(`job_offer.site_blocked`, y compris après une redirection) : aucun contournement d'anti-robots.

L'offre est lue dans le navigateur de l'utilisateur, qui y a accès :

1. **Bouton « Envoyer vers Talento »** (bookmarklet, page `/import`) : glissé une fois dans la barre de
   favoris, il ouvre `/import#offer=…` avec, par ordre de priorité côté serveur :
   - **Indeed / LinkedIn** : poste, entreprise, lieu et description lus dans le **panneau de l'offre
     affichée** (sélecteurs `SITE_SELECTORS` de `frontend/src/lib/jobOffer.ts`, plusieurs par champ) et
     l'URL propre de l'offre (`viewjob?jk=…` depuis `vjk`, `/jobs/view/<id>/` depuis `currentJobId`).
     Sur leurs pages de recherche, le JSON-LD, le premier `<h1>` et l'URL décrivent la liste, pas
     l'offre ouverte ;
   - le JSON-LD `JobPosting` : une seule offre, retenue ; plusieurs (liste, offres similaires),
     seule celle dont le titre correspond à l'offre affichée (sinon aucune) ;
   - un texte de secours : sélection de l'utilisateur (prioritaire sur tout le reste), zone de
     description connue ou page.

   **Indeed** change souvent ses classes CSS (page d'accueil « Emplois recommandés » : aucun repère
   connu). Sans description trouvée par sélecteur, le bouton envoie le texte de la page et le serveur
   repère l'offre affichée grâce à ses libellés, stables (`app/services/job_offers/page_text.py`) :
   « titre, entreprise, (note), lieu, contrat, Postuler… » puis « Description du poste » →
   « Signaler l'offre » (libellés anglais gérés aussi). Le copier-coller de toute la page passe par le
   même chemin. Exemple réel en test : `backend/tests/fixtures/indeed_accueil_fr.txt`. Le fragment `#…` n'est jamais envoyé au serveur
   web ; la page l'efface de la barre d'adresse puis l'analyse via `POST /api/job-offers/parse`.
   Ordinateur uniquement (les navigateurs mobiles ne gèrent pas ces favoris).
2. **Copier-coller guidé** dans le champ offre : lien de l'annonce conservé, page copiée (Ctrl+A,
   Ctrl+C) puis analysée ; « Nettoyer avec l'IA » extrait poste, entreprise et lieu.

Vérifié le 6 octobre 2026 sur des pages reproduisant la structure d'Indeed (page de recherche avec
`vjk`) et de LinkedIn (liste avec `currentJobId`) : à contrôler à la main sur les vraies pages, dont les
classes changent régulièrement. Si un site change, mettre à jour `SITE_SELECTORS` (les utilisateurs
doivent alors réinstaller le bouton).

Également refusants à l'usage (401 / 403 / 429 / 999 → même parcours) : APEC (`apec.fr`, 403).

Pages sans texte exploitable (application JavaScript sans données structurées, page de connexion) → `job_offer.no_content`.
