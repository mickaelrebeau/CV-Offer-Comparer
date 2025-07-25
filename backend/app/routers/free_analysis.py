import json
import asyncio
import hashlib
import time
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Request, UploadFile, File
from fastapi.responses import StreamingResponse
from app.models.comparison import ComparisonRequest
from app.models.upload import PDFUploadResponse
from app.services.comparison_service import ComparisonService
from app.services.auth_service import AuthService
from app.services.redis_service import redis_service
from app.services.upload_service import UploadService

router = APIRouter()
comparison_service = ComparisonService()
auth_service = AuthService()
upload_service = UploadService()

def get_client_identifier(request: Request) -> str:
    """Génère un identifiant unique pour le client basé sur l'IP et l'User-Agent"""
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "")
    identifier = f"{client_ip}:{user_agent}"
    return hashlib.md5(identifier.encode()).hexdigest()

def check_free_analysis_limit(client_id: str) -> bool:
    """Vérifie si le client peut faire une analyse gratuite"""
    return redis_service.check_free_analysis_available(client_id)

def mark_free_analysis_used(client_id: str):
    """Marque l'analyse gratuite comme utilisée pour ce client"""
    redis_service.mark_free_analysis_used(client_id)

@router.post("/free-compare-stream")
async def free_compare_cv_offer_stream(
    request: ComparisonRequest,
    http_request: Request
):
    """Compare un CV avec une offre d'emploi gratuitement (limité à une fois par client)"""
    
    # Vérifier la limite d'analyse gratuite
    client_id = get_client_identifier(http_request)
    
    if not check_free_analysis_limit(client_id):
        raise HTTPException(
            status_code=429,
            detail="Vous avez déjà utilisé votre analyse gratuite. Veuillez créer un compte pour continuer."
        )
    
    # Marquer l'analyse comme utilisée
    mark_free_analysis_used(client_id)
    
    async def generate_comparison():
        try:
            # Envoyer le statut initial
            yield f"data: {json.dumps({'type': 'status', 'message': 'Début de l\'analyse gratuite...'})}\n\n"
            
            # Extraire les compétences de l'offre
            yield f"data: {json.dumps({'type': 'status', 'message': 'Extraction des compétences de l\'offre...'})}\n\n"
            offer_skills = comparison_service.ai_service.extract_skills(request.offer_text)
            yield f"data: {json.dumps({'type': 'status', 'message': f'Compétences de l\'offre trouvées: {len(offer_skills)}'})}\n\n"
            
            # Extraire les compétences du CV
            yield f"data: {json.dumps({'type': 'status', 'message': 'Extraction des compétences du CV...'})}\n\n"
            cv_skills = comparison_service.ai_service.extract_skills(request.cv_text)
            yield f"data: {json.dumps({'type': 'status', 'message': f'Compétences du CV trouvées: {len(cv_skills)}'})}\n\n"
            
            comparison_items = []
            total_items = len(offer_skills)
            matches = 0
            missing = 0
            unclear = 0
            
            yield f"data: {json.dumps({'type': 'status', 'message': f'Début de la comparaison de {total_items} éléments...'})}\n\n"
            
            # Traitement par batch pour optimiser les performances
            batch_size = 5
            for i in range(0, total_items, batch_size):
                batch = offer_skills[i:i + batch_size]
                
                for j, skill in enumerate(batch):
                    current_index = i + j
                    
                    # Envoyer le progrès
                    progress = (current_index / total_items) * 100 if total_items > 0 else 0
                    yield f"data: {json.dumps({'type': 'progress', 'value': progress, 'current': current_index + 1, 'total': total_items})}\n\n"
                    
                    # Trouver la meilleure correspondance
                    best_match = None
                    best_similarity = 0.0
                    
                    for cv_skill in cv_skills:
                        similarity = comparison_service.ai_service.compare_semantic(skill, cv_skill)
                        if similarity > best_similarity:
                            best_similarity = similarity
                            best_match = cv_skill
                    
                    # Déterminer le statut
                    if best_similarity > 0.6:
                        status = "match"
                        matches += 1
                        cv_text = best_match
                    elif best_similarity > 0.3:
                        status = "unclear"
                        unclear += 1
                        cv_text = best_match if best_match else None
                    else:
                        status = "missing"
                        missing += 1
                        cv_text = None
                    
                    # Générer des suggestions si nécessaire
                    suggestions = []
                    if status in ["missing", "unclear"]:
                        suggestions = comparison_service.ai_service.generate_suggestions(skill, status)
                    
                    from app.models.comparison import ComparisonItem
                    item = ComparisonItem(
                        id=str(current_index),
                        category="compétences techniques",
                        offerText=skill,
                        cvText=cv_text,
                        status=status,
                        confidence=best_similarity,
                        suggestions=suggestions if suggestions else None
                    )
                    comparison_items.append(item)
                    
                    # Envoyer l'élément immédiatement
                    yield f"data: {json.dumps({'type': 'item', 'item': item.dict()})}\n\n"
                
                # Pause plus courte entre les batches
                await asyncio.sleep(0.05)
            
            # Calculer le pourcentage de correspondance
            match_percentage = (matches / total_items) if total_items > 0 else 0.0
            
            from app.models.comparison import ComparisonSummary
            summary = ComparisonSummary(
                totalItems=total_items,
                matches=matches,
                missing=missing,
                unclear=unclear,
                matchPercentage=match_percentage
            )
            
            # Envoyer le résumé final
            yield f"data: {json.dumps({'type': 'summary', 'summary': summary.dict()})}\n\n"
            yield f"data: {json.dumps({'type': 'complete'})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        generate_comparison(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "*"
        }
    )

