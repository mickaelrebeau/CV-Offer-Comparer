#!/usr/bin/env python3
"""
Script d'installation des modèles locaux pour la comparaison sémantique
"""

import os
import sys
from transformers import AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer

def download_models():
    """Télécharge les modèles nécessaires"""
    
    print("🚀 Démarrage du téléchargement des modèles...")
    
    models_to_download = [
        {
            "name": "CamemBERT",
            "model_id": "camembert-base",
            "type": "transformers"
        },
        {
            "name": "Sentence Transformer (MPNet)",
            "model_id": "sentence-transformers/all-mpnet-base-v2",
            "type": "sentence_transformer"
        }
    ]
    
    for model_info in models_to_download:
        print(f"\n📥 Téléchargement de {model_info['name']}...")
        
        try:
            if model_info['type'] == 'transformers':
                # Télécharger le tokenizer
                print(f"  - Tokenizer...")
                tokenizer = AutoTokenizer.from_pretrained(model_info['model_id'])
                
                # Télécharger le modèle
                print(f"  - Modèle...")
                model = AutoModel.from_pretrained(model_info['model_id'])
                
                print(f"✅ {model_info['name']} téléchargé avec succès!")
                
            elif model_info['type'] == 'sentence_transformer':
                # Télécharger le modèle Sentence Transformer
                print(f"  - Modèle Sentence Transformer...")
                model = SentenceTransformer(model_info['model_id'])
                
                print(f"✅ {model_info['name']} téléchargé avec succès!")
                
        except Exception as e:
            print(f"❌ Erreur lors du téléchargement de {model_info['name']}: {e}")
            return False
    
    print("\n🎉 Tous les modèles ont été téléchargés avec succès!")
    return True

def test_models():
    """Test rapide des modèles téléchargés"""
    
    print("\n🧪 Test des modèles téléchargés...")
    
    try:
        # Test CamemBERT
        print("  - Test CamemBERT...")
        tokenizer = AutoTokenizer.from_pretrained('camembert-base')
        model = AutoModel.from_pretrained('camembert-base')
        
        # Test simple
        text = "Bonjour, comment allez-vous?"
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        
        with model.no_grad():
            outputs = model(**inputs)
            embeddings = outputs.last_hidden_state.mean(dim=1)
        
        print(f"    ✅ Embeddings générés: {embeddings.shape}")
        
        # Test Sentence Transformer
        print("  - Test Sentence Transformer (MPNet)...")
        st_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
        
        embeddings = st_model.encode([text])
        print(f"    ✅ Embeddings générés: {embeddings.shape}")
        
        # Test de comparaison sémantique
        print("  - Test de comparaison sémantique...")
        text1 = "Python développeur"
        text2 = "Développeur Python"
        
        embeddings1 = st_model.encode([text1])
        embeddings2 = st_model.encode([text2])
        
        from sklearn.metrics.pairwise import cosine_similarity
        similarity = cosine_similarity(embeddings1, embeddings2)[0][0]
        print(f"    ✅ Similarité calculée: {similarity:.3f}")
        
        print("\n✅ Tous les tests réussis!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors des tests: {e}")
        return False

def check_dependencies():
    """Vérifie que toutes les dépendances sont installées"""
    
    print("🔍 Vérification des dépendances...")
    
    required_packages = [
        'torch',
        'transformers', 
        'sentence_transformers',
        'numpy',
        'sklearn',
        'pickle',
        'hashlib'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'pickle':
                import pickle
            elif package == 'hashlib':
                import hashlib
            else:
                __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - MANQUANT")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Packages manquants: {', '.join(missing_packages)}")
        print("Veuillez installer les dépendances avec: pip install -r requirements.txt")
        return False
    
    print("✅ Toutes les dépendances sont installées")
    return True

def main():
    """Fonction principale"""
    
    print("🔧 Installation des modèles sémantiques pour CV-Offer-Compare")
    print("=" * 60)
    
    # Vérifier les dépendances
    if not check_dependencies():
        return False
    
    # Télécharger les modèles
    if not download_models():
        print("❌ Échec du téléchargement des modèles")
        return False
    
    # Tester les modèles
    if not test_models():
        print("❌ Échec des tests des modèles")
        return False
    
    print("\n🎉 Installation terminée avec succès!")
    print("\n📝 Prochaines étapes:")
    print("1. Redémarrez votre serveur backend")
    print("2. Testez avec: python test_improved_semantic.py")
    print("3. Les modèles sont maintenant utilisés pour la comparaison sémantique améliorée")
    print("\n💡 Améliorations apportées:")
    print("   - Modèle Sentence Transformer plus performant (MPNet)")
    print("   - Cache d'embeddings pour améliorer les performances")
    print("   - Normalisation de texte avancée")
    print("   - Pondération multi-modèles")
    print("   - Relations entre technologies")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 