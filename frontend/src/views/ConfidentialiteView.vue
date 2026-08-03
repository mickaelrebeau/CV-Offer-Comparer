<template>
  <LegalPageShell
    label="Vie privée"
    title="Politique de confidentialité"
    description="Données collectées, finalités, sous-traitants et vos droits."
    updated-at="3 août 2026"
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
        <li>Historique des comparaisons : jusqu’à suppression manuelle ou suppression du compte</li>
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
        et peut déposer des cookies / stockage liés à PostHog pour la mesure d’usage. L’essai
        gratuit peut s’appuyer sur un identifiant technique côté serveur.
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
import { usePageSeo } from '@/composables/usePageSeo'
import { LEGAL_PUBLISHER } from '@/lib/site'

usePageSeo({
  title: 'Politique de confidentialité',
  description:
    'Politique de confidentialité Talento : compte, historique, Google Gemini, PostHog, conservation et droits RGPD.',
  path: '/confidentialite',
})
</script>
