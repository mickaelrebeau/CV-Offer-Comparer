# Vidéos Remotion — landing Talento

Projet autonome pour générer les démos produit de la section `#apercu`.

## Compositions

| ID | Durée | Description |
|---|---|---|
| `AnalysisDemo` | 15 s (450 frames @ 30 fps) | Parcours comparateur CV/offre |
| `InterviewDemo` | 15 s | Simulateur d'entretien + rapport |

## Commandes

```bash
npm i
npm run dev              # Remotion Studio
npm run render:landing   # MP4 + WebM + posters → frontend/public/videos/
```

Ou via le script shell :

```bash
./scripts/render-landing.sh
```

## Sortie

Les assets sont versionnés dans `frontend/public/videos/` :

- `analyse.mp4` / `analyse.webm` + `analyse-poster.webp`
- `entretien.mp4` / `entretien.webm` + `entretien-poster.webp`

Les rendus ne sont **pas** exécutés dans le Dockerfile Railway.
