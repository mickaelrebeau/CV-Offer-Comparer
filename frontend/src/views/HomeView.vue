<template>
  <div class="overflow-x-hidden relative bg-background text-foreground">
    <!-- HERO SECTION -->
    <section class="relative pt-24 pb-20 lg:pt-36 lg:pb-32 overflow-hidden">
      <!-- Background Ambient Grid & Radial Glow -->
      <div class="absolute inset-0 bg-grid-pattern opacity-40 pointer-events-none"></div>
      <div class="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-radial-gradient opacity-80 pointer-events-none"></div>

      <div class="max-w-7xl mx-auto px-6 lg:px-8 relative z-10">
        <div class="flex flex-col items-center text-center max-w-4xl mx-auto">
          
          <!-- Minimalist Apple-style Pill Badge -->
          <div class="hero-anim opacity-0 translate-y-6 inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-zinc-100 dark:bg-zinc-800/80 border border-zinc-200 dark:border-zinc-700/80 text-xs font-semibold tracking-wide text-foreground mb-8 shadow-sm">
            <span class="w-2 h-2 rounded-full bg-indigo-500 animate-pulse"></span>
            <span>CV OFFER COMPARER 2.0</span>
            <span class="text-muted-foreground font-normal">|</span>
            <span class="text-muted-foreground font-normal">SÉMANTIQUE & SIMULATION</span>
          </div>

          <!-- Main Impact Headline -->
          <h1 class="hero-anim opacity-0 translate-y-6 text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-extrabold tracking-tight mb-8 leading-[1.05]">
            Passez le filtre ATS.<br />
            <span class="text-gradient-indigo">Décrochez l'entretien.</span>
          </h1>

          <!-- Crisp Subhead -->
          <p class="hero-anim opacity-0 translate-y-6 text-base sm:text-lg md:text-xl text-muted-foreground mb-10 max-w-2xl leading-relaxed font-normal">
            Alignez la structure de votre CV avec les exigences exactes de l'offre d'emploi.
            Détectez les compétences manquantes et entraînez-vous aux questions d'entretien.
          </p>

          <!-- Primary CTA Buttons -->
          <div class="hero-anim opacity-0 translate-y-6 flex flex-col sm:flex-row items-center gap-4 w-full sm:w-auto">
            <a @click="startAnalysis" class="cursor-pointer w-full sm:w-auto px-8 py-4 rounded-full bg-foreground text-background font-semibold text-sm hover:opacity-90 transition-all shadow-glow hover:shadow-glow-lg flex items-center justify-center gap-2 group">
              <span>Lancer une analyse offerte</span>
              <svg class="w-4 h-4 group-hover:translate-x-1 transition-transform" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M5 12h14M12 5l7 7-7 7"/>
              </svg>
            </a>
            <a href="#how-it-works" class="cursor-pointer w-full sm:w-auto px-8 py-4 rounded-full bg-zinc-100 dark:bg-zinc-800/60 hover:bg-zinc-200 dark:hover:bg-zinc-800 text-foreground font-medium text-sm transition-all border border-zinc-200/80 dark:border-zinc-700/80 flex items-center justify-center">
              Explorer la méthode
            </a>
          </div>
        </div>

        <!-- Interactive Awwwards-grade Live Preview Showcase -->
        <div id="architecture" class="hero-ui opacity-0 mt-16 sm:mt-24 relative max-w-5xl mx-auto scroll-mt-24">
          <div class="glass-panel rounded-2xl shadow-2xl overflow-hidden border border-zinc-200/80 dark:border-zinc-800">
            <!-- Window Control Header -->
            <div class="h-11 px-5 flex items-center justify-between bg-zinc-100/80 dark:bg-zinc-900/80 border-b border-zinc-200/80 dark:border-zinc-800">
              <div class="flex items-center gap-2">
                <div class="w-3 h-3 rounded-full bg-zinc-300 dark:bg-zinc-700"></div>
                <div class="w-3 h-3 rounded-full bg-zinc-300 dark:bg-zinc-700"></div>
                <div class="w-3 h-3 rounded-full bg-zinc-300 dark:bg-zinc-700"></div>
                <span class="ml-2 text-xs font-medium text-muted-foreground font-mono">cv-offer-comparator.app — Preview</span>
              </div>
              <div class="flex items-center gap-2">
                <button @click="activeDemoTab = 'analysis'" class="px-3 py-1 text-xs font-medium rounded-md transition-colors" :class="activeDemoTab === 'analysis' ? 'bg-background text-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'">
                  Analyse ATS
                </button>
                <button @click="activeDemoTab = 'interview'" class="px-3 py-1 text-xs font-medium rounded-md transition-colors" :class="activeDemoTab === 'interview' ? 'bg-background text-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'">
                  Simulation Entretien
                </button>
              </div>
            </div>

            <!-- Tab Content: ATS Analysis -->
            <div v-if="activeDemoTab === 'analysis'" class="p-6 sm:p-8 bg-background/50 space-y-6">
              <div class="grid md:grid-cols-3 gap-6 items-center">
                <!-- Score Gauge -->
                <div class="p-6 rounded-xl bg-card border border-border flex flex-col items-center justify-center text-center">
                  <div class="text-xs uppercase tracking-wider font-semibold text-muted-foreground mb-3">Score d'Adéquation</div>
                  <div class="relative w-28 h-28 flex items-center justify-center">
                    <svg class="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                      <path class="text-zinc-200 dark:text-zinc-800" stroke-width="3" stroke="currentColor" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                      <path class="text-emerald-500" stroke-linecap="round" stroke-dasharray="88, 100" stroke-width="3.2" stroke="currentColor" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                    </svg>
                    <span class="absolute text-3xl font-extrabold tracking-tight">88%</span>
                  </div>
                  <span class="mt-3 text-xs font-semibold px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                    Forte Correspondance ATS
                  </span>
                </div>

                <!-- Missing vs Matched Key Skills -->
                <div class="md:col-span-2 space-y-4">
                  <div class="p-4 rounded-xl bg-card border border-border space-y-2">
                    <div class="flex items-center justify-between text-xs">
                      <span class="font-semibold text-emerald-600 dark:text-emerald-400 flex items-center gap-1.5">
                        <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
                        Compétences Détectées (12)
                      </span>
                      <span class="text-muted-foreground">Match parfait</span>
                    </div>
                    <div class="flex flex-wrap gap-1.5 pt-1">
                      <span v-for="skill in ['TypeScript', 'Vue 3 / React', 'Tailwind CSS', 'API REST', 'Git', 'Node.js']" :key="skill" class="text-xs px-2.5 py-1 rounded-md bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 font-medium">
                        ✓ {{ skill }}
                      </span>
                    </div>
                  </div>

                  <div class="p-4 rounded-xl bg-card border border-border space-y-2">
                    <div class="flex items-center justify-between text-xs">
                      <span class="font-semibold text-rose-500 flex items-center gap-1.5">
                        <span class="w-2 h-2 rounded-full bg-rose-500"></span>
                        Mots-Clés Requis Manquants (2)
                      </span>
                      <span class="text-muted-foreground">Action recommandée</span>
                    </div>
                    <div class="flex flex-wrap gap-1.5 pt-1">
                      <span v-for="missing in ['Docker / Containerization', 'Tests Unitaires (Jest / Vitest)']" :key="missing" class="text-xs px-2.5 py-1 rounded-md bg-rose-500/10 text-rose-600 dark:text-rose-400 font-medium">
                        + {{ missing }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Tab Content: Interview Simulator -->
            <div v-else class="p-6 sm:p-8 bg-background/50 space-y-4">
              <div class="p-4 rounded-xl bg-card border border-border space-y-3">
                <div class="flex items-center justify-between">
                  <span class="text-xs font-semibold uppercase tracking-wider text-indigo-500">Question 1 / 5 • Technique</span>
                  <span class="text-xs text-muted-foreground font-mono">02:15</span>
                </div>
                <p class="text-sm font-semibold text-foreground">
                  "Vous mentionnez l'utilisation de Vue 3 et TypeScript. Comment optimisez-vous les performances de rendu lors du chargement de listes volumineuses ?"
                </p>
              </div>

              <div class="p-4 rounded-xl bg-indigo-50/50 dark:bg-indigo-950/20 border border-indigo-200/50 dark:border-indigo-800/40 space-y-2">
                <div class="text-xs font-semibold text-indigo-600 dark:text-indigo-400 flex items-center gap-1.5">
                  <span>💡 Recommandation de Réponse & Mots-Clés</span>
                </div>
                <p class="text-xs text-muted-foreground leading-relaxed">
                  Mentionnez l'utilisation de la virtualisation de liste (Virtual Scrolling), du lazy loading des composants, et de la mémoïsation avec <code class="px-1 py-0.5 rounded bg-zinc-200 dark:bg-zinc-800 font-mono">computed</code>.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- METRICS TICKER / STRIP (Apple Editorial Style) -->
    <section class="py-12 border-y border-zinc-200/80 dark:border-zinc-800/80 bg-zinc-50/50 dark:bg-zinc-900/30">
      <div class="max-w-7xl mx-auto px-6 lg:px-8">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          <div class="space-y-1">
            <div class="text-3xl sm:text-4xl font-extrabold tracking-tight text-foreground">94%</div>
            <div class="text-xs text-muted-foreground uppercase tracking-wider font-medium">Taux de passage ATS</div>
          </div>
          <div class="space-y-1">
            <div class="text-3xl sm:text-4xl font-extrabold tracking-tight text-foreground">&lt; 15s</div>
            <div class="text-xs text-muted-foreground uppercase tracking-wider font-medium">Analyse Sémantique</div>
          </div>
          <div class="space-y-1">
            <div class="text-3xl sm:text-4xl font-extrabold tracking-tight text-foreground">100%</div>
            <div class="text-xs text-muted-foreground uppercase tracking-wider font-medium">Confidentialité Locale</div>
          </div>
          <div class="space-y-1">
            <div class="text-3xl sm:text-4xl font-extrabold tracking-tight text-foreground">0</div>
            <div class="text-xs text-muted-foreground uppercase tracking-wider font-medium">Jargon / Clarté Pure</div>
          </div>
        </div>
      </div>
    </section>

    <!-- BENTO GRID FEATURES (Inspired by Apple & Content Architecture) -->
    <section id="features" class="py-24 sm:py-32 relative">
      <div class="max-w-7xl mx-auto px-6 lg:px-8">
        <div class="text-center max-w-3xl mx-auto mb-16 sm:mb-20 reveal-up">
          <p class="text-xs font-bold uppercase tracking-widest text-indigo-500 mb-3">Ingénierie de Candidature</p>
          <h2 class="text-3xl sm:text-5xl font-bold tracking-tight text-foreground mb-4">
            Tout le nécessaire pour franchir les filtres.
          </h2>
          <p class="text-base sm:text-lg text-muted-foreground">
            Une suite d'outils analytiques conçus avec la méticulosité d'un studio d'architecture.
          </p>
        </div>

        <div class="grid md:grid-cols-3 gap-6 sm:gap-8">
          <!-- Bento Card 1: Large Span -->
          <div class="md:col-span-2 glass-card p-8 sm:p-10 rounded-2xl flex flex-col justify-between relative overflow-hidden group">
            <div class="space-y-4 max-w-lg z-10">
              <span class="text-xs font-mono px-2.5 py-1 rounded bg-zinc-100 dark:bg-zinc-800 text-muted-foreground">01 / DIAGNOSTIC</span>
              <h3 class="text-2xl sm:text-3xl font-bold tracking-tight text-foreground">
                Analyse d'Écart Sémantique (Gap Analysis)
              </h3>
              <p class="text-sm sm:text-base text-muted-foreground leading-relaxed">
                Les logiciels de recrutement (ATS) éliminent automatiquement les profils ne présentant pas les termes exacts de la fiche de poste. Notre moteur compare votre texte et extrait instantanément les écarts stratégiques.
              </p>
            </div>
            
            <div class="mt-8 pt-6 border-t border-border flex items-center justify-between text-xs text-muted-foreground">
              <span class="flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
                Analyse par paires de termes
              </span>
              <span class="font-mono">Realtime Processing</span>
            </div>
          </div>

          <!-- Bento Card 2 -->
          <div class="glass-card p-8 sm:p-10 rounded-2xl flex flex-col justify-between relative overflow-hidden group">
            <div class="space-y-4">
              <span class="text-xs font-mono px-2.5 py-1 rounded bg-zinc-100 dark:bg-zinc-800 text-muted-foreground">02 / SCORE</span>
              <h3 class="text-xl sm:text-2xl font-bold tracking-tight text-foreground">
                Score de Matching Précis
              </h3>
              <p class="text-sm text-muted-foreground leading-relaxed">
                Un indice global calculé sur la pondération des hard skills, soft skills et prérequis spécifiques de l'employeur.
              </p>
            </div>

            <div class="mt-8 flex items-baseline gap-2">
              <span class="text-4xl font-extrabold text-foreground">88%</span>
              <span class="text-xs text-emerald-500 font-medium">Seuil d'Entretien Vise</span>
            </div>
          </div>

          <!-- Bento Card 3 -->
          <div class="glass-card p-8 sm:p-10 rounded-2xl flex flex-col justify-between relative overflow-hidden group">
            <div class="space-y-4">
              <span class="text-xs font-mono px-2.5 py-1 rounded bg-zinc-100 dark:bg-zinc-800 text-muted-foreground">03 / SIMULATION</span>
              <h3 class="text-xl sm:text-2xl font-bold tracking-tight text-foreground">
                Simulateur d'Entretien
              </h3>
              <p class="text-sm text-muted-foreground leading-relaxed">
                Entraînez-vous sur des questions générées d'après les zones d'ombre de votre profil face à l'offre.
              </p>
            </div>

            <div class="mt-8">
              <span class="text-xs font-medium text-indigo-500 flex items-center gap-1">
                <span>Démarrer un entraînement</span>
                <span>→</span>
              </span>
            </div>
          </div>

          <!-- Bento Card 4: Large Span -->
          <div class="md:col-span-2 glass-card p-8 sm:p-10 rounded-2xl flex flex-col justify-between relative overflow-hidden group">
            <div class="space-y-4 max-w-lg z-10">
              <span class="text-xs font-mono px-2.5 py-1 rounded bg-zinc-100 dark:bg-zinc-800 text-muted-foreground">04 / OPTIMISATION</span>
              <h3 class="text-2xl sm:text-3xl font-bold tracking-tight text-foreground">
                Recommandations de Reformulation Directes
              </h3>
              <p class="text-sm sm:text-base text-muted-foreground leading-relaxed">
                Recevez des propositions concrètes de phrases d'impact pour enrichir votre CV sans dénaturer vos réalisations réelles. Copiez en 1-clic dans votre éditeur.
              </p>
            </div>

            <div class="mt-8 pt-6 border-t border-border flex items-center justify-between text-xs text-muted-foreground">
              <span>Suggestions de tournures ATS-friendly</span>
              <span class="font-mono">1-Click Copy</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- METHOD & WORKFLOW (Apple Style Horizontal Steps) -->
    <section id="how-it-works" class="py-24 sm:py-32 border-t border-zinc-200/80 dark:border-zinc-800/80 bg-zinc-50/30 dark:bg-zinc-950/20">
      <div class="max-w-7xl mx-auto px-6 lg:px-8">
        <div class="max-w-3xl mb-16 sm:mb-20">
          <p class="text-xs font-bold uppercase tracking-widest text-indigo-500 mb-3">Workflow en 3 étapes</p>
          <h2 class="text-3xl sm:text-5xl font-bold tracking-tight text-foreground">
            Simple, rigoureux, efficace.
          </h2>
        </div>

        <div class="grid md:grid-cols-3 gap-8 relative">
          <!-- Step 1 -->
          <div class="step-card space-y-4 p-8 rounded-2xl bg-card border border-border">
            <div class="w-10 h-10 rounded-full bg-zinc-100 dark:bg-zinc-800 flex items-center justify-center text-sm font-bold font-mono text-foreground">
              01
            </div>
            <h3 class="text-xl font-bold text-foreground">Importation</h3>
            <p class="text-sm text-muted-foreground leading-relaxed">
              Déposez votre CV au format PDF ou collez directement le texte. Ajoutez l'offre d'emploi visée.
            </p>
          </div>

          <!-- Step 2 -->
          <div class="step-card space-y-4 p-8 rounded-2xl bg-card border border-border">
            <div class="w-10 h-10 rounded-full bg-zinc-100 dark:bg-zinc-800 flex items-center justify-center text-sm font-bold font-mono text-foreground">
              02
            </div>
            <h3 class="text-xl font-bold text-foreground">Analyse & Diagnostic</h3>
            <p class="text-sm text-muted-foreground leading-relaxed">
              Le moteur extrait les entités, mots-clés clés et évalue le taux de concordance de votre dossier.
            </p>
          </div>

          <!-- Step 3 -->
          <div class="step-card space-y-4 p-8 rounded-2xl bg-card border border-border">
            <div class="w-10 h-10 rounded-full bg-zinc-100 dark:bg-zinc-800 flex items-center justify-center text-sm font-bold font-mono text-foreground">
              03
            </div>
            <h3 class="text-xl font-bold text-foreground">Optimisation & Préparation</h3>
            <p class="text-sm text-muted-foreground leading-relaxed">
              Ajustez votre CV avec les suggestions proposées et lancez une simulation d'entretien interactive.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- AWWWARDS-GRADE FINAL CTA SECTION -->
    <section class="py-24 sm:py-32 relative overflow-hidden">
      <div class="max-w-5xl mx-auto px-6 lg:px-8 relative z-10">
        <div class="reveal-scale rounded-3xl p-10 sm:p-16 md:p-20 text-center bg-zinc-900 text-white relative overflow-hidden border border-zinc-800 shadow-2xl">
          <!-- Inner Ambient Glow -->
          <div class="absolute -top-24 -left-24 w-96 h-96 bg-indigo-500/20 blur-[100px] rounded-full pointer-events-none"></div>
          <div class="absolute -bottom-24 -right-24 w-96 h-96 bg-purple-500/20 blur-[100px] rounded-full pointer-events-none"></div>

          <h2 class="text-3xl sm:text-5xl font-extrabold tracking-tight mb-6 relative z-10 leading-tight">
            Prêt à transformer vos candidatures ?
          </h2>
          <p class="text-zinc-400 text-base sm:text-lg mb-10 max-w-xl mx-auto relative z-10 font-normal leading-relaxed">
            Profitez dès maintenant d'une analyse gratuite sans inscription obligatoire.
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

  // Upward reveals for features
  gsap.utils.toArray('.reveal-up').forEach((elem: any) => {
    gsap.from(elem, {
      scrollTrigger: {
        trigger: elem,
        start: "top 85%",
      },
      y: 40,
      opacity: 0,
      duration: 0.9,
      ease: 'power3.out'
    })
  })

  // Step cards stagger
  gsap.from('.step-card', {
    scrollTrigger: {
      trigger: '#how-it-works',
      start: "top 75%",
    },
    y: 30,
    opacity: 0,
    duration: 0.8,
    stagger: 0.15,
    ease: 'power2.out'
  })

  // CTA Scale animation
  gsap.from('.reveal-scale', {
    scrollTrigger: {
      trigger: '.reveal-scale',
      start: "top 90%",
    },
    scale: 0.94,
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
