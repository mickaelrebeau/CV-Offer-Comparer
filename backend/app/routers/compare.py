import json
import asyncio
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.comparison import ComparisonRequest
from app.services.comparison_service import ComparisonService
from app.services.auth_service import AuthService

router = APIRouter()
security = HTTPBearer()
auth_service = AuthService()
comparison_service = ComparisonService()

@router.get("/test-stream")
async def test_stream():
    """Route de test pour vérifier que les SSE fonctionnent"""
    
    async def generate_test():
        try:
            for i in range(10):
                yield f"data: {json.dumps({'type': 'status', 'message': f'Test message {i + 1}/10'})}\n\n"
                yield f"data: {json.dumps({'type': 'progress', 'value': (i + 1) * 10, 'current': i + 1, 'total': 10})}\n\n"
                await asyncio.sleep(0.5)
            
            yield f"data: {json.dumps({'type': 'complete'})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        generate_test(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "*"
        }
    )

@router.post("/compare-stream")
async def compare_cv_offer_stream(
    request: ComparisonRequest, 
    user=Depends(auth_service.verify_token)
):
    """Compare un CV avec une offre d'emploi avec streaming des résultats"""
    
    async def generate_comparison():
        try:
            # Envoyer le statut initial
            yield f"data: {json.dumps({'type': 'status', 'message': 'Début de l\'analyse...'})}\n\n"
            
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
                        category="compétences techniques",  # Simplifié pour l'exemple
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