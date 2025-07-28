#!/bin/bash

# Script de build optimisé pour réduire la taille du build
# Objectif: < 512MB

echo "🔧 Build optimisé du backend"
echo "📊 Objectif: < 512MB"
echo "=" * 50

# Vérifier que Docker est installé
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé"
    exit 1
fi

# Nettoyer les images et conteneurs inutiles
echo "🧹 Nettoyage des images Docker inutiles..."
docker system prune -f

# Construire l'image optimisée
echo "🏗️  Construction de l'image optimisée..."
docker build -f Dockerfile.optimized -t cv-offer-compare-backend:optimized .

# Vérifier la taille de l'image
echo "📊 Vérification de la taille de l'image..."
IMAGE_SIZE=$(docker images cv-offer-compare-backend:optimized --format "table {{.Size}}" | tail -n 1)
echo "📦 Taille de l'image: $IMAGE_SIZE"

# Extraire la taille en MB
SIZE_MB=$(echo $IMAGE_SIZE | sed 's/MB//' | sed 's/GB/*1024/' | bc -l 2>/dev/null || echo "0")

if (( $(echo "$SIZE_MB < 512" | bc -l) )); then
    echo "✅ Succès! Taille de l'image: ${SIZE_MB}MB (< 512MB)"
else
    echo "⚠️  Attention: Taille de l'image: ${SIZE_MB}MB (>= 512MB)"
fi

# Afficher les informations sur l'image
echo "📋 Informations sur l'image:"
docker images cv-offer-compare-backend:optimized

# Tester l'image
echo "🧪 Test de l'image..."
docker run --rm -d --name test-backend -p 8000:8000 cv-offer-compare-backend:optimized

# Attendre que le conteneur démarre
sleep 5

# Vérifier que le conteneur fonctionne
if docker ps | grep -q test-backend; then
    echo "✅ Conteneur démarré avec succès"
    
    # Test de santé
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ API accessible"
    else
        echo "⚠️  API non accessible (peut être normal si les modèles ne sont pas téléchargés)"
    fi
    
    # Arrêter le conteneur de test
    docker stop test-backend
else
    echo "❌ Échec du démarrage du conteneur"
fi

echo "🎉 Build terminé!"
echo "📝 Commandes utiles:"
echo "   - Démarrer: docker run -p 8000:8000 cv-offer-compare-backend:optimized"
echo "   - Voir les logs: docker logs <container_id>"
echo "   - Accéder au shell: docker run -it cv-offer-compare-backend:optimized /bin/bash" 