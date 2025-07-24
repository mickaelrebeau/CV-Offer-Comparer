#!/bin/bash

# Script de build personnalisé pour Render
echo "🚀 Démarrage du build..."

# Mettre à jour pip
pip install --upgrade pip

# Installer les dépendances système nécessaires
apt-get update -y
apt-get install -y build-essential

# Installer les dépendances Python
echo "📦 Installation des dépendances Python..."
pip install -r requirements.txt

echo "✅ Build terminé avec succès!" 