@router.get("/free-analysis-status")
async def get_free_analysis_status(http_request: Request):
    """Vérifie le statut de l'analyse gratuite pour le client"""
    client_id = get_client_identifier(http_request)
    can_use_free = check_free_analysis_limit(client_id)
    
    # Récupérer les informations détaillées si l'analyse a été utilisée
    analysis_info = None
    if not can_use_free:
        analysis_info = redis_service.get_free_analysis_info(client_id)
    
    return {
        "can_use_free_analysis": can_use_free,
        "client_id": client_id,
        "message": "Vous pouvez faire une analyse gratuite" if can_use_free else "Vous avez déjà utilisé votre analyse gratuite",
        "analysis_info": analysis_info
    }

@router.post("/reset-free-analysis")
async def reset_free_analysis(http_request: Request):
    """Réinitialise l'analyse gratuite pour le client (pour les tests)"""
    client_id = get_client_identifier(http_request)
    
    success = redis_service.reset_free_analysis(client_id)
    
    return {
        "message": "Analyse gratuite réinitialisée" if success else "Erreur lors de la réinitialisation",
        "client_id": client_id,
        "success": success
    }

@router.get("/free-analysis-stats")
async def get_free_analysis_stats():
    """Récupère les statistiques globales des analyses gratuites"""
    stats = redis_service.get_stats()
    redis_health = redis_service.health_check()
    
    return {
        "stats": stats,
        "redis_health": redis_health,
        "timestamp": datetime.now().isoformat()
    }

@router.post("/free-upload-cv", response_model=PDFUploadResponse)
async def free_upload_cv_pdf(
    http_request: Request,
    file: UploadFile = File(...)
):
    """Upload et extraction de texte d'un CV PDF pour l'essai gratuit"""
    
    # Vérifier le type de fichier
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Seuls les fichiers PDF sont acceptés")
    
    # Vérifier la taille du fichier
    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Le fichier est trop volumineux (max 10MB)")
    
    try:
        # Extraire le texte du PDF
        extracted_text = upload_service.extract_text_from_pdf(file)
        
        if not extracted_text.strip():
            return PDFUploadResponse(
                success=False,
                text="",
                message="Aucun texte n'a pu être extrait du PDF"
            )
        
        return PDFUploadResponse(
            success=True,
            text=extracted_text,
            message=f"Texte extrait avec succès ({len(extracted_text)} caractères)"
        )
        
    except Exception as e:
        return PDFUploadResponse(
            success=False,
            text="",
            message=f"Erreur lors de l'extraction: {str(e)}"
        ) 