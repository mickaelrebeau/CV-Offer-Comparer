<template>
  <LegalPageShell
    v-if="locale === 'en'"
    label="Privacy"
    title="Privacy policy"
    description="Data collected, purposes, processors and your rights."
    updated-at="2026-09-28"
  >
    <section>
      <h2>1. Data controller</h2>
      <p>
        <strong>{{ LEGAL_PUBLISHER.name }}</strong> —
        <a :href="`mailto:${LEGAL_PUBLISHER.email}`">{{ LEGAL_PUBLISHER.email }}</a>
      </p>
    </section>

    <section>
      <h2>2. Data processed</h2>
      <h3>User account</h3>
      <ul>
        <li>Email address</li>
        <li>Hashed password (email sign-up) or Google identifier</li>
        <li>Name / avatar, if provided by Google OAuth</li>
        <li>Account creation date</li>
      </ul>
      <h3>Comparison history (signed-in accounts)</h3>
      <ul>
        <li>Excerpts and texts of the job offer / resume linked to the analysis</li>
        <li>JSON summary (scores, match / missing / unclear items)</li>
        <li>Analysis date</li>
      </ul>
      <h3>Interview simulation history (signed-in accounts)</h3>
      <ul>
        <li>Excerpts and texts of the job offer / resume linked to the simulation</li>
        <li>Questions, answers and JSON analysis (score, strengths, suggestions)</li>
        <li>Session duration and date</li>
      </ul>
      <h3>Cover letter history (signed-in accounts)</h3>
      <ul>
        <li>Excerpts and texts of the job offer / resume used to write the letter (the imported file itself is never stored)</li>
        <li>Generated letter (subject, paragraphs, sign-off) and chosen options (tone, length, language)</li>
        <li>Generation date</li>
      </ul>
      <h3>Personal AI API keys (signed-in accounts, optional)</h3>
      <ul>
        <li>Chosen provider (Gemini, OpenAI, Anthropic, DeepSeek, Qwen, Kimi or OpenAI-compatible endpoint), model and, if provided, endpoint URL</li>
        <li>API key, stored <strong>encrypted</strong> only; a masked hint (e.g. <code>sk-••••abcd</code>) is the only part ever displayed</li>
        <li>Active configuration and creation / update dates</li>
      </ul>
      <h3>Email verification and password reset</h3>
      <ul>
        <li>Email address verification date</li>
        <li>Single-use tokens sent by email, stored only as a fingerprint (SHA-256 hash) with their expiry date</li>
      </ul>
      <h3>Free trial (visitors)</h3>
      <ul>
        <li>Technical identifier derived from the IP address and the browser (user agent), used to limit the trial</li>
      </ul>
      <h3>Technical data &amp; analytics</h3>
      <ul>
        <li>IP address and account identifier, used as rate-limiting counters (anti-abuse)</li>
        <li>Temporary Google sign-in data: anti-forgery value (<code>oauth_state</code> cookie) and single-use sign-in code</li>
        <li>Hosting technical logs (Railway)</li>
        <li>Product events and errors via <strong>PostHog</strong> (EU), including the user identifier once signed in</li>
      </ul>
    </section>

    <section>
      <h2>3. Purposes</h2>
      <ul>
        <li>Provide the analysis service, the interview simulator and the cover letter generator</li>
        <li>Authenticate users and keep the requested history</li>
        <li>Verify email addresses and allow password resets</li>
        <li>Prevent abuse (free trial, rate limiting, security)</li>
        <li>Improve the product and diagnose errors (PostHog)</li>
      </ul>
      <p>Main legal basis: performance of the requested service and legitimate interest in security / improvement, in compliance with the GDPR.</p>
    </section>

    <section>
      <h2>4. Transfer to AI providers</h2>
      <p>
        To produce the analysis or the cover letter, the <strong>text of the resume and the job offer</strong> is sent
        to <strong>Google Gemini</strong> (Google AI API) for the duration of the processing. This
        content is not meant to build a public profile; it is necessary for the service to work.
        Please also review Google’s terms for the use of the API.
      </p>
      <p>
        Documents are <strong>not kept as files</strong> on our servers after the analysis
        session, except for the history explicitly saved for signed-in accounts.
      </p>
      <p>
        <strong>Personal API key (BYOK).</strong> If you activate your own key, the texts of your
        resume and job offers are sent to <strong>the provider you chose</strong> (Google, OpenAI,
        Anthropic, DeepSeek, Alibaba Cloud, Moonshot AI or the endpoint you entered) instead of
        Talento’s Gemini account. That provider then processes them under the terms you accepted
        with it, and <strong>bills the calls to you directly</strong>. Your key is used only for
        your own account’s AI calls, can be deleted at any time from your profile (irreversible
        deletion) and is deleted along with your account. The free trial always uses Talento’s
        stack.
      </p>
    </section>

    <section>
      <h2>5. Retention periods</h2>
      <ul>
        <li>Account: until deleted by the user or upon request</li>
        <li>Personal API keys (encrypted): until deleted from the profile or until the account is deleted</li>
        <li>Comparison, interview simulation and cover letter history: until manually deleted (from the dashboard) or until the account is deleted</li>
        <li>Email verification and password reset tokens: valid for 48 h and 60 min respectively; deleted once used, when a new link is sent or when the account is deleted</li>
        <li>Free trial (Redis): short duration (around 24 h depending on configuration)</li>
        <li>Rate-limiting counters (Redis): one minute, or until midnight UTC for daily quotas</li>
        <li>Google sign-in: <code>oauth_state</code> cookie 10 min, sign-in code 60 s</li>
        <li>PostHog analytics: according to the PostHog project’s retention policy</li>
      </ul>
    </section>

    <section>
      <h2>6. Recipients / processors</h2>
      <ul>
        <li><strong>Railway</strong> — application hosting and databases</li>
        <li><strong>Google</strong> — Gemini (analysis) and OAuth (if you sign in with Google)</li>
        <li><strong>The AI provider you choose</strong>, only if you activate a personal API key</li>
        <li><strong>PostHog</strong> — product analytics / errors (EU region)</li>
        <li><strong>Resend</strong> (United States) — sending transactional emails (email verification, password reset): email address and message content, when email sending is enabled</li>
      </ul>
    </section>

    <section>
      <h2>7. Cookies and trackers</h2>
      <p>The service uses the following strictly necessary storage, which does not require consent:</p>
      <ul>
        <li>browser local storage: authentication token (<code>talento_access_token</code>), interface language preference (<code>talento_locale</code>), free trial marker (<code>talento_free_analysis_used</code>), and a temporary copy of the latest interview report (<code>interviewAnalysis</code>, including the resume and job offer texts), deleted as soon as the results are displayed;</li>
        <li>an <code>oauth_state</code> cookie (httpOnly, 10 min), set only during Google sign-in to protect it against forgery;</li>
        <li>the app’s cache (service worker, Cache Storage): only the application’s files (pages, scripts, styles, icons, fonts), to make it load faster and keep it available offline — never API responses or your documents.</li>
      </ul>
      <p>
        For usage analytics, a <strong>consent banner</strong> asks you to accept or decline
        PostHog cookies / storage. If you decline, PostHog may keep anonymized, cookieless
        tracking. The free trial may rely on a server-side technical identifier.
      </p>
    </section>

    <section>
      <h2>8. Your rights</h2>
      <p>
        Under the GDPR, you have the right to access, rectify, erase, restrict, object to and port
        your data, under the conditions provided by law. You can delete your account from the
        Profile page, or write to us at
        <a :href="`mailto:${LEGAL_PUBLISHER.email}`">{{ LEGAL_PUBLISHER.email }}</a>.
        You may also lodge a complaint with the CNIL (cnil.fr), the French data protection
        authority.
      </p>
    </section>

    <section>
      <h2>9. Security</h2>
      <p>
        Reasonable measures: HTTPS, hashed passwords, email links stored only as a fingerprint,
        personal API keys encrypted at rest and never displayed again, authenticated API access
        for protected routes, rate limiting. As no system is infallible, we recommend not uploading unnecessary secrets in
        your resume.
      </p>
    </section>

    <section>
      <h2>10. Changes</h2>
      <p>
        This policy may be updated. The update date is shown at the top of the page. Substantial
        changes will be reflected on this page.
      </p>
    </section>
  </LegalPageShell>

  <LegalPageShell
    v-else
    label="Vie privée"
    title="Politique de confidentialité"
    description="Données collectées, finalités, sous-traitants et vos droits."
    updated-at="2026-09-28"
  >
    <section>
      <h2>1. Responsable du traitement</h2>
      <p>
        <strong>{{ LEGAL_PUBLISHER.name }}</strong> —
        <a :href="`mailto:${LEGAL_PUBLISHER.email}`">{{ LEGAL_PUBLISHER.email }}</a>
      </p>
    </section>

    <section>
      <h2>2. Données traitées</h2>
      <h3>Compte utilisateur</h3>
      <ul>
        <li>Adresse e-mail</li>
        <li>Mot de passe hashé (si inscription e-mail) ou identifiant Google</li>
        <li>Nom / avatar éventuels fournis par Google OAuth</li>
        <li>Date de création du compte</li>
      </ul>
      <h3>Historique des comparaisons (comptes connectés)</h3>
      <ul>
        <li>Extraits et textes d’offre / CV associés à l’analyse</li>
        <li>Résumé JSON (scores, items match / missing / unclear)</li>
        <li>Date de l’analyse</li>
      </ul>
      <h3>Historique des simulations d’entretien (comptes connectés)</h3>
      <ul>
        <li>Extraits et textes d’offre / CV associés à la simulation</li>
        <li>Questions, réponses et analyse JSON (score, points forts, suggestions)</li>
        <li>Durée de la session et date</li>
      </ul>
      <h3>Historique des lettres de motivation (comptes connectés)</h3>
      <ul>
        <li>Extraits et textes d’offre / CV ayant servi à rédiger la lettre (le fichier importé n’est jamais conservé)</li>
        <li>Lettre générée (objet, paragraphes, formule de politesse) et options choisies (ton, longueur, langue)</li>
        <li>Date de génération</li>
      </ul>
      <h3>Clés API IA personnelles (comptes connectés, facultatif)</h3>
      <ul>
        <li>Fournisseur choisi (Gemini, OpenAI, Anthropic, DeepSeek, Qwen, Kimi ou endpoint compatible OpenAI), modèle et, le cas échéant, URL de l’endpoint</li>
        <li>Clé API, conservée uniquement <strong>chiffrée</strong> ; seul un indice masqué (ex. <code>sk-••••abcd</code>) est affiché</li>
        <li>Configuration active et dates de création / mise à jour</li>
      </ul>
      <h3>Vérification de l’adresse e-mail et réinitialisation du mot de passe</h3>
      <ul>
        <li>Date de vérification de l’adresse e-mail</li>
        <li>Jetons à usage unique envoyés par e-mail, conservés uniquement sous forme d’empreinte (hash SHA-256) avec leur date d’expiration</li>
      </ul>
      <h3>Essai gratuit (visiteurs)</h3>
      <ul>
        <li>Identifiant technique dérivé de l’adresse IP et du navigateur (user agent), pour limiter l’essai</li>
      </ul>
      <h3>Données techniques &amp; analytics</h3>
      <ul>
        <li>Adresse IP et identifiant de compte, utilisés comme compteurs de limitation de débit (anti-abus)</li>
        <li>Données temporaires de connexion Google : valeur anti-falsification (cookie <code>oauth_state</code>) et code de connexion à usage unique</li>
        <li>Journaux techniques d’hébergement (Railway)</li>
        <li>Événements produit et erreurs via <strong>PostHog</strong> (UE), y compris identifiant utilisateur après connexion</li>
      </ul>
    </section>

    <section>
      <h2>3. Finalités</h2>
      <ul>
        <li>Fournir le service d’analyse, le simulateur d’entretien et le générateur de lettre de motivation</li>
        <li>Authentifier les utilisateurs et conserver l’historique demandé</li>
        <li>Vérifier les adresses e-mail et permettre la réinitialisation du mot de passe</li>
        <li>Limiter les abus (essai gratuit, limitation de débit, sécurité)</li>
        <li>Améliorer le produit et diagnostiquer les erreurs (PostHog)</li>
      </ul>
      <p>Base légale principale : exécution du service demandé et intérêt légitime pour la sécurité / amélioration, dans le respect du RGPD.</p>
    </section>

    <section>
      <h2>4. Transfert vers les fournisseurs d’IA</h2>
      <p>
        Pour produire l’analyse ou la lettre de motivation, le <strong>texte du CV et de l’offre</strong> est transmis à
        <strong>Google Gemini</strong> (API Google AI) le temps du traitement. Ce contenu n’est
        pas destiné à constituer un profil public ; il est nécessaire au fonctionnement du
        service. Consultez également les conditions Google relatives à l’usage de l’API.
      </p>
      <p>
        Les documents ne sont <strong>pas conservés comme fichiers</strong> sur nos serveurs après
        la session d’analyse, hors historique explicitement enregistré pour les comptes connectés.
      </p>
      <p>
        <strong>Clé API personnelle (BYOK).</strong> Si vous activez votre propre clé, les textes de
        votre CV et des offres sont transmis <strong>au fournisseur que vous avez choisi</strong>
        (Google, OpenAI, Anthropic, DeepSeek, Alibaba Cloud, Moonshot AI ou l’endpoint renseigné) au
        lieu du compte Gemini de Talento. Ce fournisseur les traite selon les conditions que vous avez
        acceptées auprès de lui et <strong>vous facture directement</strong> les appels. Votre clé
        n’est utilisée que pour les appels IA de votre compte, peut être supprimée à tout moment
        depuis votre profil (suppression irréversible) et est effacée avec votre compte. L’essai
        gratuit utilise toujours la stack de Talento.
      </p>
    </section>

    <section>
      <h2>5. Durées de conservation</h2>
      <ul>
        <li>Compte : jusqu’à suppression par l’utilisateur ou demande</li>
        <li>Clés API personnelles (chiffrées) : jusqu’à suppression depuis le profil ou suppression du compte</li>
        <li>Historique des comparaisons, des simulations d’entretien et des lettres de motivation : jusqu’à suppression manuelle (depuis le tableau de bord) ou suppression du compte</li>
        <li>Jetons de vérification d’e-mail et de réinitialisation : valables respectivement 48 h et 60 min ; supprimés à l’utilisation, à l’envoi d’un nouveau lien ou à la suppression du compte</li>
        <li>Essai gratuit (Redis) : durée courte (ordre de 24 h selon configuration)</li>
        <li>Compteurs de limitation de débit (Redis) : une minute, ou jusqu’à minuit UTC pour les quotas journaliers</li>
        <li>Connexion Google : cookie <code>oauth_state</code> 10 min, code de connexion 60 s</li>
        <li>Analytics PostHog : selon la politique de rétention du projet PostHog</li>
      </ul>
    </section>

    <section>
      <h2>6. Destinataires / sous-traitants</h2>
      <ul>
        <li><strong>Railway</strong> — hébergement applicatif et bases</li>
        <li><strong>Google</strong> — Gemini (analyse) et OAuth (si connexion Google)</li>
        <li><strong>Le fournisseur d’IA de votre choix</strong>, uniquement si vous activez une clé API personnelle</li>
        <li><strong>PostHog</strong> — analytics produit / erreurs (région UE)</li>
        <li><strong>Resend</strong> (États-Unis) — envoi des e-mails transactionnels (vérification d’adresse, réinitialisation du mot de passe) : adresse e-mail et contenu du message, lorsque l’envoi d’e-mails est activé</li>
      </ul>
    </section>

    <section>
      <h2>7. Cookies et traceurs</h2>
      <p>Le service utilise les stockages strictement nécessaires suivants, qui ne requièrent pas de consentement :</p>
      <ul>
        <li>stockage local du navigateur : jeton d’authentification (<code>talento_access_token</code>), préférence de langue de l’interface (<code>talento_locale</code>), indicateur d’essai gratuit (<code>talento_free_analysis_used</code>) et copie temporaire du dernier rapport d’entretien (<code>interviewAnalysis</code>, qui contient les textes du CV et de l’offre), effacée dès l’affichage des résultats ;</li>
        <li>un cookie <code>oauth_state</code> (httpOnly, 10 min), posé uniquement pendant la connexion Google pour la protéger contre la falsification ;</li>
        <li>le cache de l’application (service worker, Cache Storage) : uniquement les fichiers de l’application (pages, scripts, styles, icônes, polices), pour accélérer le chargement et la rendre disponible hors ligne — jamais les réponses de l’API ni vos documents.</li>
      </ul>
      <p>
        Pour la mesure d’usage, une <strong>bannière de consentement</strong> vous demande
        d’accepter ou de refuser les cookies / le stockage PostHog. En cas de refus, PostHog peut
        continuer un suivi anonymisé sans cookies (mode cookieless). L’essai gratuit peut
        s’appuyer sur un identifiant technique côté serveur.
      </p>
    </section>

    <section>
      <h2>8. Vos droits</h2>
      <p>
        Conformément au RGPD, vous disposez d’un droit d’accès, de rectification, d’effacement,
        de limitation, d’opposition et de portabilité, dans les conditions prévues par la loi.
        Vous pouvez supprimer votre compte depuis la page Profil, ou nous écrire à
        <a :href="`mailto:${LEGAL_PUBLISHER.email}`">{{ LEGAL_PUBLISHER.email }}</a>.
        Vous pouvez également introduire une réclamation auprès de la CNIL (cnil.fr).
      </p>
    </section>

    <section>
      <h2>9. Sécurité</h2>
      <p>
        Mesures raisonnables : HTTPS, mots de passe hashés, liens envoyés par e-mail conservés
        uniquement sous forme d’empreinte, clés API personnelles chiffrées au repos et jamais
        réaffichées, accès API authentifié pour les routes protégées,
        limitation de débit. Aucun système n’étant infaillible, nous vous invitons à ne pas
        téléverser de secrets inutiles dans vos CV.
      </p>
    </section>

    <section>
      <h2>10. Évolutions</h2>
      <p>
        Cette politique peut être mise à jour. La date de mise à jour figure en tête de page.
        Les changements substantiels seront reflétés sur cette page.
      </p>
    </section>
  </LegalPageShell>
</template>

<script setup lang="ts">
import LegalPageShell from '@/components/LegalPageShell.vue'
import { useLocale } from '@/i18n/useLocale'
import { LEGAL_PUBLISHER } from '@/lib/site'

// Titre, description et canonical : App.vue (meta.seo = 'privacy')
const { locale } = useLocale()
</script>
