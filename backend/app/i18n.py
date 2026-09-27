"""Messages de l'API traduisibles (fr/en).

Contrat : la langue est négociée via l'en-tête `Accept-Language` (le front envoie la langue de
l'interface). Les erreurs exposées au client sont des `ApiError` : le JSON renvoyé contient
`detail` (message traduit) et `code` (identifiant stable, à utiliser côté client pour la logique).
"""

from fastapi import HTTPException, Request

SUPPORTED_LOCALES = ("fr", "en")
DEFAULT_LOCALE = "fr"

MESSAGES: dict[str, dict[str, str]] = {
    # Authentification
    "auth.email_taken": {
        "fr": "Un compte existe déjà avec cet email",
        "en": "An account already exists with this email",
    },
    "auth.invalid_credentials": {
        "fr": "Email ou mot de passe incorrect",
        "en": "Incorrect email or password",
    },
    "auth.invalid_token": {"fr": "Token invalide", "en": "Invalid token"},
    "auth.user_not_found": {"fr": "Utilisateur non trouvé", "en": "User not found"},
    "auth.email_not_verified": {
        "fr": "Confirmez votre adresse e-mail pour utiliser cette fonctionnalité.",
        "en": "Confirm your email address to use this feature.",
    },
    "auth.invalid_reset_link": {
        "fr": "Lien de réinitialisation invalide ou expiré",
        "en": "Invalid or expired reset link",
    },
    "auth.invalid_verification_link": {
        "fr": "Lien de vérification invalide ou expiré",
        "en": "Invalid or expired verification link",
    },
    "auth.invalid_login_code": {
        "fr": "Code de connexion invalide ou expiré",
        "en": "Invalid or expired sign-in code",
    },
    "auth.google_not_configured": {
        "fr": "Google OAuth non configuré (GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET)",
        "en": "Google OAuth is not configured (GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET)",
    },
    "auth.google_exchange_failed": {
        "fr": "Échec de l'échange du code Google",
        "en": "Google code exchange failed",
    },
    "auth.google_token_missing": {"fr": "Token Google manquant", "en": "Missing Google token"},
    "auth.google_invalid_token": {"fr": "ID token Google invalide", "en": "Invalid Google ID token"},
    "auth.google_invalid_audience": {"fr": "Audience Google invalide", "en": "Invalid Google audience"},
    "auth.google_email_not_verified": {"fr": "Email Google non vérifié", "en": "Google email not verified"},
    "auth.google_incomplete_profile": {"fr": "Profil Google incomplet", "en": "Incomplete Google profile"},
    "auth.forgot_password_sent": {
        "fr": "Si un compte existe pour cette adresse, un e-mail de réinitialisation vient d'être envoyé.",
        "en": "If an account exists for this address, a reset email has just been sent.",
    },
    "auth.already_verified": {"fr": "Adresse e-mail déjà vérifiée", "en": "Email address already verified"},
    "auth.verification_sent": {"fr": "E-mail de vérification envoyé", "en": "Verification email sent"},
    "auth.account_deleted": {"fr": "Compte supprimé", "en": "Account deleted"},
    # Historique
    "history.comparison_not_found": {"fr": "Comparaison introuvable", "en": "Comparison not found"},
    "history.interview_not_found": {"fr": "Entretien introuvable", "en": "Interview not found"},
    "history.cover_letter_not_found": {"fr": "Lettre de motivation introuvable", "en": "Cover letter not found"},
    # Upload / extraction
    "upload.only_pdf": {"fr": "Seuls les fichiers PDF sont acceptés", "en": "Only PDF files are accepted"},
    "upload.cv_format": {"fr": "Le CV doit être au format PDF ou TXT", "en": "The resume must be a PDF or TXT file"},
    "upload.too_large": {
        "fr": "Le fichier est trop volumineux (max {max_mb} Mo)",
        "en": "The file is too large ({max_mb} MB max)",
    },
    "upload.empty_file": {"fr": "Le fichier CV est vide", "en": "The resume file is empty"},
    "upload.pdf_unreadable": {
        "fr": "PDF illisible ou corrompu. Réexportez votre CV en PDF, ou collez son texte directement.",
        "en": "Unreadable or corrupted PDF. Export your resume to PDF again, or paste its text directly.",
    },
    "upload.pdf_no_text": {
        "fr": "Ce PDF ne contient pas de texte lisible (PDF scanné ou image ?). "
        "Exportez votre CV en PDF texte, ou collez son texte directement.",
        "en": "This PDF contains no readable text (scanned PDF or image?). "
        "Export your resume as a text PDF, or paste its text directly.",
    },
    "upload.extracted": {
        "fr": "Texte extrait avec succès ({count} caractères)",
        "en": "Text extracted successfully ({count} characters)",
    },
    # Analyse (SSE)
    "analysis.start": {"fr": "Début de l'analyse…", "en": "Starting the analysis…"},
    "analysis.start_free": {"fr": "Début de l'analyse gratuite…", "en": "Starting the free analysis…"},
    "analysis.gemini": {
        "fr": "Analyse ATS par Gemini (extraction + matching)…",
        "en": "ATS analysis by Gemini (extraction + matching)…",
    },
    "analysis.streaming": {
        "fr": "Exigences analysées : {total} — diffusion des résultats…",
        "en": "Requirements analyzed: {total} — streaming results…",
    },
    "analysis.failed": {
        "fr": "L'analyse a échoué. Réessayez dans un instant.",
        "en": "The analysis failed. Please try again in a moment.",
    },
    # Essai gratuit
    "free.already_used": {
        "fr": "Vous avez déjà utilisé votre analyse gratuite. Veuillez créer un compte pour continuer.",
        "en": "You have already used your free analysis. Please create an account to continue.",
    },
    "free.available": {"fr": "Vous pouvez faire une analyse gratuite", "en": "You can run one free analysis"},
    "free.used": {"fr": "Vous avez déjà utilisé votre analyse gratuite", "en": "You have already used your free analysis"},
    # Entretien
    "interview.questions_generated": {
        "fr": "{count} questions générées avec succès",
        "en": "{count} questions generated successfully",
    },
    "interview.questions_failed": {
        "fr": "Erreur lors de la génération des questions",
        "en": "Error while generating the questions",
    },
    "interview.analysis_failed": {
        "fr": "Erreur lors de l'analyse des réponses",
        "en": "Error while analyzing the answers",
    },
    "interview.job_empty": {
        "fr": "Veuillez fournir une description de l'offre d'emploi",
        "en": "Please provide a job offer description",
    },
    "interview.invalid_payload": {"fr": "Format JSON invalide", "en": "Invalid JSON format"},
    # Lettre de motivation
    "cover_letter.start": {"fr": "Lecture du CV et de l'offre…", "en": "Reading the resume and the job offer…"},
    "cover_letter.gemini": {
        "fr": "Rédaction de la lettre par Gemini…",
        "en": "Gemini is writing the letter…",
    },
    "cover_letter.writing": {"fr": "Mise en forme de la lettre…", "en": "Formatting the letter…"},
    "cover_letter.failed": {
        "fr": "La génération de la lettre a échoué. Réessayez dans un instant.",
        "en": "The cover letter could not be generated. Please try again in a moment.",
    },
    "cover_letter.cv_missing": {
        "fr": "Veuillez fournir votre CV (fichier PDF / TXT ou texte)",
        "en": "Please provide your resume (PDF / TXT file or text)",
    },
    "cover_letter.text_too_long": {
        "fr": "Le CV et l'offre sont limités à {max_chars} caractères chacun",
        "en": "The resume and the job offer are limited to {max_chars} characters each",
    },
    "cover_letter.invalid_option": {
        "fr": "Ton, longueur ou langue de lettre invalide",
        "en": "Invalid letter tone, length or language",
    },
    # Limites
    "rate.too_many": {
        "fr": "Trop de requêtes. Réessayez dans un instant.",
        "en": "Too many requests. Please try again in a moment.",
    },
    "rate.too_many_ip": {
        "fr": "Trop de requêtes depuis cette adresse IP. Réessayez dans un instant.",
        "en": "Too many requests from this IP address. Please try again in a moment.",
    },
    "rate.daily_quota": {
        "fr": "Quota journalier atteint. Réessayez demain.",
        "en": "Daily quota reached. Please try again tomorrow.",
    },
}


