#!/bin/bash

echo "🚀 Démarrage du build pour CV Offer Compare Backend"

# Vérifier la version de Python
python --version

# Installer les dépendances
echo "📦 Installation des dépendances..."
pip install -r requirements.txt

# Vérifier que l'application peut démarrer
echo "🔍 Test de démarrage de l'application..."
python -c "from app import app; print('✅ Application importée avec succès')"

# Vérifier les routes SSE
echo "🔍 Vérification des routes SSE..."
python -c "
from app.routers.compare import router
routes = [route.path for route in router.routes]
sse_routes = [r for r in routes if 'stream' in r]
print(f'✅ Routes SSE trouvées: {sse_routes}')
"

echo "✅ Build terminé avec succès!" 