<template>
  <LegalPageShell
    v-if="locale === 'en'"
    label="Privacy"
    title="Privacy policy"
    description="Data collected, purposes, processors and your rights."
    updated-at="2026-08-03"
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
      <h3>Free trial (visitors)</h3>
      <ul>
        <li>Technical token / identifier (Redis or equivalent) used to limit the trial</li>
      </ul>
      <h3>Technical data &amp; analytics</h3>
      <ul>
        <li>Hosting technical logs (Railway)</li>
        <li>Product events and errors via <strong>PostHog</strong> (EU), including the user identifier once signed in</li>
      </ul>
    </section>

    <section>
      <h2>3. Purposes</h2>
      <ul>
        <li>Provide the analysis service and the interview simulator</li>
        <li>Authenticate users and keep the requested history</li>
        <li>Prevent abuse (free trial, security)</li>
        <li>Improve the product and diagnose errors (PostHog)</li>
      </ul>
      <p>Main legal basis: performance of the requested service and legitimate interest in security / improvement, in compliance with the GDPR.</p>
    </section>

    <section>
      <h2>4. Transfer to Google Gemini</h2>
      <p>
        To produce the analysis, the <strong>text of the resume and the job offer</strong> is sent
        to <strong>Google Gemini</strong> (Google AI API) for the duration of the processing. This
        content is not meant to build a public profile; it is necessary for the service to work.
        Please also review Google’s terms for the use of the API.
      </p>
      <p>
        Documents are <strong>not kept as files</strong> on our servers after the analysis
        session, except for the history explicitly saved for signed-in accounts.
      </p>
    </section>

    <section>
      <h2>5. Retention periods</h2>
      <ul>
        <li>Account: until deleted by the user or upon request</li>
        <li>Comparison and interview simulation history: until manually deleted or until the account is deleted</li>
        <li>Free trial (Redis): short duration (around 24 h depending on configuration)</li>
        <li>PostHog analytics: according to the PostHog project’s retention policy</li>
      </ul>
    </section>

    <section>
      <h2>6. Recipients / processors</h2>
      <ul>
        <li><strong>Railway</strong> — application hosting and databases</li>
        <li><strong>Google</strong> — Gemini (analysis) and OAuth (if you sign in with Google)</li>
        <li><strong>PostHog</strong> — product analytics / errors (EU region)</li>
      </ul>
    </section>

    <section>
      <h2>7. Cookies and trackers</h2>
      <p>
        The service uses the browser’s local storage for the JWT authentication token (required
        for your account to work). For usage analytics, a <strong>consent banner</strong> asks you
        to accept or decline PostHog cookies / storage. If you decline, PostHog may keep
        anonymized, cookieless tracking. The free trial may rely on a server-side technical
        identifier.
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
        Reasonable measures: HTTPS, hashed passwords, authenticated API access for protected
        routes. As no system is infallible, we recommend not uploading unnecessary secrets in
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
    updated-at="2026-08-03"
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
      <h3>Essai gratuit (visiteurs)</h3>
      <ul>
        <li>Jeton / identifiant technique (Redis ou équivalent) pour limiter l’essai</li>
      </ul>
      <h3>Données techniques &amp; analytics</h3>
      <ul>
        <li>Journaux techniques d’hébergement (Railway)</li>
        <li>Événements produit et erreurs via <strong>PostHog</strong> (UE), y compris identifiant utilisateur après connexion</li>
      </ul>
    </section>

    <section>
      <h2>3. Finalités</h2>
      <ul>
        <li>Fournir le service d’analyse et le simulateur d’entretien</li>
        <li>Authentifier les utilisateurs et conserver l’historique demandé</li>
        <li>Limiter les abus (essai gratuit, sécurité)</li>
        <li>Améliorer le produit et diagnostiquer les erreurs (PostHog)</li>
      </ul>
      <p>Base légale principale : exécution du service demandé et intérêt légitime pour la sécurité / amélioration, dans le respect du RGPD.</p>
    </section>

    <section>
      <h2>4. Transfert vers Google Gemini</h2>
      <p>
        Pour produire l’analyse, le <strong>texte du CV et de l’offre</strong> est transmis à
        <strong>Google Gemini</strong> (API Google AI) le temps du traitement. Ce contenu n’est
        pas destiné à constituer un profil public ; il est nécessaire au fonctionnement du
        service. Consultez également les conditions Google relatives à l’usage de l’API.
      </p>
      <p>
        Les documents ne sont <strong>pas conservés comme fichiers</strong> sur nos serveurs après
        la session d’analyse, hors historique explicitement enregistré pour les comptes connectés.
      </p>
    </section>

    <section>
      <h2>5. Durées de conservation</h2>
      <ul>
        <li>Compte : jusqu’à suppression par l’utilisateur ou demande</li>
        <li>Historique des comparaisons et des simulations d’entretien : jusqu’à suppression manuelle ou suppression du compte</li>
        <li>Essai gratuit (Redis) : durée courte (ordre de 24 h selon configuration)</li>
        <li>Analytics PostHog : selon la politique de rétention du projet PostHog</li>
      </ul>
    </section>

    <section>
      <h2>6. Destinataires / sous-traitants</h2>
      <ul>
        <li><strong>Railway</strong> — hébergement applicatif et bases</li>
        <li><strong>Google</strong> — Gemini (analyse) et OAuth (si connexion Google)</li>
        <li><strong>PostHog</strong> — analytics produit / erreurs (région UE)</li>
      </ul>
    </section>

    <section>
      <h2>7. Cookies et traceurs</h2>
      <p>
        Le service utilise le stockage local du navigateur pour le jeton d’authentification JWT
        (nécessaire au fonctionnement du compte). Pour la mesure d’usage, une
        <strong>bannière de consentement</strong> vous demande d’accepter ou de refuser les
        cookies / le stockage PostHog. En cas de refus, PostHog peut continuer un suivi
        anonymisé sans cookies (mode cookieless). L’essai gratuit peut s’appuyer sur un
        identifiant technique côté serveur.
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
        Mesures raisonnables : HTTPS, mots de passe hashés, accès API authentifié pour les
        routes protégées. Aucun système n’étant infaillible, nous vous invitons à ne pas
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
