# Vidéos de démo — landing Talento (HyperFrames)

Trois démos produit de 18 s, muettes et en boucle, pour la section « Aperçu réel » de la landing, en français et en anglais :

| Démo | Contenu |
|---|---|
| `analyse` | Comparateur CV ↔ offre : saisie, analyse en streaming, score ATS, rapport, reformulation |
| `entretien` | Simulateur : questions générées, réponse minutée, rapport noté |
| `lettre` | Générateur de lettre de motivation : style, rédaction paragraphe par paragraphe, copie |

Chaque vidéo : accroche titrée → l'app en 3D → le résultat (zoom-through) → le détail utile → signature « Candidatez juste. » → boucle.

## Structure

- `index.html` — composition unique ; variables `demo` (`analyse` / `entretien` / `lettre`) et `lang` (`fr` / `en`).
- `assets/demos.js` — pages de l'app reconstruites en HTML + scénarios minutés (caméra, curseur, callouts, transitions).
- `assets/talento.css` — tokens et composants repris de l'app (`frontend/tailwind.config.js`), polices Geist locales.
- `assets/content.js` — **généré** par `scripts/build-content.py` : libellés réels de l'app (`frontend/src/locales`), statuts du backend, données anonymisées.
- `data/inputs.json` — CV et offre **anonymisés** (« Alex Moreau », éditeur SaaS du secteur public).
- `BRIEF.md`, `STORYBOARD.md`, `storyboard.html` — brief, plan et planche d'esquisses validés.

## Commandes

```bash
python3 scripts/build-content.py        # après une modification des locales de l'app
npx hyperframes preview                 # Studio (choisir la démo et la langue dans les variables)
scripts/qa.sh lettre en check           # contrôle d'une combinaison (check / snapshot)
scripts/render-all.sh                   # 6 rendus + MP4/WebM/posters → frontend/public/videos/
```

`scripts/render-all.sh` demande ffmpeg (libx264, libvpx-vp9) et `cwebp`. Les masters vont dans `renders/` (ignoré par git) ; seuls les fichiers web sont versionnés.

## Règles

- L'UI montrée est celle de l'app : libellés i18n réels, comportements réels (pas de « Copié ✓ » là où l'app n'en affiche pas).
- Aucune donnée personnelle réelle : le CV et l'offre d'origine (`cv.txt`, `offre.txt` à la racine) ne sont jamais versionnés.
- Rendu déterministe : GSAP et polices locaux, aucun appel réseau.
