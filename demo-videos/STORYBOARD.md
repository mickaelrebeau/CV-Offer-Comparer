---
format: 1920x1080
duration: 18s (×3 vidéos, ×2 langues)
message: "Talento est un vrai outil : on le voit analyser, entraîner et rédiger à partir d'un vrai CV et d'une vraie offre"
arc: Accroche → l'app entre en scène → la machine travaille → le résultat (hero) → le détail utile → signature de marque → boucle
audience: candidats qui visitent la landing de Talento (section « Aperçu réel »)
mode: collaborative
---

# Démos Talento — storyboard v2

## Changes from v1

- Retour utilisateur (verbatim) : « je veux des vidéos dynamique avec des belles transition. ce sont certe des vidéos de démo mais je veux égalmenet un coté marketing pour la landing page ».
- Ajouts : une **accroche titrée** en ouverture, l'app présentée comme un **produit mis en scène** (fenêtre flottante en 3D sur une scène papier), des **transitions** entre chaque phase, des **callouts** qui nomment la fonctionnalité montrée, une **signature de marque** (logo + slogan + bouton d'action) avant la boucle.
- Durée : 15 s → **18 s** par vidéo (l'accroche et la signature prennent ~4 s ; la démo garde ~13 s).
- Levée de l'interdit v1 « pas de texte marketing » : le texte ajouté vient **uniquement du copy existant** de la landing et du dashboard (déjà traduit FR/EN), jamais d'une promesse inventée.

## Locked

- Plan v2 validé (« je valide la V2 ») et planche d'esquisses `storyboard.html` validée (« c'est validé, lance la construction ») : placement, hiérarchie et copy des 16 plans sont figés ; la construction habille ces mises en page sans les redessiner.

## Écarts au build (vérité de l'UI)

- Frame 5 : dans l'app, le bouton « Copier » d'une reformulation ne change pas de libellé ; la vidéo montre le clic (onde du curseur) sans « Copié ✓ » inventé. Les autres critères s'estompent pendant le plan tenu (traitement de montage).
- Frame 9 : « Obtenir le rapport » n'apparaît qu'à la dernière question ; la vidéo montre le clic sur « Suivante » puis une ellipse (zoom-through) vers le rapport.
- Chiffres des cartes vert / ambre un cran plus foncés que dans l'app (émeraude 600, ambre 700) pour le contraste en vidéo ; apparitions sans rebond (`power3.out`, règle spring-pop), au lieu du `back.out` prévu.
- Durée réelle : 18,0 s par vidéo (6 rendus).

## Décisions

- **Message** : « Voici l'outil, pas une maquette » — chaque démo déroule un vrai parcours de l'app, emballé comme une séquence produit.
- **Audience et arc** : visiteurs de la landing, fenêtre de ~900 px de large, en lecture muette et en boucle. Arc de chaque vidéo : accroche → l'app entre en scène → la machine travaille → le résultat (hero) → le détail utile → signature → boucle.
- **Format** : 1920×1080, 30 fps, 18 s, muet, boucle (la dernière image rejoint la première). Trois compositions (`analyse`, `entretien`, `lettre`), variable `lang` (`fr` / `en`) → 6 rendus.
- **Scène (le fil conducteur)** : un **plateau papier** `#F1EEE7` légèrement texturé (grain fin), une grille de filets `#D5D0C4` qui dérive lentement, et un **chiffre fantôme géant** du module (« 01 », « 02 », « 03 », encre à ~12 %). L'app est une **fenêtre flottante** (barre de navigation Talento, onglet actif) avec une ombre portée franche, qui entre en perspective 3D puis se redresse ; la caméra la parcourt (push-in, recadrage, bascule). Un **curseur** unique pilote chaque action.
- **Lisibilité** : UI reconstruite à ~1,5× et cadrée sur la zone active par la caméra, pour rester lisible dans une fenêtre de 900 px.
- **Transitions (overview « Medium → High », SaaS/lancement)** :
  - principale — **zoom-through** : la caméra traverse l'élément sur lequel on vient d'agir (le bouton, la carte de score) pour entrer dans la phase suivante, 0,4 s, `power4.inOut` ;
  - accent 1 — **3D reveal** : l'arrivée de la fenêtre d'app après l'accroche (perspective → à plat, 0,7 s, `expo.out`) ;
  - accent 2 — **blur crossfade** : sortie de la signature vers l'accroche, pour la boucle (0,7 s, `sine.inOut`).
  - Une seule direction de mouvement pour tout le film : **de droite à gauche / vers l'avant**.