def negotiate_locale(accept_language: str | None) -> str:
    """Première langue supportée de l'en-tête Accept-Language (poids q respectés), sinon fr."""
    if not accept_language:
        return DEFAULT_LOCALE
    candidates = []
    for index, part in enumerate(accept_language.split(",")):
        tag, _, params = part.strip().partition(";")
        quality = 1.0
        if params.strip().startswith("q="):
            try:
                quality = float(params.strip()[2:])
            except ValueError:
                quality = 0.0
        candidates.append((-quality, index, tag.strip().lower().split("-")[0]))
    for _, _, language in sorted(candidates):
        if language in SUPPORTED_LOCALES:
            return language
    return DEFAULT_LOCALE


def request_locale(request: Request) -> str:
    """Dépendance FastAPI : langue de la requête."""
    return negotiate_locale(request.headers.get("accept-language"))


def t(code: str, locale: str = DEFAULT_LOCALE, **params) -> str:
    messages = MESSAGES[code]
    return messages.get(locale, messages[DEFAULT_LOCALE]).format(**params)


class ApiError(HTTPException):
    """Erreur exposée au client : traduite à la réponse selon Accept-Language."""

    def __init__(self, status_code: int, code: str, headers: dict | None = None, **params):
        # `detail` en français par défaut (logs, appels internes) ; la réponse HTTP est traduite
        super().__init__(status_code=status_code, detail=t(code, **params), headers=headers)
        self.code = code
        self.params = params
