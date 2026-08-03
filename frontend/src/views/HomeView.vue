<template>
  <div ref="rootEl" class="bg-paper text-ink font-sans antialiased selection:bg-ink selection:text-paper">

    <!-- ────────────────────────── NAVIGATION (fixe, centrée) ────────────────────────── -->
    <header class="pointer-events-none fixed inset-x-0 top-0 z-50 flex justify-between items-start p-5 lg:justify-center lg:p-8">
      <a
        href="/"
        @click.prevent="handleLogoClick"
        class="pointer-events-auto cursor-pointer lg:absolute lg:left-8"
        aria-label="Talento — accueil"
      >
        <BrandLogo tag="span" size="sm" />
      </a>
      <nav
        class="pointer-events-auto hidden lg:flex items-center gap-7 rounded-full border border-ink/12 bg-paper/80 px-6 py-2.5 font-mono text-caption uppercase backdrop-blur-md"
      >
        <a href="#probleme" class="text-ink-soft transition-colors hover:text-ink">Problème</a>
        <a href="#methode" class="text-ink-soft transition-colors hover:text-ink">Méthode</a>
        <a href="#apercu" class="text-ink-soft transition-colors hover:text-ink">Aperçu</a>
        <a href="#stats" class="text-ink-soft transition-colors hover:text-ink">Étapes</a>
        <a href="#acces" class="text-ink-soft transition-colors hover:text-ink">Accès</a>
        <a href="#faq" class="text-ink-soft transition-colors hover:text-ink">FAQ</a>
      </nav>

      <div
        class="pointer-events-auto flex items-center gap-1 rounded-full border border-ink/12 bg-paper/80 p-1 pl-1.5 backdrop-blur-md lg:absolute lg:right-8"
      >
        <a
          v-if="!authStore.isAuthenticated"
          @click="navigateTo('/login')"
          class="hidden cursor-pointer px-4 py-1.5 font-mono text-caption uppercase text-ink-soft transition-colors hover:text-ink sm:block"
        >
          Connexion
        </a>
        <a
          @click="primaryAction"
          class="cursor-pointer rounded-full bg-ink px-5 py-2 font-mono text-caption uppercase text-paper transition-opacity hover:opacity-85"
        >
          {{ authStore.isAuthenticated ? 'Tableau de bord' : 'Analyser mon CV' }}
        </a>
      </div>
    </header>

    <div>

      <!-- ────────────────────────── 01 · HERO ────────────────────────── -->
      <section class="grid min-h-svh grid-cols-1 lg:grid-cols-12" aria-label="Présentation Talento">
        <div class="flex flex-col justify-center px-5 pt-32 pb-16 sm:px-8 lg:col-span-6 lg:px-16 lg:py-24 xl:pl-20">
          <p data-reveal="hero" class="mb-3 font-mono text-caption uppercase tracking-[0.14em] text-ink">
            Talento
          </p>
          <p data-reveal="hero" class="mb-5 font-mono text-caption uppercase text-ink-soft">
            Conçu pour les candidatures ciblées.
          </p>

          <h1 data-reveal="hero" class="mb-8 max-w-[16ch] text-balance font-medium text-display">
            L'analyse ATS que vous ne referez plus à la main.
          </h1>

          <p data-reveal="hero" class="mb-6 max-w-[52ch] text-lead text-ink-soft">
            Chaque candidature repart de zéro : relire l'offre, deviner les mots-clés, réécrire les
            mêmes phrases. Talento fige les décisions — extraction, correspondance
            sémantique, scoring, préparation d'entretien — et les rejoue sur chaque offre en une
            seule passe.
          </p>

          <p data-reveal="hero" class="mb-10 font-mono text-caption uppercase text-ink-soft">
            Pour ceux qui visent un poste précis, pas cinquante.
          </p>

          <div data-reveal="hero" class="flex flex-col gap-3 sm:flex-row sm:items-center">
            <a
              href="/free-trial"
              @click.prevent="primaryAction"
              class="inline-flex h-12 cursor-pointer items-center justify-center rounded-lg bg-ink px-6 font-mono text-caption uppercase text-paper transition-opacity hover:opacity-85"
            >
              Lancer une analyse gratuite
            </a>
            <a
              href="#methode"
              class="inline-flex h-12 items-center justify-center rounded-lg border border-ink/20 px-6 font-mono text-caption uppercase text-ink transition-colors hover:border-ink/50"
            >
              Voir la méthode
            </a>
          </div>

          <div data-reveal="hero" class="mt-12 flex flex-wrap gap-x-6 gap-y-2 border-t border-paper-line pt-6 font-mono text-micro uppercase text-ink-soft">
            <span>Gemini · 1 appel</span>
            <span>Flux SSE · &lt; 2 s</span>
            <span>Historique compte</span>
            <span>Licence MIT</span>
          </div>
        </div>

        <!-- Panneau terminal -->
        <div data-reveal="hero-panel" class="relative min-h-[70svh] bg-ink p-5 pt-24 sm:p-8 sm:pt-28 lg:col-span-6 lg:min-h-svh lg:p-12 lg:pt-28">
          <div class="flex h-full flex-col overflow-hidden rounded-xl bg-ink-deep font-mono text-caption text-paper/90 ring-1 ring-white/10">
            <div class="flex h-9 shrink-0 items-center justify-between border-b border-white/10 px-4 text-micro uppercase text-paper/40">
              <span>analyse — session en direct</span>
              <span class="flex items-center gap-1.5">
                <span class="h-1.5 w-1.5 rounded-full bg-emerald-400"></span>
                streaming
              </span>
            </div>

            <div class="relative flex flex-1 flex-col overflow-hidden p-4 sm:p-6">
              <div class="pointer-events-none absolute inset-x-0 top-0 h-px animate-scan bg-gradient-to-r from-transparent via-emerald-400/50 to-transparent"></div>

              <div class="space-y-1.5 text-paper/50">
                <p><span class="text-paper/30">$</span> lecture offre.pdf … <span class="text-emerald-400">ok</span></p>
                <p><span class="text-paper/30">$</span> lecture cv.pdf … <span class="text-emerald-400">ok</span></p>
                <p><span class="text-paper/30">$</span> extraction des critères … <span class="text-emerald-400">18 trouvés</span></p>
              </div>

              <div class="my-5 flex items-end justify-between border-y border-white/10 py-5">
                <div>
                  <div class="mb-1 text-micro uppercase text-paper/40">Score de correspondance</div>
                  <div class="text-5xl font-medium tabular-nums text-paper">{{ animatedScore }}%</div>
                </div>
                <div class="text-right text-micro uppercase text-paper/40">
                  <div>18 critères</div>
                  <div>14 couverts</div>
                  <div>4 manquants</div>
                </div>
              </div>

              <div class="space-y-1">
                <div
                  v-for="row in streamRows.slice(0, visibleRows)"
                  :key="row.label"
                  class="flex items-baseline justify-between gap-4 border-b border-white/5 py-1.5"
                >
                  <span class="flex items-baseline gap-4">
                    <span class="tabular-nums text-paper/30">{{ row.id }}</span>
                    <span class="text-paper/80">{{ row.label }}</span>
                  </span>
                  <span :class="row.tone">{{ row.status }}</span>
                </div>
              </div>

              <div class="mt-7 space-y-2.5">
                <div class="text-micro uppercase text-paper/40">Couverture par catégorie</div>
                <div v-for="cat in categories" :key="cat.label" class="flex items-center gap-4">
                  <span class="w-28 shrink-0 text-paper/55">{{ cat.label }}</span>
                  <span class="h-px flex-1 bg-white/10">
                    <span class="block h-px bg-paper/60" :style="{ width: cat.value + '%' }"></span>
                  </span>
                  <span class="w-10 shrink-0 text-right tabular-nums text-paper/40">{{ cat.value }}%</span>
                </div>
              </div>

              <p class="mt-auto pt-6 text-paper/30">
                <span class="text-paper/20">$</span> génération des reformulations
                <span class="animate-caret">▍</span>
              </p>
            </div>
          </div>
        </div>
      </section>

      <!-- ────────────────────────── 02 · PROBLÈME ────────────────────────── -->
      <section id="probleme" data-reveal="section" class="border-t border-paper-line py-20 lg:py-40">
        <div class="mx-auto grid max-w-[100rem] grid-cols-1 gap-12 px-5 sm:px-8 lg:grid-cols-12 lg:gap-8 lg:px-16">
          <div data-reveal-item class="order-2 lg:order-1 lg:col-span-6">
            <div class="rounded-xl bg-ink-deep p-1.5 shadow-[0_24px_60px_-30px_rgba(35,35,35,0.6)]">
              <div class="overflow-hidden rounded-lg bg-ink font-mono text-caption text-paper ring-1 ring-white/10">
                <div class="flex h-9 items-center border-b border-white/10 px-4 text-micro uppercase text-paper/40">
                  temps-perdu.log
                </div>
                <div class="overflow-x-auto p-4 sm:p-6">
                  <div class="min-w-max space-y-1.5">
                    <div
                      v-for="item in timeSinks"
                      :key="item.id"
                      class="flex items-baseline justify-between gap-8"
                    >
                      <span class="flex items-baseline gap-5">
                        <span class="tabular-nums text-paper/35">{{ item.id }}</span>
                        <span class="text-paper/85">{{ item.label }}</span>
                      </span>
                      <span class="tabular-nums text-paper/45">{{ item.cost }}</span>
                    </div>
                  </div>
                </div>
                <div class="border-t border-white/10 px-4 py-3 text-micro uppercase text-paper/50 sm:px-6">
                  Temps perdu estimé : ~12 heures par candidature (1,5 jour)
                </div>
              </div>
            </div>
          </div>

          <div data-reveal-item class="order-1 lg:order-2 lg:col-span-5 lg:col-start-8 lg:pt-4">
            <p class="mb-5 font-mono text-caption uppercase text-ink-soft">Problèmes courants</p>
            <h2 class="mb-7 max-w-[18ch] text-balance font-medium text-headline">
              Adapter un CV à une offre coûte une journée. À chaque fois.
            </h2>
            <div class="space-y-4 text-lead text-ink-soft">
              <p>
                Ce n'est jamais la partie facile qui fait mal. C'est relire l'offre ligne par ligne
                pour deviner ce que le filtre attend. C'est réécrire les mêmes expériences sous un
                intitulé différent. C'est le PDF que l'ATS découpe mal, et le refus automatique
                avant qu'un humain n'ouvre le dossier.
              </p>
              <p>
                Personne ne compte ces heures, et tout le monde les repaie à la candidature
                suivante.
              </p>
            </div>
          </div>
        </div>
      </section>

      <!-- ────────────────────────── 03 · MÉTHODE (bande encre) ────────────────────────── -->
      <section id="methode" data-reveal="section" data-animate-rows class="bg-ink py-20 text-paper lg:py-40">
        <div class="mx-auto max-w-[100rem] px-5 sm:px-8 lg:px-16">
          <div class="grid grid-cols-1 gap-12 lg:grid-cols-12 lg:gap-8">
            <div data-reveal-item class="lg:col-span-5">
              <p class="mb-5 font-mono text-caption uppercase text-paper/45">Architecture</p>
              <h2 class="max-w-[16ch] text-balance font-medium text-headline">
                Chaque décision déjà prise. Pour passer directement à l'entretien.
              </h2>
            </div>
            <div data-reveal-item class="lg:col-span-6 lg:col-start-7 lg:pt-2">
              <p class="text-lead text-paper/60">
                Un générateur de CV vous donne des gabarits. Ici, ce sont des décisions : comment
                l'offre est découpée, comment une compétence est reconnue comme équivalente, quels
                écarts comptent, dans quel ordre les résultats arrivent à l'écran. Fixées une fois,
                appliquées à chaque analyse. C'est ce qui rend le modèle utile : un LLM sans
                contraintes improvise, un LLM dans une structure figée produit un résultat
                comparable d'une offre à l'autre.
              </p>
            </div>
          </div>

          <div class="mt-16 border-t border-white/10 lg:mt-24">
            <div
              v-for="decision in decisions"
              :key="decision.id"
              data-reveal-row
              class="grid grid-cols-1 gap-3 border-b border-white/10 py-7 lg:grid-cols-12 lg:gap-8"
            >
              <div class="font-mono text-caption uppercase text-paper/35 lg:col-span-2">
                {{ decision.id }}
              </div>
              <h3 class="font-medium text-title lg:col-span-4">{{ decision.title }}</h3>
              <p class="max-w-[62ch] text-lead text-paper/55 lg:col-span-6">{{ decision.body }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- ────────────────────────── 04 · APERÇU ────────────────────────── -->
      <section id="apercu" data-reveal="section" class="py-20 lg:py-40">
        <div class="mx-auto max-w-[100rem] px-5 sm:px-8 lg:px-16">
          <div class="mb-12 flex flex-col gap-6 lg:mb-16 lg:flex-row lg:items-end lg:justify-between">
            <div data-reveal-item>
              <p class="mb-5 font-mono text-caption uppercase text-ink-soft">Aperçu réel</p>
              <h2 class="max-w-[14ch] text-balance font-medium text-headline">
                Voici l'outil, pas une maquette.
              </h2>
            </div>

            <div data-reveal-item class="flex gap-1 rounded-lg border border-ink/15 p-1 font-mono text-caption uppercase">
              <button
                v-for="tab in tabs"
                :key="tab.id"
                @click="activeTab = tab.id"
                class="rounded-md px-4 py-2 transition-colors"
                :class="activeTab === tab.id ? 'bg-ink text-paper' : 'text-ink-soft hover:text-ink'"
              >
                {{ tab.label }}
              </button>
            </div>
          </div>

          <div data-reveal-item class="rounded-xl bg-ink-deep p-1.5 shadow-[0_40px_80px_-40px_rgba(35,35,35,0.55)]">
            <div class="overflow-hidden rounded-lg bg-ink font-mono text-caption text-paper ring-1 ring-white/10">
              <div class="flex h-10 items-center gap-2 border-b border-white/10 px-4 text-micro uppercase text-paper/40">
                <span class="h-2 w-2 rounded-full bg-white/15"></span>
                <span class="h-2 w-2 rounded-full bg-white/15"></span>
                <span class="h-2 w-2 rounded-full bg-white/15"></span>
                <span class="ml-3">{{ activeTab === 'analyse' ? 'comparateur — résultat' : 'simulateur — session' }}</span>
              </div>

              <!-- Onglet analyse -->
              <div v-if="activeTab === 'analyse'" class="grid grid-cols-1 lg:grid-cols-12">
                <div class="border-b border-white/10 p-6 lg:col-span-4 lg:border-b-0 lg:border-r lg:p-8">
                  <div class="mb-2 text-micro uppercase text-paper/40">Score global</div>
                  <div class="mb-6 text-6xl font-medium tabular-nums">88%</div>

                  <div class="space-y-3">
                    <div v-for="cat in categories" :key="cat.label">
                      <div class="mb-1.5 flex items-baseline justify-between text-micro uppercase">
                        <span class="text-paper/60">{{ cat.label }}</span>
                        <span class="tabular-nums text-paper/40">{{ cat.value }}%</span>
                      </div>
                      <div class="h-px w-full bg-white/10">
                        <div class="h-px bg-paper/70" :style="{ width: cat.value + '%' }"></div>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="p-6 lg:col-span-8 lg:p-8">
                  <div class="mb-3 text-micro uppercase text-paper/40">Détail des critères</div>
                  <div class="space-y-0">
                    <div
                      v-for="crit in criteria"
                      :key="crit.label"
                      class="flex items-baseline justify-between gap-6 border-b border-white/5 py-2.5"
                    >
                      <span class="text-paper/85">{{ crit.label }}</span>
                      <span class="shrink-0 text-micro uppercase" :class="crit.tone">{{ crit.status }}</span>
                    </div>
                  </div>

                  <div class="mt-6 rounded-lg border border-white/10 p-4">
                    <div class="mb-2 text-micro uppercase text-paper/40">Reformulation proposée</div>
                    <p class="font-sans text-sm leading-relaxed text-paper/80">
                      « Conteneurisation des services applicatifs avec Docker et déploiement continu
                      via GitHub Actions, réduisant le temps de mise en production de 40 %. »
                    </p>
                  </div>
                </div>
              </div>

              <!-- Onglet simulateur -->
              <div v-else class="grid grid-cols-1 lg:grid-cols-12">
                <div class="border-b border-white/10 p-6 lg:col-span-7 lg:border-b-0 lg:border-r lg:p-8">
                  <div class="mb-3 text-micro uppercase text-paper/40">Question 01 / 10 — technique</div>
                  <p class="mb-6 font-sans text-lg font-medium leading-snug text-paper">
                    Votre CV mentionne Vue 3 et TypeScript. Comment gérez-vous le rendu d'une liste
                    de plusieurs milliers d'éléments sans dégrader l'interface ?
                  </p>
                  <div class="rounded-lg border border-white/10 p-4">
                    <div class="mb-2 text-micro uppercase text-paper/40">Axes attendus</div>
                    <ul class="space-y-1.5 text-paper/70">
                      <li>— virtualisation de liste</li>
                      <li>— chargement différé des composants</li>
                      <li>— mémoïsation via <span class="text-paper">computed</span></li>
                    </ul>
                  </div>
                </div>

                <div class="p-6 lg:col-span-5 lg:p-8">
                  <div class="mb-3 text-micro uppercase text-paper/40">Origine de la question</div>
                  <p class="mb-6 text-paper/60">
                    Générée depuis l'écart réel entre votre profil et l'offre, pas depuis une banque
                    de questions générique.
                  </p>
                  <div class="space-y-2 border-t border-white/10 pt-4 text-micro uppercase text-paper/40">
                    <div class="flex justify-between"><span>Questions</span><span class="text-paper/70">10</span></div>
                    <div class="flex justify-between"><span>Retour par réponse</span><span class="text-paper/70">immédiat</span></div>
                    <div class="flex justify-between"><span>Durée moyenne</span><span class="text-paper/70">12 min</span></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ────────────────────────── 05 · CHIFFRES + ÉTAPES (bande encre) ────────────────────────── -->
      <section id="stats" data-reveal="section" class="bg-ink py-20 text-paper lg:py-40" aria-label="Indicateurs et étapes">
        <div class="mx-auto max-w-[100rem] px-5 sm:px-8 lg:px-16">
          <div class="grid grid-cols-2 gap-8 border-b border-white/10 pb-16 lg:grid-cols-4">
            <div v-for="stat in stats" :key="stat.label" data-reveal-stat>
              <div class="mb-2 text-4xl font-medium tabular-nums lg:text-5xl">{{ stat.value }}</div>
              <div class="font-mono text-micro uppercase text-paper/40">{{ stat.label }}</div>
            </div>
          </div>

          <div class="mt-16 grid grid-cols-1 gap-10 lg:grid-cols-3 lg:gap-8">
            <div v-for="step in steps" :key="step.id" data-reveal-item>
              <div class="mb-4 font-mono text-caption uppercase text-paper/35">{{ step.id }}</div>
              <h3 class="mb-3 font-medium text-title">{{ step.title }}</h3>
              <p class="max-w-[42ch] text-lead text-paper/55">{{ step.body }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- ────────────────────────── 06 · ACCÈS ────────────────────────── -->
      <section id="acces" data-reveal="section" class="py-20 lg:py-40">
        <div class="mx-auto max-w-[100rem] px-5 sm:px-8 lg:px-16">
          <div class="grid grid-cols-1 gap-12 lg:grid-cols-12 lg:gap-8">
            <div data-reveal-item class="lg:col-span-5">
              <p class="mb-5 font-mono text-caption uppercase text-ink-soft">Accès</p>
              <h2 class="mb-6 max-w-[14ch] text-balance font-medium text-headline">
                Gratuit à l'essai. Ouvert au code.
              </h2>
              <p class="max-w-[46ch] text-lead text-ink-soft">
                Le projet est publié sous licence MIT. Vous pouvez l'utiliser en ligne, lire le
                code, l'héberger vous-même ou contribuer.
              </p>
            </div>

            <div data-reveal-item class="lg:col-span-6 lg:col-start-7">
              <div class="rounded-xl border border-ink/15 p-6 sm:p-8">
                <div class="mb-6 flex items-baseline justify-between border-b border-paper-line pb-5">
                  <span class="font-mono text-caption uppercase">Compte gratuit</span>
                  <span class="text-3xl font-medium">0 €</span>
                </div>

                <ul class="mb-8 space-y-2.5 font-mono text-caption uppercase text-ink-soft">
                  <li v-for="perk in perks" :key="perk" class="flex gap-3">
                    <span class="text-ink/30">—</span>
                    <span>{{ perk }}</span>
                  </li>
                </ul>

                <div class="flex flex-col gap-3 sm:flex-row sm:items-center">
                  <a
                    @click="primaryAction"
                    class="inline-flex h-12 flex-1 cursor-pointer items-center justify-center rounded-lg bg-ink px-6 font-mono text-caption uppercase text-paper transition-opacity hover:opacity-85"
                  >
                    Créer mon compte
                  </a>
                  <a
                    href="https://github.com/mickaelrebeau/CV-Offer-Comparer"
                    target="_blank"
                    rel="noopener"
                    class="inline-flex h-12 items-center justify-center rounded-lg border border-ink/20 px-6 font-mono text-caption uppercase transition-colors hover:border-ink/50"
                  >
                    Voir le code
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ────────────────────────── 07 · FAQ (bande encre) ────────────────────────── -->
      <section
        id="faq"
        data-reveal="section"
        data-animate-rows
        class="bg-ink py-20 text-paper lg:py-40"
        itemscope
        itemtype="https://schema.org/FAQPage"
      >
        <div class="mx-auto max-w-[100rem] px-5 sm:px-8 lg:px-16">
          <div data-reveal-item class="mb-14 lg:mb-20">
            <p class="mb-5 font-mono text-caption uppercase text-paper/45">Avant de commencer</p>
            <h2 class="max-w-[16ch] text-balance font-medium text-headline">
              Les questions qu'on nous pose.
            </h2>
          </div>

          <div class="border-t border-white/10">
            <div
              v-for="item in faq"
              :key="item.id"
              data-reveal-row
              itemscope
              itemprop="mainEntity"
              itemtype="https://schema.org/Question"
              class="grid grid-cols-1 gap-3 border-b border-white/10 py-7 lg:grid-cols-12 lg:gap-8"
            >
              <div class="font-mono text-caption uppercase text-paper/40 lg:col-span-4" itemprop="name">
                {{ item.id }} / {{ item.question }}
              </div>
              <div
                itemscope
                itemprop="acceptedAnswer"
                itemtype="https://schema.org/Answer"
                class="max-w-[70ch] text-lead text-paper/60 lg:col-span-7 lg:col-start-6"
              >
                <p itemprop="text">{{ item.answer }}</p>
              </div>
            </div>
          </div>

          <div data-reveal-item class="mt-16">
            <a
              href="/free-trial"
              @click.prevent="primaryAction"
              class="inline-flex h-12 cursor-pointer items-center justify-center rounded-lg bg-paper px-6 font-mono text-caption uppercase text-ink transition-opacity hover:opacity-85"
            >
              Lancer une analyse gratuite
            </a>
          </div>
        </div>
      </section>

      <!-- ────────────────────────── FOOTER ────────────────────────── -->
      <footer class="px-5 py-16 sm:px-8 lg:px-16 lg:py-20">
        <div class="mx-auto max-w-[100rem]">
          <BrandLogo tag="p" class="mb-12" size="md" />

          <div
            class="mb-14 select-none text-balance font-medium leading-[0.92] tracking-[-0.03em]"
            style="font-size: clamp(2.5rem, 11vw, 11rem)"
          >
            Candidatez juste.
          </div>

          <div class="flex flex-col gap-4 border-t border-paper-line pt-6 font-mono text-micro uppercase text-ink-soft sm:flex-row sm:items-center sm:justify-between">
            <span>© 2026 — Licence MIT</span>
            <div class="flex flex-wrap gap-x-6 gap-y-2">
              <RouterLink to="/mentions-legales" class="transition-colors hover:text-ink">Mentions légales</RouterLink>
              <RouterLink to="/cgv" class="transition-colors hover:text-ink">CGV</RouterLink>
              <RouterLink to="/confidentialite" class="transition-colors hover:text-ink">Confidentialité</RouterLink>
              <a href="https://github.com/mickaelrebeau/CV-Offer-Comparer" target="_blank" rel="noopener" class="transition-colors hover:text-ink">GitHub</a>
              <a href="mailto:rebeau.mickael@gmail.com" class="transition-colors hover:text-ink">Contact</a>
              <a href="/login" @click.prevent="navigateTo('/login')" class="cursor-pointer transition-colors hover:text-ink">Connexion</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import BrandLogo from '@/components/BrandLogo.vue'
import { useAuthStore } from '@/stores/auth'
import { useLandingScroll } from '@/composables/useLandingScroll'
import {
  buildFaqJsonLd,
  buildSoftwareJsonLd,
  buildWebSiteJsonLd,
  usePageSeo,
} from '@/composables/usePageSeo'
import { SITE_DESCRIPTION, SITE_NAME } from '@/lib/site'

const router = useRouter()
const authStore = useAuthStore()
const rootEl = ref<HTMLElement | null>(null)
useLandingScroll({ root: rootEl })

const activeTab = ref<'analyse' | 'simulateur'>('analyse')

const tabs = [
  { id: 'analyse' as const, label: '01 · Analyse' },
  { id: 'simulateur' as const, label: '02 · Entretien' },
]

const timeSinks = [
  { id: '001', label: "Relire l'offre et isoler les vrais critères", cost: '~1 H' },
  { id: '002', label: "Réécrire le CV pour l'intitulé du poste", cost: '~3 H' },
  { id: '003', label: 'Deviner les mots-clés attendus par le filtre', cost: '~2 H' },
  { id: '004', label: 'Vérifier que le PDF passe le parsing', cost: '~1 H' },
  { id: '005', label: 'Repérer honnêtement les compétences manquantes', cost: '~1 H' },
  { id: '006', label: 'Reformuler les expériences en résultats mesurables', cost: '~2 H' },
  { id: '007', label: 'Préparer les questions techniques probables', cost: '~2 H' },
  { id: '008', label: 'Tout recommencer à la candidature suivante', cost: '∞ H' },
]

const decisions = [
  {
    id: '001',
    title: 'Une seule passe',
    body: "L'offre et le CV partent ensemble dans un appel structuré unique. Pas de chaîne de prompts, pas de latence cumulée : la première réponse arrive en moins de deux secondes.",
  },
  {
    id: '002',
    title: 'Correspondance sémantique',
    body: "« Vue 3 » et « Vue.js », « Postgres » et « PostgreSQL », « anglais courant » et « bilingue » sont reconnus comme équivalents. L'intention compte, pas la chaîne de caractères.",
  },
  {
    id: '003',
    title: "Cinq catégories d'écart",
    body: "Compétences techniques, compétences transverses, langues, niveau d'expérience, diplômes et certifications. Les mêmes cases à chaque analyse, avec le même seuil de correspondance.",
  },
  {
    id: '004',
    title: 'Reformulations prêtes à coller',
    body: "Chaque critère faible ou manquant reçoit une formulation orientée résultat, lisible par un ATS comme par un recruteur, que vous copiez directement dans votre document.",
  },
  {
    id: '005',
    title: "Entretien dérivé de l'écart",
    body: "Les questions ne sortent pas d'une banque générique : elles sont générées depuis la différence exacte entre votre profil et l'offre, avec un retour sur chaque réponse.",
  },
  {
    id: '006',
    title: 'Résultats au fil du flux',
    body: "Les critères s'affichent au fur et à mesure via un flux SSE. Vous lisez les premiers résultats pendant que les suivants arrivent, sans écran d'attente.",
  },
  {
    id: '007',
    title: 'Contrôle des données',
    body: "Les fichiers ne sont pas archivés hors session. Gemini reçoit le texte pour l'analyse ; les comptes connectés peuvent conserver un historique. Aucun CV revendu, suppression possible depuis le profil.",
  },
]

const stats = [
  { value: '< 2 s', label: 'Première réponse' },
  { value: '1', label: 'Appel modèle par analyse' },
  { value: '5', label: "Catégories d'écart" },
  { value: '0', label: 'Document conservé' },
]

const steps = [
  {
    id: '001',
    title: 'Déposez',
    body: "Votre CV en PDF et le texte de l'offre. Le texte est extrait et nettoyé automatiquement.",
  },
  {
    id: '002',
    title: 'Lisez',
    body: 'Score global, détail par critère, écarts classés et reformulations, affichés au fil du flux.',
  },
  {
    id: '003',
    title: 'Préparez',
    body: "Dix questions d'entretien construites sur vos points faibles réels, avec un retour immédiat.",
  },
]

const perks = [
  'Essai sans carte bancaire',
  'Analyse complète en flux continu',
  'Écarts classés et reformulations',
  "Simulateur d'entretien et retours",
  'Import PDF et extraction automatique',
  'Code source ouvert, auto-hébergeable',
]

const faq = [
  {
    id: 'Q.001',
    question: 'Sur quelle stack est-ce construit ?',
    answer: "Vue 3, TypeScript, Pinia et Tailwind côté interface. FastAPI, PostgreSQL et le modèle Gemini via google-genai côté serveur. Déploiement Docker sur Railway.",
  },
  {
    id: 'Q.002',
    question: 'En quoi est-ce différent des générateurs de CV ?',
    answer: "Un générateur vous donne une mise en page. Ici, vous obtenez un diagnostic : ce que l'offre demande, ce que votre CV couvre réellement, ce qui manque, et quoi écrire à la place.",
  },
  {
    id: 'Q.003',
    question: 'Mes documents sont-ils conservés ?',
    answer: "Le CV et l'offre sont envoyés à Google Gemini pour l'analyse, puis traités en mémoire côté serveur. Pour les comptes connectés, l'historique des analyses peut être enregistré. Seul votre compte (et cet historique) est stocké durablement ; vous pouvez tout supprimer depuis votre profil. Détails : page Confidentialité.",
  },
  {
    id: 'Q.007',
    question: 'Utilisez-vous des outils d’analytics ?',
    answer: "Oui. PostHog (région UE) mesure l'usage produit et les erreurs. Après connexion, votre compte peut être associé aux événements. Voir la politique de confidentialité.",
  },
  {
    id: 'Q.004',
    question: 'Le score est-il fiable ?',
    answer: "C'est une estimation calibrée sur les critères extraits de l'offre, pas le score exact d'un ATS propriétaire. Il sert à hiérarchiser vos corrections, pas à prédire une embauche.",
  },
  {
    id: 'Q.005',
    question: 'Puis-je héberger le projet moi-même ?',
    answer: "Oui. Le dépôt est public sous licence MIT et contient les Dockerfile, le guide de démarrage et les variables d'environnement nécessaires.",
  },
  {
    id: 'Q.006',
    question: 'Comment contribuer ?',
    answer: "Les issues et pull requests sont ouvertes. Le guide de contribution décrit la mise en place locale, les conventions de commit et le processus de revue.",
  },
]

const categories = [
  { label: 'Techniques', value: 92 },
  { label: 'Transverses', value: 85 },
  { label: 'Langues', value: 100 },
  { label: 'Expérience', value: 78 },
  { label: 'Diplômes', value: 90 },
]

const criteria = [
  { label: 'TypeScript — 3 ans minimum', status: 'couvert', tone: 'text-emerald-400' },
  { label: 'Vue 3 / Composition API', status: 'couvert', tone: 'text-emerald-400' },
  { label: 'Tests unitaires (Vitest)', status: 'partiel', tone: 'text-amber-400' },
  { label: 'Docker / conteneurisation', status: 'manquant', tone: 'text-rose-400' },
  { label: 'Anglais professionnel', status: 'couvert', tone: 'text-emerald-400' },
]

const streamRows = [
  { id: '001', label: 'TypeScript', status: 'couvert', tone: 'text-emerald-400' },
  { id: '002', label: 'Vue 3', status: 'couvert', tone: 'text-emerald-400' },
  { id: '003', label: 'Tests unitaires', status: 'partiel', tone: 'text-amber-400' },
  { id: '004', label: 'Docker', status: 'manquant', tone: 'text-rose-400' },
]

const animatedScore = ref(0)
const visibleRows = ref(0)

usePageSeo({
  title: undefined,
  description: SITE_DESCRIPTION,
  path: '/',
  jsonLd: [
    buildWebSiteJsonLd(),
    buildSoftwareJsonLd(),
    buildFaqJsonLd(faq.map(({ question, answer }) => ({ question, answer }))),
    {
      '@context': 'https://schema.org',
      '@type': 'Organization',
      name: SITE_NAME,
      url: 'https://cv-compare.up.railway.app',
      logo: 'https://cv-compare.up.railway.app/logo.png',
      email: 'rebeau.mickael@gmail.com',
      sameAs: ['https://github.com/mickaelrebeau/CV-Offer-Comparer'],
    },
  ],
})

let scoreTimer: number | undefined
let rowTimer: number | undefined

onMounted(() => {
  scoreTimer = window.setInterval(() => {
    if (animatedScore.value >= 88) {
      window.clearInterval(scoreTimer)
      return
    }
    animatedScore.value += 2
  }, 24)

  rowTimer = window.setInterval(() => {
    if (visibleRows.value >= streamRows.length) {
      window.clearInterval(rowTimer)
      return
    }
    visibleRows.value += 1
  }, 420)
})

onUnmounted(() => {
  window.clearInterval(scoreTimer)
  window.clearInterval(rowTimer)
})

const navigateTo = (path: string) => router.push(path)

const primaryAction = () => {
  router.push(authStore.isAuthenticated ? '/dashboard' : '/free-trial')
}

const handleLogoClick = () => {
  router.push(authStore.isAuthenticated ? '/dashboard' : '/')
}
</script>