- **Copy marketing (existant, FR / EN)** :
  - accroches — Analyse : `landing.hero.title` « L'analyse ATS que vous ne referez plus à la main. » ; Entretien : « Préparez l'étape décisive. » (début de `dashboard.modules.interview.description`) ; Lettre : `coverLetter.title` « Une lettre qui répond à l'offre ».
  - callouts — les 3 `dashboard.modules.<module>.features` de chaque module (ex. « Diagnostic d'écart sémantique », « Chronomètre en direct », « Copie et export .txt / .md »).
  - signature — logo Talento + `landing.footer.slogan` « Candidatez juste. » + bouton du module (`landing.nav.analyze` « Analyser mon CV », `dashboard.modules.interview.cta` « Démarrer la simulation », `dashboard.modules.coverLetter.cta` « Rédiger une lettre »).
- **Marque, capturée sur l'app** (`capture/fr|en/*.png`, `frontend/tailwind.config.js`) : papier `#F1EEE7` / `#E6E2D8` / `#D5D0C4`, encre `#232323` / `#141414` / `#5E5C57` ; statuts couvert `#10B981`, partiel `#F59E0B`, manquant `#F43F5E` (seules couleurs saturées, toujours porteuses de sens) ; **Geist** + **Geist Mono** en fichiers locaux ; rayons 12 / 8 px ; eases `power3.out` (entrées), `power2.inOut` (caméra), `back.out(1.4)` (pastilles), `expo.out` (3D reveal).
- **Callouts** : étiquette Geist Mono en capitales sur fond encre `#232323`, texte papier, reliée à l'élément par un filet qui se trace (`scaleX 0 → 1`), jamais plus d'un callout à l'écran à la fois.
- **Registre** (à installer au build) : `zoom-through-transition`, `ui-3d-reveal`, `browser-device-stage`, `simulated-cursor`, `kinetic-center-build` — adaptés aux tokens Talento.
- **Données** : couple CV / offre anonymisé (`data/inputs.json`) ; résultats réellement calculés par l'app (captures) : 5 couverts, 3 manquants, 2 à préciser, score ATS 50 % ; entretien 7,6/10 ; lettre signée « Alex Moreau ».
- **Interdits** : pas de glow, pas de dégradé linéaire plein écran, pas de néon, pas d'UI inventée, pas de promesse marketing hors copy existant, pas de donnée personnelle réelle ni de nom d'entreprise, pas de callout manuscrit (hors charte). Éviter le **diaporama** (les phases restent dans la même fenêtre, la caméra relie tout) et l'**économiseur d'écran** (chaque mouvement de caméra suit une action).
- **Plan tenu (held frame)** : un par vidéo, sur le détail utile (la reformulation, le score, la lettre copiée) — la caméra s'arrête, l'information se lit ~1,2 s.
- **Vérité** : l'app à l'écran est l'UI réelle de Talento reconstruite d'après les captures, avec ses libellés i18n ; les chiffres sont ceux produits par l'app sur les données anonymisées. Le texte hors app (accroche, callouts, signature) est le copy existant du site.

## Frame 1 — Analyse · Accroche (0–2,2 s)

- scene: Plateau papier, « 01 » fantôme ; « L'analyse ATS que vous ne referez plus à la main. » se construit mot à mot
- duration: 2.2s
- transition_in: cut
- status: animated
- src: compositions/analyse.html
- video: analyse
- blueprint: kinetic-type-beats (kinetic-center-build)
- poster: 1.6s

Premier mouvement à 0,1 s : les mots entrent par la droite et poussent la phrase vers la gauche jusqu'à la verrouiller, Geist 96 px encre. La grille dérive, le « 01 » géant glisse lentement. Contrainte : pas de sous-titre, pas de logo ici.

## Frame 2 — Analyse · L'app entre en scène (2,2–5 s)

- scene: 3D reveal de la fenêtre Comparateur ; offre et CV se remplissent ; callout « Extraction des compétences requises »
- duration: 2.8s
- transition_in: 3d-reveal
- status: animated
- src: compositions/analyse.html
- video: analyse
- blueprint: cursor-ui-demo (+ ui-3d-reveal)
- poster: 4.2s

Le titre recule et s'efface pendant que la fenêtre arrive inclinée (≈ 25°, de la droite) et se pose à plat. Le texte de l'offre puis du CV apparaît ligne par ligne ; le callout pointe le panneau offre. Le curseur entre et file vers « Lancer la comparaison ».

## Frame 3 — Analyse · La machine travaille (5–7 s)

- scene: Clic ; statuts réels et barre de progression ; la caméra pousse vers le bouton
- duration: 2s
- transition_in: cut
- status: animated
- src: compositions/analyse.html
- video: analyse
- blueprint: agent-progress-theater
- poster: 6.2s

Clic (onde de pression), spinner, « Analyse ATS par Gemini (extraction + matching)… », barre 12 % → 60 %. La caméra accélère vers le bouton : c'est lui que la transition va traverser.

## Frame 4 — Analyse · Le résultat (7–11,5 s) — HERO

- scene: Zoom-through vers les 4 cartes qui comptent (5 · 3 · 2 · 50 %) ; le rapport se remplit ; callout « Diagnostic d'écart sémantique »
- duration: 4.5s
- transition_in: zoom-through
- status: animated
- src: compositions/analyse.html
- video: analyse
- blueprint: dataviz-countup + grid-card-assemble
- poster: 9.5s

La transition la plus marquée du film : on traverse le bouton et on atterrit, cadré serré, sur les cartes de stats qui comptent (émeraude, rose, ambre, encre). La caméra recule d'un cran pendant que le rapport sombre se remplit en cascade, pastilles COUVERT / PARTIEL / MANQUANT en pop.

## Frame 5 — Analyse · Le détail utile (11,5–14,5 s)

- scene: Push-in sur « LangChain, RAG et bases vectorielles — MANQUANT » et sa reformulation ; clic « Copier » ; callout « Reformulations directes »
- duration: 3s
- transition_in: cut
- status: animated
- src: compositions/analyse.html
- video: analyse
- blueprint: cursor-ui-demo
- poster: 13.5s

Plan tenu ~1,2 s après le clic « Copier » : « Décrivez un pipeline RAG ou un assistant IA que vous avez construit ». Contrainte : aucun autre élément ne bouge pendant la tenue.

## Frame 6 — Analyse · Signature (14,5–18 s)

- scene: La fenêtre recule et bascule hors champ ; logo Talento, « Candidatez juste. », bouton « Analyser mon CV » cliqué ; blur crossfade vers l'accroche
- duration: 3.5s
- transition_in: zoom-out
- status: animated
- src: compositions/analyse.html
- video: analyse
- blueprint: cta-morph-press
- poster: 16s

La fenêtre se réduit et part vers la gauche en 3D ; au centre, le logo et le slogan se posent, le bouton encre apparaît, le curseur le presse (retour visuel). 17,3 s : blur crossfade vers l'état exact de la frame 1 à 0 s — boucle invisible.

## Frame 7 — Entretien · Accroche (0–2,2 s)

- scene: Plateau papier, « 02 » fantôme ; « Préparez l'étape décisive. » se construit mot à mot
- duration: 2.2s
- transition_in: cut
- status: animated
- src: compositions/entretien.html
- video: entretien
- blueprint: kinetic-type-beats (kinetic-center-build)
- poster: 1.6s

## Frame 8 — Entretien · Les questions (2,2–5,5 s)

- scene: 3D reveal du Simulateur ; clic « Générer les questions » ; 5 questions ciblées en cascade ; callout « Questions prédictives ciblées »
- duration: 3.3s
- transition_in: 3d-reveal
- status: animated
- src: compositions/entretien.html
- video: entretien
- blueprint: cursor-ui-demo + grid-card-assemble
- poster: 4.8s

Panneaux déjà remplis ; le curseur clique immédiatement. Les cartes « Question N · Catégorie » s'empilent (LLM en production, assistant RH en RAG, migration AWS → Azure, API REST robuste, motivation). Le curseur file vers « Lancer la simulation ».

## Frame 9 — Entretien · Répondre (5,5–10,5 s)

- scene: Zoom-through dans le panneau sombre « Question 1 / 5 » ; chronomètre ; la réponse se tape ; callout « Chronomètre en direct »
- duration: 5s
- transition_in: zoom-through
- status: animated
- src: compositions/entretien.html
- video: entretien
- blueprint: prompt-type-submit-generate (variante frappe)
- poster: 8.5s

On traverse « Lancer la simulation » et on atterrit dans le panneau sombre : la question en grand, le chronomètre avance, la réponse se tape (« …–35 % de coûts… »), progression 20 %. Le curseur clique « Obtenir le rapport ».

## Frame 10 — Entretien · Le rapport (10,5–14,5 s) — HERO

- scene: Zoom-through vers le score 7,6/10 qui compte, « Bonne prestation » ; points forts et pistes ; callout « Évaluation des réponses »
- duration: 4s
- transition_in: zoom-through
- status: animated
- src: compositions/entretien.html
- video: entretien
- blueprint: dataviz-countup
- poster: 12.5s

Plan tenu ~1,2 s sur le score et les points forts.

## Frame 11 — Entretien · Signature (14,5–18 s)

- scene: Logo, « Candidatez juste. », bouton « Démarrer la simulation » cliqué ; blur crossfade vers l'accroche
- duration: 3.5s
- transition_in: zoom-out
- status: animated
- src: compositions/entretien.html
- video: entretien
- blueprint: cta-morph-press
- poster: 16s

## Frame 12 — Lettre · Accroche (0–2,2 s)

- scene: Plateau papier, « 03 » fantôme ; « Une lettre qui répond à l'offre » se construit mot à mot
- duration: 2.2s
- transition_in: cut
- status: animated
- src: compositions/lettre.html
- video: lettre
- blueprint: kinetic-type-beats (kinetic-center-build)
- poster: 1.6s

## Frame 13 — Lettre · Le style (2,2–5 s)

- scene: 3D reveal de la page Lettre ; le curseur passe le ton sur « Chaleureux » ; callout « Ton et longueur au choix » ; clic « Générer la lettre »
- duration: 2.8s
- transition_in: 3d-reveal
- status: animated
- src: compositions/lettre.html
- video: lettre
- blueprint: cursor-ui-demo
- poster: 4.2s

## Frame 14 — Lettre · La lettre s'écrit (5–11,5 s) — HERO

- scene: Zoom-through vers « Votre lettre » ; statuts réels puis objet, accroche, corps, conclusion et signature « Alex Moreau » paragraphe par paragraphe ; callout « Accroche, corps et conclusion »
- duration: 6.5s
- transition_in: zoom-through
- status: animated
- src: compositions/lettre.html
- video: lettre
- blueprint: prompt-type-submit-generate (réponse en streaming)
- poster: 9.5s

Chaque section arrive d'un bloc (fondu + glissement), dans l'ordre du flux réel ; la caméra suit la lecture vers le bas sans couper une ligne.

## Frame 15 — Lettre · Copier (11,5–14,5 s)

- scene: Clic « Copier » → « Lettre copiée ✓ » ; callout « Copie et export .txt / .md »
- duration: 3s
- transition_in: cut
- status: animated
- src: compositions/lettre.html
- video: lettre
- blueprint: cursor-ui-demo
- poster: 13.5s

Plan tenu ~1,2 s sur la lettre complète et la barre d'actions.

## Frame 16 — Lettre · Signature (14,5–18 s)

- scene: Logo, « Candidatez juste. », bouton « Rédiger une lettre » cliqué ; blur crossfade vers l'accroche
- duration: 3.5s
- transition_in: zoom-out
- status: animated
- src: compositions/lettre.html
- video: lettre
- blueprint: cta-morph-press
- poster: 16s
