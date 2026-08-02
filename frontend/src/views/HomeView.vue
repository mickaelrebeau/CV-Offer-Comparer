<template>
  <div class="overflow-x-hidden relative bg-background text-foreground font-sans antialiased">
    <!-- HERO SECTION -->
    <section class="relative pt-24 pb-16 lg:pt-36 lg:pb-28 overflow-hidden">
      <!-- Background Ambient Grid & Subtle Glow -->
      <div class="absolute inset-0 bg-grid-pattern opacity-30 pointer-events-none"></div>
      <div class="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[500px] bg-radial-gradient opacity-70 pointer-events-none"></div>

      <div class="max-w-6xl mx-auto px-6 lg:px-8 relative z-10">
        <div class="flex flex-col items-center text-center max-w-4xl mx-auto">
          
          <!-- ContentArchitecture Style Tagline Subhead -->
          <div class="hero-anim opacity-0 translate-y-6 text-xs font-mono italic text-muted-foreground mb-4">
            _Built for high-stakes candidacies & ATS precision._
          </div>

          <!-- Minimalist Status Pill -->
          <div class="hero-anim opacity-0 translate-y-6 inline-flex items-center gap-2 px-3 py-1 rounded-full bg-zinc-100 dark:bg-zinc-800/80 border border-zinc-200 dark:border-zinc-700/80 text-[11px] font-mono tracking-tight text-foreground mb-8 shadow-sm">
            <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span class="font-semibold">CV OFFER COMPARER</span>
            <span class="text-zinc-400">/</span>
            <span class="text-muted-foreground">ENGINEERED FOR JOB SEARCH</span>
          </div>

          <!-- Main Impact Headline -->
          <h1 class="hero-anim opacity-0 translate-y-6 text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-black tracking-tight mb-8 leading-[1.02] text-foreground">
            Passez le filtre ATS.<br />
            <span class="text-gradient-indigo">Décrochez l'entretien.</span>
          </h1>

          <!-- Crisp Subhead -->
          <p class="hero-anim opacity-0 translate-y-6 text-base sm:text-lg md:text-xl text-muted-foreground mb-10 max-w-2xl leading-relaxed font-normal">
            L'architecture d'analyse sémantique qui aligne votre CV avec l'offre d'emploi.
            Détectez les mots-clés manquants, éliminez les angles morts et entraînez-vous aux entretiens.
          </p>

          <!-- Primary CTA Buttons -->
          <div class="hero-anim opacity-0 translate-y-6 flex flex-col sm:flex-row items-center gap-4 w-full sm:w-auto">
            <a @click="startAnalysis" class="cursor-pointer w-full sm:w-auto px-8 py-4 rounded-full bg-foreground text-background font-semibold text-sm hover:opacity-90 transition-all shadow-glow hover:shadow-glow-lg flex items-center justify-center gap-2 group">
              <span>Lancer une analyse gratuite</span>
              <svg class="w-4 h-4 group-hover:translate-x-1 transition-transform" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M5 12h14M12 5l7 7-7 7"/>
              </svg>
            </a>
            <a href="#architecture" class="cursor-pointer w-full sm:w-auto px-8 py-4 rounded-full bg-zinc-100 dark:bg-zinc-900 hover:bg-zinc-200 dark:hover:bg-zinc-800 text-foreground font-medium text-sm transition-all border border-zinc-200 dark:border-zinc-800 flex items-center justify-center">
              Explorer l'architecture
            </a>
          </div>

          <p class="hero-anim opacity-0 translate-y-6 text-xs text-muted-foreground italic mt-4">
            _Pour ingénieurs, managers et spécialistes exigeants._
          </p>
        </div>

        <!-- Interactive Architecture Workbench Showcase -->
        <div id="architecture" class="hero-ui opacity-0 mt-16 sm:mt-24 relative max-w-5xl mx-auto scroll-mt-24">
          <div class="glass-panel rounded-2xl shadow-2xl overflow-hidden border border-zinc-200 dark:border-zinc-800">
            <!-- Window Control Header -->
            <div class="h-11 px-5 flex items-center justify-between bg-zinc-100/90 dark:bg-zinc-900/90 border-b border-zinc-200 dark:border-zinc-800">
              <div class="flex items-center gap-2">
                <div class="w-3 h-3 rounded-full bg-zinc-300 dark:bg-zinc-700"></div>
                <div class="w-3 h-3 rounded-full bg-zinc-300 dark:bg-zinc-700"></div>
                <div class="w-3 h-3 rounded-full bg-zinc-300 dark:bg-zinc-700"></div>
                <span class="ml-2 text-xs font-mono text-muted-foreground">cv-offer-comparer.app — workbench v2.0</span>
              </div>
              <div class="flex items-center gap-1.5 p-1 rounded-lg bg-zinc-200/60 dark:bg-zinc-800/60">
                <button @click="activeDemoTab = 'analysis'" class="px-3 py-1 text-xs font-mono rounded-md transition-all" :class="activeDemoTab === 'analysis' ? 'bg-background text-foreground shadow-sm font-semibold' : 'text-muted-foreground hover:text-foreground'">
                  01 / ATS Gap Analysis
                </button>
                <button @click="activeDemoTab = 'interview'" class="px-3 py-1 text-xs font-mono rounded-md transition-all" :class="activeDemoTab === 'interview' ? 'bg-background text-foreground shadow-sm font-semibold' : 'text-muted-foreground hover:text-foreground'">
                  02 / Interview Studio
                </button>
              </div>
            </div>

            <!-- Tab Content: ATS Analysis -->
            <div v-if="activeDemoTab === 'analysis'" class="p-6 sm:p-8 bg-background/60 space-y-6">
              <div class="grid md:grid-cols-3 gap-6 items-stretch">
                <!-- Score Gauge Card -->
                <div class="p-6 rounded-xl bg-card border border-border flex flex-col items-center justify-center text-center">
                  <div class="text-[11px] font-mono uppercase tracking-widest text-muted-foreground mb-3">Matching Score</div>
                  <div class="relative w-28 h-28 flex items-center justify-center">
                    <svg class="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                      <path class="text-zinc-200 dark:text-zinc-800" stroke-width="3" stroke="currentColor" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                      <path class="text-emerald-500" stroke-linecap="round" stroke-dasharray="88, 100" stroke-width="3.2" stroke="currentColor" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                    </svg>
                    <span class="absolute text-3xl font-black tracking-tight">88%</span>
                  </div>
                  <span class="mt-3 text-xs font-mono font-semibold px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                    MATCH ATS VALIDE
                  </span>
                </div>

                <!-- Matched & Missing Keywords Breakdown -->
                <div class="md:col-span-2 space-y-4 flex flex-col justify-between">
                  <div class="p-4 rounded-xl bg-card border border-border space-y-2">
                    <div class="flex items-center justify-between text-xs">
                      <span class="font-mono font-semibold text-emerald-600 dark:text-emerald-400 flex items-center gap-1.5">
                        <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
                        Compétences Détectées (12)
                      </span>
                      <span class="text-muted-foreground font-mono text-[11px]">Match Sémantique</span>
                    </div>
                    <div class="flex flex-wrap gap-1.5 pt-1">
                      <span v-for="skill in ['TypeScript', 'Vue 3 / React', 'Tailwind CSS', 'FastAPI / Node', 'Git CI/CD', 'PostgreSQL']" :key="skill" class="text-xs px-2.5 py-1 rounded-md bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 font-medium">
                        ✓ {{ skill }}
                      </span>
                    </div>
                  </div>

                  <div class="p-4 rounded-xl bg-card border border-border space-y-2">
                    <div class="flex items-center justify-between text-xs">
                      <span class="font-mono font-semibold text-rose-500 flex items-center gap-1.5">
                        <span class="w-2 h-2 rounded-full bg-rose-500"></span>
                        Angles Morts / Exigences Manquantes (2)
                      </span>
                      <span class="text-muted-foreground font-mono text-[11px]">Action Recommandée</span>
                    </div>
                    <div class="flex flex-wrap gap-1.5 pt-1">
                      <span v-for="missing in ['Docker / Containerization', 'Tests Unitaires (Vitest / Pytest)']" :key="missing" class="text-xs px-2.5 py-1 rounded-md bg-rose-500/10 text-rose-600 dark:text-rose-400 font-medium">
                        + {{ missing }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Tab Content: Interview Simulator -->
            <div v-else class="p-6 sm:p-8 bg-background/60 space-y-4">
              <div class="p-5 rounded-xl bg-card border border-border space-y-3">
                <div class="flex items-center justify-between">
                  <span class="text-xs font-mono font-bold uppercase tracking-wider text-indigo-500">Question 1 / 5 • Technique & Performance</span>
                  <span class="text-xs text-muted-foreground font-mono">02:15</span>
                </div>
                <p class="text-sm font-semibold text-foreground leading-relaxed">
                  "Vous mentionnez l'utilisation de Vue 3 et TypeScript. Comment optimisez-vous les performances de rendu lors du chargement de listes volumineuses ?"
                </p>
              </div>

              <div class="p-5 rounded-xl bg-indigo-50/50 dark:bg-indigo-950/20 border border-indigo-200/50 dark:border-indigo-800/40 space-y-2">
                <div class="text-xs font-mono font-bold text-indigo-600 dark:text-indigo-400 flex items-center gap-1.5">
                  <span>💡 RECOMMANDATION DE RÉPONSE & MOTS-CLÉS</span>
                </div>
                <p class="text-xs text-muted-foreground leading-relaxed font-normal">
                  Axez votre réponse sur la virtualisation de liste (Virtual Scrolling), le lazy loading des composants, et la mémoïsation avec <code class="px-1.5 py-0.5 rounded bg-zinc-200 dark:bg-zinc-800 font-mono text-[11px]">computed</code>.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- SECTION: THE COMMON PROBLEMS (ContentArchitecture Style) -->
    <section class="py-20 lg:py-28 border-t border-zinc-200 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-950/40">
      <div class="max-w-5xl mx-auto px-6 lg:px-8">
        <div class="mb-12">
          <div class="text-xs font-mono italic text-muted-foreground mb-3">_Problème récurrent_</div>
          <h2 class="text-3xl sm:text-4xl md:text-5xl font-black tracking-tight text-foreground leading-tight">
            Le trou noir des filtres ATS vous coûte des entretiens. À chaque candidature.
          </h2>
        </div>

        <p class="text-base sm:text-lg text-muted-foreground leading-relaxed mb-12 max-w-3xl">
          Ce n'est presque jamais un manque de compétences qui bloque votre dossier. C'est l'algorithme ATS qui ne détecte pas vos synonymes. Ce sont les mots-clés absents de vos puces d'expérience. Et l'anxiété avant le premier tour où vous devinez à l'aveugle les questions du recruteur.
        </p>

        <!-- Matrix of Lost Time per Application -->
        <div class="space-y-3 font-mono text-xs sm:text-sm">
          <div class="p-4 rounded-xl bg-background border border-border flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <span class="text-foreground font-medium">• Relecture et adaptation manuelle du CV ligne par ligne</span>
            <span class="text-rose-500 font-semibold sm:text-right">~2.5 HRS</span>
          </div>

          <div class="p-4 rounded-xl bg-background border border-border flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <span class="text-foreground font-medium">• Recherche des synonymes et densité de mots-clés imposée par la fiche</span>
            <span class="text-rose-500 font-semibold sm:text-right">~1.5 HRS</span>
          </div>

          <div class="p-4 rounded-xl bg-background border border-border flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <span class="text-foreground font-medium">• Improvisation et manque de préparation aux questions pièges</span>
            <span class="text-rose-500 font-semibold sm:text-right">~2.0 HRS</span>
          </div>

          <div class="p-4 rounded-xl bg-background border border-border flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <span class="text-foreground font-medium">• Erreurs de parsing PDF et rejets automatiques inexpliqués</span>
            <span class="text-rose-500 font-semibold sm:text-right">~1.0 HR</span>
          </div>
        </div>

        <div class="mt-8 text-xs font-mono text-rose-600 dark:text-rose-400 font-bold uppercase tracking-wider">
          _TEMPS PERDU ESTIMÉ : ~7 HEURES PAR DOSSIER DE CANDIDATURE_
        </div>
      </div>
    </section>

    <!-- SECTION: THE DECISIONS MADE (ContentArchitecture Style) -->
    <section id="features" class="py-24 sm:py-32 border-t border-zinc-200 dark:border-zinc-800">
      <div class="max-w-5xl mx-auto px-6 lg:px-8">
        <div class="mb-16">
          <div class="text-xs font-mono italic text-muted-foreground mb-3">_L'architecture solution_</div>
          <h2 class="text-3xl sm:text-4xl md:text-5xl font-black tracking-tight text-foreground leading-tight mb-6">
            Chaque décision d'analyse déjà validée.
          </h2>
          <p class="text-base sm:text-lg text-muted-foreground leading-relaxed max-w-3xl">
            CV Offer Comparer est le socle structuré d'ingénierie de candidature. Des règles de matching sémantique, d'extraction de compétences et de simulation d'entretien éprouvées, prêtes à l'emploi.
          </p>
        </div>

        <!-- Bento Decision Grid -->
        <div class="grid md:grid-cols-2 gap-6">
          <!-- Item 1 -->
          <div class="glass-card p-8 rounded-2xl space-y-4 border border-border flex flex-col justify-between">
            <div class="space-y-3">
              <span class="text-[11px] font-mono px-2.5 py-1 rounded bg-zinc-100 dark:bg-zinc-800 text-muted-foreground">01 / GEMINI LLM DIRECT</span>
              <h3 class="text-xl font-bold tracking-tight text-foreground">
                Analyse Structurée Monopasse
              </h3>
              <p class="text-sm text-muted-foreground leading-relaxed">
                Aucun enchaînement lent de prompts. Un seul appel structuré Gemini extrait les exigences, évalue la correspondance sémantique et génère les suggestions en streaming SSE instantané.
              </p>
            </div>
            <div class="pt-4 border-t border-border/60 text-xs font-mono text-muted-foreground">
              Stream SSE • Latence &lt; 2s
            </div>
          </div>

          <!-- Item 2 -->
          <div class="glass-card p-8 rounded-2xl space-y-4 border border-border flex flex-col justify-between">
            <div class="space-y-3">
              <span class="text-[11px] font-mono px-2.5 py-1 rounded bg-zinc-100 dark:bg-zinc-800 text-muted-foreground">02 / DIAGNOSTIC SÉMANTIQUE</span>
              <h3 class="text-xl font-bold tracking-tight text-foreground">
                Gap Analysis Multi-Catégories
              </h3>
              <p class="text-sm text-muted-foreground leading-relaxed">
                Catégorisation automatique des compétences techniques, soft skills, langues, formations et niveau d'expérience. Les variations de synonymes sont automatiquement neutralisées.
              </p>
            </div>
            <div class="pt-4 border-t border-border/60 text-xs font-mono text-muted-foreground">
              Hard & Soft Skills • Synonym Matching
            </div>
          </div>

          <!-- Item 3 -->
          <div class="glass-card p-8 rounded-2xl space-y-4 border border-border flex flex-col justify-between">
            <div class="space-y-3">
              <span class="text-[11px] font-mono px-2.5 py-1 rounded bg-zinc-100 dark:bg-zinc-800 text-muted-foreground">03 / SIMULATEUR D'ENTRETIEN</span>
              <h3 class="text-xl font-bold tracking-tight text-foreground">
                Entraînement Ciblé sur les Angles Morts
              </h3>
              <p class="text-sm text-muted-foreground leading-relaxed">
                Le simulateur construit 10 questions sur-mesure d'après les faiblesses identifiées entre votre CV et l'offre, puis évalue la qualité de vos réponses.
              </p>
            </div>
            <div class="pt-4 border-t border-border/60 text-xs font-mono text-muted-foreground">
              Q&A Sur-mesure • Feedback Pratique
            </div>
          </div>

          <!-- Item 4 -->
          <div class="glass-card p-8 rounded-2xl space-y-4 border border-border flex flex-col justify-between">
            <div class="space-y-3">
              <span class="text-[11px] font-mono px-2.5 py-1 rounded bg-zinc-100 dark:bg-zinc-800 text-muted-foreground">04 / SÉCURITÉ & SOBRIÉTÉ</span>
              <h3 class="text-xl font-bold tracking-tight text-foreground">
                PostgreSQL + Redis & Zero Slop
              </h3>
              <p class="text-sm text-muted-foreground leading-relaxed">
                Gestion de session JWT robuste, stockage Postgres sécurisé et contrôle des limites d'essai via Redis. Aucune phrase creuse ou verbiage généré.
              </p>
            </div>
            <div class="pt-4 border-t border-border/60 text-xs font-mono text-muted-foreground">
              PostgreSQL • Redis • Privacy First
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- METRICS TICKER STRIP -->
    <section class="py-12 border-y border-zinc-200 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-950/30">
      <div class="max-w-6xl mx-auto px-6 lg:px-8">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-8 text-center font-mono">
          <div class="space-y-1">
            <div class="text-3xl sm:text-4xl font-black text-foreground">94%</div>
            <div class="text-[11px] text-muted-foreground uppercase tracking-wider">Taux de passage ATS</div>
          </div>
          <div class="space-y-1">
            <div class="text-3xl sm:text-4xl font-black text-foreground">&lt; 2s</div>
            <div class="text-[11px] text-muted-foreground uppercase tracking-wider">Streaming LLM</div>
          </div>
          <div class="space-y-1">
            <div class="text-3xl sm:text-4xl font-black text-foreground">100%</div>
            <div class="text-[11px] text-muted-foreground uppercase tracking-wider">Confidentialité Données</div>
          </div>
          <div class="space-y-1">
            <div class="text-3xl sm:text-4xl font-black text-foreground">0</div>
            <div class="text-[11px] text-muted-foreground uppercase tracking-wider">Jargon Inutile</div>
          </div>
        </div>
      </div>
    </section>

    <!-- METHOD & WORKFLOW (3 Steps) -->
    <section id="how-it-works" class="py-24 sm:py-32 border-b border-zinc-200 dark:border-zinc-800">
      <div class="max-w-5xl mx-auto px-6 lg:px-8">
        <div class="mb-16">
          <div class="text-xs font-mono italic text-muted-foreground mb-3">_Méthodologie_</div>
          <h2 class="text-3xl sm:text-5xl font-black tracking-tight text-foreground">
            Simple, rigoureux, efficace.
          </h2>
        </div>

        <div class="grid md:grid-cols-3 gap-8">
          <!-- Step 1 -->
          <div class="p-8 rounded-2xl bg-card border border-border space-y-4">
            <div class="w-9 h-9 rounded-full bg-zinc-100 dark:bg-zinc-800 flex items-center justify-center text-xs font-mono font-bold text-foreground">
              01
            </div>
            <h3 class="text-lg font-bold text-foreground">Importation du Dossier</h3>
            <p class="text-xs sm:text-sm text-muted-foreground leading-relaxed font-normal">
              Déposez votre CV au format PDF ou collez le texte direct. Ajoutez le texte de l'offre d'emploi ciblée.
            </p>
          </div>

          <!-- Step 2 -->
          <div class="p-8 rounded-2xl bg-card border border-border space-y-4">
            <div class="w-9 h-9 rounded-full bg-zinc-100 dark:bg-zinc-800 flex items-center justify-center text-xs font-mono font-bold text-foreground">
              02
            </div>
            <h3 class="text-lg font-bold text-foreground">Analyse & Match</h3>
            <p class="text-xs sm:text-sm text-muted-foreground leading-relaxed font-normal">
              Gemini extrait la taxonomie du poste, évalue la couverture de votre CV et génère des suggestions de reformulation ATS.
            </p>
          </div>

          <!-- Step 3 -->
          <div class="p-8 rounded-2xl bg-card border border-border space-y-4">
            <div class="w-9 h-9 rounded-full bg-zinc-100 dark:bg-zinc-800 flex items-center justify-center text-xs font-mono font-bold text-foreground">
              03
            </div>
            <h3 class="text-lg font-bold text-foreground">Simulation d'Entretien</h3>
            <p class="text-xs sm:text-sm text-muted-foreground leading-relaxed font-normal">
              Répondez aux questions ciblées sur vos angles morts et obtenez un feedback instantané avec conseils d'amélioration.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- FINAL CALL TO ACTION -->
    <section class="py-24 sm:py-32 relative overflow-hidden">
      <div class="max-w-4xl mx-auto px-6 lg:px-8 relative z-10 text-center">
        <div class="reveal-scale rounded-3xl p-10 sm:p-16 bg-zinc-900 text-white relative overflow-hidden border border-zinc-800 shadow-2xl">
          <div class="absolute -top-24 -left-24 w-80 h-80 bg-indigo-500/20 blur-[100px] rounded-full pointer-events-none"></div>
          <div class="absolute -bottom-24 -right-24 w-80 h-80 bg-purple-500/20 blur-[100px] rounded-full pointer-events-none"></div>

          <div class="text-xs font-mono italic text-zinc-400 mb-4">_L'analyse suivante est à vous._</div>

          <h2 class="text-3xl sm:text-5xl font-black tracking-tight mb-6 relative z-10 leading-tight">
            Prêt à faire la différence lors de votre prochaine candidature ?
          </h2>
          <p class="text-zinc-400 text-sm sm:text-base mb-10 max-w-xl mx-auto relative z-10 font-normal leading-relaxed">
            Profitez dès maintenant d'une analyse sémantique offerte, sans carte bancaire ni configuration complexe.
          </p>

          <a @click="startAnalysis" class="cursor-pointer inline-flex items-center gap-3 px-8 py-4 bg-white text-zinc-900 hover:bg-zinc-100 font-semibold rounded-full transition-all hover:scale-105 shadow-glow relative z-10 text-sm">
            <span>Commencer une analyse gratuite</span>
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
          </a>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import gsap from 'gsap'
import ScrollTrigger from 'gsap/ScrollTrigger'
import Lenis from 'lenis'

gsap.registerPlugin(ScrollTrigger)

const router = useRouter()
const authStore = useAuthStore()

const activeDemoTab = ref<'analysis' | 'interview'>('analysis')
let lenis: Lenis | null = null

const startAnalysis = () => {
  router.push('/free-trial')
}

onMounted(() => {
  // Initialize Lenis smooth scroll
  lenis = new Lenis({
    duration: 1.2,
    easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
    smoothWheel: true,
  })

  lenis.on('scroll', ScrollTrigger.update)

  const updateTicker = (time: number) => {
    lenis?.raf(time * 1000)
  }

  gsap.ticker.add(updateTicker)
  gsap.ticker.lagSmoothing(0)

  // GSAP Animations
  const tl = gsap.timeline()

  tl.to('.hero-anim', {
    y: 0,
    opacity: 1,
    duration: 0.9,
    stagger: 0.12,
    ease: 'power3.out'
  }).to('.hero-ui', {
    opacity: 1,
    y: -10,
    duration: 1,
    ease: 'power2.out'
  }, "-=0.4")

  // CTA Scale animation
  gsap.from('.reveal-scale', {
    scrollTrigger: {
      trigger: '.reveal-scale',
      start: "top 90%",
    },
    scale: 0.95,
    opacity: 0,
    duration: 0.8,
    ease: 'power2.out'
  })
})

onUnmounted(() => {
  if (lenis) {
    lenis.destroy()
    lenis = null
  }
})
</script>
