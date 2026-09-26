<template>
  <LegalPageShell
    v-if="locale === 'en'"
    label="Legal information"
    title="Legal notice"
    description="Publisher, hosting and access conditions of the Talento service."
    updated-at="2026-08-03"
  >
    <section>
      <h2>1. Website publisher</h2>
      <p>
        The <strong>Talento</strong> website (GitHub repository “CV-Offer-Comparer”) is published by
        <strong>{{ LEGAL_PUBLISHER.name }}</strong>, a private individual.
      </p>
      <ul>
        <li>Contact: <a :href="`mailto:${LEGAL_PUBLISHER.email}`">{{ LEGAL_PUBLISHER.email }}</a></li>
        <li>Profile: <a :href="LEGAL_PUBLISHER.github" target="_blank" rel="noopener">GitHub</a></li>
        <li>Website: <a :href="SITE_URL">{{ SITE_URL }}</a></li>
      </ul>
      <p>
        As there is no dedicated company, the publisher acts in their own name to provide this
        open source service.
      </p>
    </section>

    <section>
      <h2>2. Publication director</h2>
      <p>{{ LEGAL_PUBLISHER.name }}.</p>
    </section>

    <section>
      <h2>3. Hosting</h2>
      <p>
        The application is deployed on the <strong>Railway</strong> infrastructure
        (Railway Corp / railway.app). Application data (user accounts, comparison history) is
        stored in PostgreSQL and Redis provided by this host.
      </p>
    </section>

    <section>
      <h2>4. Nature of the service</h2>
      <p>
        Talento is open source software released under the <strong>MIT</strong> License. It
        provides an analysis assisted by artificial intelligence (Google Gemini) between a resume
        and a job offer, as well as an interview simulator. The online service is offered as a
        free tool, with no guarantee of being hired.
      </p>
    </section>

    <section>
      <h2>5. Intellectual property</h2>
      <p>
        The source code is available on
        <a :href="GITHUB_URL" target="_blank" rel="noopener">GitHub</a>
        under the MIT License. The trademarks, logos and editorial content of the landing page
        remain the property of the publisher, unless stated otherwise.
      </p>
    </section>

    <section>
      <h2>6. Liability</h2>
      <p>
        The publisher strives to keep the service available, without any obligation of result.
        The scores and suggestions generated are indicative. Users remain solely responsible for
        how they use the rewrites and for the content of their applications.
      </p>
    </section>

    <section>
      <h2>7. Contact</h2>
      <p>
        For any question about this legal notice:
        <a :href="`mailto:${LEGAL_PUBLISHER.email}`">{{ LEGAL_PUBLISHER.email }}</a>.
      </p>
    </section>
  </LegalPageShell>

  <LegalPageShell
    v-else
    label="Informations légales"
    title="Mentions légales"
    description="Éditeur, hébergement et conditions d’accès au service Talento."
    updated-at="2026-08-03"
  >
    <section>
      <h2>1. Éditeur du site</h2>
      <p>
        Le site <strong>Talento</strong> (dépôt GitHub « CV-Offer-Comparer ») est édité par
        <strong>{{ LEGAL_PUBLISHER.name }}</strong>, personne physique.
      </p>
      <ul>
        <li>Contact : <a :href="`mailto:${LEGAL_PUBLISHER.email}`">{{ LEGAL_PUBLISHER.email }}</a></li>
        <li>Profil : <a :href="LEGAL_PUBLISHER.github" target="_blank" rel="noopener">GitHub</a></li>
        <li>Site : <a :href="SITE_URL">{{ SITE_URL }}</a></li>
      </ul>
      <p>
        En l’absence de société commerciale dédiée, l’éditeur agit en son nom propre pour la
        mise à disposition du service open source.
      </p>
    </section>

    <section>
      <h2>2. Directeur de la publication</h2>
      <p>{{ LEGAL_PUBLISHER.name }}.</p>
    </section>

    <section>
      <h2>3. Hébergement</h2>
      <p>
        L’application est déployée sur l’infrastructure <strong>Railway</strong>
        (Railway Corp / railway.app). Les données applicatives (comptes utilisateurs,
        historique des comparaisons) sont stockées sur PostgreSQL et Redis fournis par
        cet hébergeur.
      </p>
    </section>

    <section>
      <h2>4. Nature du service</h2>
      <p>
        Talento est un outil logiciel open source sous licence <strong>MIT</strong>. Il propose
        une analyse assistée par intelligence artificielle (Google Gemini) entre un CV et une
        offre d’emploi, ainsi qu’un simulateur d’entretien. Le service en ligne est proposé
        à titre d’essai / outil gratuit, sans garantie de résultat d’embauche.
      </p>
    </section>

    <section>
      <h2>5. Propriété intellectuelle</h2>
      <p>
        Le code source est disponible sur
        <a :href="GITHUB_URL" target="_blank" rel="noopener">GitHub</a>
        sous licence MIT. Les marques, logos et contenus rédactionnels de la landing restent
        la propriété de l’éditeur, sauf mention contraire.
      </p>
    </section>

    <section>
      <h2>6. Responsabilité</h2>
      <p>
        L’éditeur s’efforce d’assurer la disponibilité du service, sans obligation de résultat.
        Les scores et suggestions générés sont indicatifs. L’utilisateur reste seul responsable
        de l’usage qu’il fait des reformulations et du contenu de ses candidatures.
      </p>
    </section>

    <section>
      <h2>7. Contact</h2>
      <p>
        Pour toute question relative aux présentes mentions :
        <a :href="`mailto:${LEGAL_PUBLISHER.email}`">{{ LEGAL_PUBLISHER.email }}</a>.
      </p>
    </section>
  </LegalPageShell>
</template>

<script setup lang="ts">
import LegalPageShell from '@/components/LegalPageShell.vue'
import { useLocale } from '@/i18n/useLocale'
import { GITHUB_URL, LEGAL_PUBLISHER, SITE_URL } from '@/lib/site'

// Titre, description et canonical : App.vue (meta.seo = 'legalNotice')
const { locale } = useLocale()
</script>
