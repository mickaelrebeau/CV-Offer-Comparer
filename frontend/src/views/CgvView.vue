<template>
  <LegalPageShell
    label="Conditions"
    title="Conditions générales (CGV / CGU)"
    description="Conditions d’accès et d’utilisation du service Talento en ligne."
    updated-at="3 août 2026"
  >
    <section>
      <h2>1. Objet</h2>
      <p>
        Les présentes conditions régissent l’accès et l’utilisation du service en ligne
        <strong>Talento</strong> (analyse CV ↔ offre, historique, simulateur d’entretien).
        En créant un compte ou en utilisant l’essai gratuit, vous acceptez ces conditions.
      </p>
    </section>

    <section>
      <h2>2. Description du service</h2>
      <ul>
        <li>Comparaison assistée par IA (Google Gemini) entre un CV et une offre d’emploi</li>
        <li>Suggestions de reformulation orientées ATS</li>
        <li>Simulateur d’entretien personnalisé</li>
        <li>Historique des analyses pour les comptes authentifiés</li>
        <li>Essai limité pour les visiteurs non connectés</li>
      </ul>
      <p>
        Le code source est ouvert (licence MIT). Vous pouvez également auto-héberger le projet
        ; les présentes conditions concernent principalement l’instance publique hébergée par
        l’éditeur.
      </p>
    </section>

    <section>
      <h2>3. Accès et compte</h2>
      <p>
        L’accès aux fonctions avancées nécessite un compte (e-mail / mot de passe ou Google OAuth).
        Vous êtes responsable de la confidentialité de vos identifiants et de l’exactitude des
        informations fournies.
      </p>
    </section>

    <section>
      <h2>4. Gratuité et absence de vente</h2>
      <p>
        L’instance publique est proposée <strong>sans contrepartie financière</strong> au moment
        de la rédaction des présentes. Il n’y a pas de panier, de facturation ni d’abonnement
        payant. Si une offre payante est introduite ultérieurement, elle fera l’objet de
        conditions spécifiques clairement présentées avant tout engagement.
      </p>
    </section>

    <section>
      <h2>5. Usage acceptable</h2>
      <p>Vous vous engagez à :</p>
      <ul>
        <li>utiliser le service à des fins légitimes de candidature ou d’évaluation personnelle</li>
        <li>ne pas tenter de contourner les limites d’essai, quotas ou mesures de sécurité</li>
        <li>ne pas surcharger volontairement l’API ou les appels au modèle d’IA</li>
        <li>ne pas téléverser de contenus illicites</li>
      </ul>
    </section>

    <section>
      <h2>6. Intelligence artificielle et résultats</h2>
      <p>
        Les analyses sont générées par un modèle d’IA tiers. Les scores, écarts et reformulations
        sont <strong>indicatifs</strong> et ne constituent ni un conseil RH, ni une garantie
        d’embauche, ni le score d’un ATS propriétaire. Vous restez seul responsable du contenu
        final de vos documents de candidature.
      </p>
    </section>

    <section>
      <h2>7. Disponibilité</h2>
      <p>
        Le service est fourni « en l’état ». Des interruptions (maintenance, incidents
        hébergeur, quotas IA) peuvent survenir sans que cela ouvre droit à indemnité.
      </p>
    </section>

    <section>
      <h2>8. Résiliation</h2>
      <p>
        Vous pouvez supprimer votre compte depuis la page Profil. L’éditeur peut suspendre
        l’accès en cas d’usage abusif ou de non-respect des présentes conditions.
      </p>
    </section>

    <section>
      <h2>9. Droit applicable</h2>
      <p>
        Les présentes sont régies par le droit français. En cas de litige, et à défaut
        d’accord amiable, les tribunaux compétents seront ceux du ressort du domicile de
        l’éditeur, sous réserve des règles impératives de protection du consommateur.
      </p>
    </section>

    <section>
      <h2>10. Contact</h2>
      <p>
        <a :href="`mailto:${CONTACT_EMAIL}`">{{ CONTACT_EMAIL }}</a>
      </p>
    </section>
  </LegalPageShell>
</template>

<script setup lang="ts">
import LegalPageShell from '@/components/LegalPageShell.vue'
import { usePageSeo } from '@/composables/usePageSeo'
import { CONTACT_EMAIL } from '@/lib/site'

usePageSeo({
  title: 'CGV / CGU',
  description: 'Conditions générales d’utilisation du service Talento (analyse ATS, essai gratuit, responsabilités).',
  path: '/cgv',
})
</script>
