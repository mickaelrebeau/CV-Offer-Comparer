<template>
  <div class="min-h-screen bg-[#09090b] text-[#fafafa] font-sans antialiased selection:bg-zinc-800 selection:text-white">
    
    <!-- TOP SUBTLE NAVIGATION HEADER (ContentArchitecture Style) -->
    <header class="border-b border-zinc-800/80 sticky top-0 z-50 bg-[#09090b]/90 backdrop-blur-md">
      <div class="max-w-4xl mx-auto px-6 h-14 flex items-center justify-between text-xs font-mono">
        <a @click="handleLogoClick" class="cursor-pointer flex items-center gap-2 hover:text-white transition-colors">
          <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
          <span class="font-bold tracking-tight text-white">CV OFFER COMPARER</span>
        </a>

        <nav class="hidden sm:flex items-center gap-6 text-zinc-400">
          <a href="#problems" class="hover:text-white transition-colors">_problems</a>
          <a href="#decisions" class="hover:text-white transition-colors">_architecture</a>
          <a href="#workbench" class="hover:text-white transition-colors">_workbench</a>
          <a href="#pricing" class="hover:text-white transition-colors">_access</a>
        </nav>

        <div class="flex items-center gap-3">
          <template v-if="!authStore.isAuthenticated">
            <a @click="navigateTo('/login')" class="cursor-pointer text-zinc-400 hover:text-white transition-colors">
              login
            </a>
            <a @click="startAnalysis" class="cursor-pointer px-3 py-1 rounded bg-white text-zinc-950 font-semibold hover:bg-zinc-200 transition-colors">
              [get access]
            </a>
          </template>
          <template v-else>
            <a @click="navigateTo('/dashboard')" class="cursor-pointer text-zinc-400 hover:text-white transition-colors">
              [dashboard]
            </a>
          </template>
        </div>
      </div>
    </header>

    <main class="max-w-4xl mx-auto px-6 py-16 sm:py-24 space-y-24 sm:space-y-32">

      <!-- HERO SECTION -->
      <section class="space-y-8">
        <div class="space-y-2">
          <p class="text-xs sm:text-sm font-mono italic text-zinc-400">
            _Built for high-stakes candidacies & ATS precision._
          </p>
          <h1 class="text-4xl sm:text-6xl md:text-7xl font-bold tracking-tight text-white leading-[1.08]">
            The ATS architecture candidates don't reinvent.
          </h1>
        </div>

        <p class="text-base sm:text-xl text-zinc-300 leading-relaxed font-normal max-w-2xl">
          Every job hunt invents a new CV strategy, none decided. This Gemini-powered platform commits years of recruitment and ATS parsing decisions. Your application aligns inside them, in real-time.
        </p>

        <p class="text-xs sm:text-sm font-mono italic text-zinc-400">
          _For candidates who value precision, speed, and zero fluff._
        </p>

        <div class="pt-2 flex flex-col sm:flex-row sm:items-center gap-4 text-xs font-mono">
          <a @click="startAnalysis" class="cursor-pointer inline-flex items-center justify-center px-6 py-3 rounded bg-white text-zinc-950 font-bold hover:bg-zinc-200 transition-all">
            [Start free analysis]
          </a>
          <a href="#workbench" class="inline-flex items-center justify-center px-6 py-3 rounded border border-zinc-800 text-zinc-300 hover:border-zinc-700 hover:text-white transition-all">
            Explore the workbench ↓
          </a>
        </div>
      </section>

      <!-- SECTION: COMMON PROBLEMS -->
      <section id="problems" class="pt-12 border-t border-zinc-800 space-y-8">
        <div class="space-y-2">
          <p class="text-xs sm:text-sm font-mono italic text-zinc-400">
            _Common problems_
          </p>
          <h2 class="text-2xl sm:text-4xl font-bold tracking-tight text-white leading-tight">
            The manual ATS tailoring costs you days. Every single time.
          </h2>
        </div>

        <p class="text-sm sm:text-base text-zinc-300 leading-relaxed max-w-3xl">
          It's never the easy stuff that hurts. It's formatting the CV again. Matching exact keywords and subtle variations, wired up and subtly rejected again. The rejection email where your profile was filtered before a human ever saw it. A CV structure recruiters actually understand, instead of one they skim over.
        </p>

        <p class="text-xs sm:text-sm text-zinc-400 font-mono italic">
          This is the part nobody quotes for and everybody rebuilds. Hours gone before the real interview starts.
        </p>

        <!-- Time lost breakdown table -->
        <div class="space-y-2 font-mono text-xs sm:text-sm border-t border-b border-zinc-800/80 py-4">
          <div class="py-2.5 flex items-center justify-between gap-4 border-b border-zinc-900">
            <span class="text-zinc-300">- Candidate redesigns CV architecture on every prompt</span>
            <span class="text-zinc-500 font-semibold shrink-0">(∞ HRS)</span>
          </div>
          <div class="py-2.5 flex items-center justify-between gap-4 border-b border-zinc-900">
            <span class="text-zinc-300">- Keyword density & synonym matching from job post</span>
            <span class="text-zinc-500 font-semibold shrink-0">(~3 HRS)</span>
          </div>
          <div class="py-2.5 flex items-center justify-between gap-4 border-b border-zinc-900">
            <span class="text-zinc-300">- Identifying missing hard skills & experience gaps</span>
            <span class="text-zinc-500 font-semibold shrink-0">(~2 HRS)</span>
          </div>
          <div class="py-2.5 flex items-center justify-between gap-4 border-b border-zinc-900">
            <span class="text-zinc-300">- Drafting tailored bullet points & impact statements</span>
            <span class="text-zinc-500 font-semibold shrink-0">(~2 HRS)</span>
          </div>
          <div class="py-2.5 flex items-center justify-between gap-4 border-b border-zinc-900">
            <span class="text-zinc-300">- Preparing for recruiter technical & behavioral questions</span>
            <span class="text-zinc-500 font-semibold shrink-0">(~3 HRS)</span>
          </div>
          <div class="py-2.5 flex items-center justify-between gap-4">
            <span class="text-zinc-300">- PDF formatting & ATS parser compatibility check</span>
            <span class="text-zinc-500 font-semibold shrink-0">(~1 HR)</span>
          </div>
        </div>

        <div class="text-xs font-mono text-amber-400/90 tracking-wide">
          _ESTIMATED TIME LOST: ~11 HOURS PER APPLICATION (1.5 FULL DAYS)_
        </div>
      </section>

      <!-- SECTION: DECISIONS MADE -->
      <section id="decisions" class="pt-12 border-t border-zinc-800 space-y-8">
        <div class="space-y-2">
          <p class="text-xs sm:text-sm font-mono italic text-zinc-400">
            _Architecture_
          </p>
          <h2 class="text-2xl sm:text-4xl font-bold tracking-tight text-white leading-tight">
            Every decision already made. So you can skip to the actual interview.
          </h2>
        </div>

        <p class="text-sm sm:text-base text-zinc-300 leading-relaxed max-w-3xl">
          The CV Offer Architecture is the production foundation underneath successful candidacies. Hundreds of choices—schema, parsing, sifting, structure, scoring—made once and committed. Not a generic resume builder you outgrow in a week. Input your documents; the architecture is fixed, the analysis is instant. Fixed decisions are what make AI work: an engine inside committed conventions ships results, an engine without them hallucinates.
        </p>

        <!-- Bulleted Decision List -->
        <ul class="space-y-6 text-sm text-zinc-300">
          <li class="space-y-1">
            <div class="font-bold text-white flex items-center gap-2">
              <span class="text-emerald-500 font-mono">•</span>
              <span>Gemini-native single-pass pipeline:</span>
            </div>
            <p class="text-zinc-400 text-xs sm:text-sm leading-relaxed pl-4">
              A single structured Gemini call extracts job requirements, calculates confidence scores across categories, and streams results over SSE in under 2 seconds. No chained prompts, no API lag.
            </p>
          </li>

          <li class="space-y-1">
            <div class="font-bold text-white flex items-center gap-2">
              <span class="text-emerald-500 font-mono">•</span>
              <span>Categorized Gap Analysis:</span>
            </div>
            <p class="text-zinc-400 text-xs sm:text-sm leading-relaxed pl-4">
              Hard skills, soft skills, languages, experience levels, and certifications are isolated automatically into clean buckets with specific match thresholds.
            </p>
          </li>

          <li class="space-y-1">
            <div class="font-bold text-white flex items-center gap-2">
              <span class="text-emerald-500 font-mono">•</span>
              <span>Synonym & term normalization:</span>
            </div>
            <p class="text-zinc-400 text-xs sm:text-sm leading-relaxed pl-4">
              "Vue.js" and "Vue 3", "PostgreSQL" and "Postgres", or "bilingue" and "anglais courant" are recognized as matches. The engine evaluates semantic intent rather than dumb string matching.
            </p>
          </li>

          <li class="space-y-1">
            <div class="font-bold text-white flex items-center gap-2">
              <span class="text-emerald-500 font-mono">•</span>
              <span>Interview Studio:</span>
            </div>
            <p class="text-zinc-400 text-xs sm:text-sm leading-relaxed pl-4">
              Generates 10 tailored interview questions based on the exact gap between your profile and the job description, then provides actionable feedback on your responses.
            </p>
          </li>

          <li class="space-y-1">
            <div class="font-bold text-white flex items-center gap-2">
              <span class="text-emerald-500 font-mono">•</span>
              <span>1-Click Reformulations:</span>
            </div>
            <p class="text-zinc-400 text-xs sm:text-sm leading-relaxed pl-4">
              Provides impact-driven, ATS-friendly phrasing for missing or unclear qualifications that you can copy directly into your document.
            </p>
          </li>

          <li class="space-y-1">
            <div class="font-bold text-white flex items-center gap-2">
              <span class="text-emerald-500 font-mono">•</span>
              <span>Privacy & security built-in:</span>
            </div>
            <p class="text-zinc-400 text-xs sm:text-sm leading-relaxed pl-4">
              PostgreSQL + Redis session control with JWT authentication. Documents are processed in memory and never stored or sold to third parties.
            </p>
          </li>
        </ul>
      </section>

      <!-- SECTION: INTERACTIVE WORKBENCH (REAL PREVIEW) -->
      <section id="workbench" class="pt-12 border-t border-zinc-800 space-y-6">
        <div class="space-y-2">
          <p class="text-xs sm:text-sm font-mono italic text-zinc-400">
            _Interactive preview_
          </p>
          <h2 class="text-2xl sm:text-4xl font-bold tracking-tight text-white leading-tight">
            This is the actual workbench.
          </h2>
        </div>

        <div class="border border-zinc-800 rounded-lg bg-[#0c0c0e] overflow-hidden font-mono text-xs">
          <!-- Window Bar -->
          <div class="h-10 px-4 flex items-center justify-between border-b border-zinc-800 bg-[#121215]">
            <div class="flex items-center gap-2 text-zinc-400">
              <span class="w-2.5 h-2.5 rounded-full bg-zinc-700"></span>
              <span class="w-2.5 h-2.5 rounded-full bg-zinc-700"></span>
              <span class="w-2.5 h-2.5 rounded-full bg-zinc-700"></span>
              <span class="ml-2 text-zinc-400 text-[11px]">cv-offer-comparer.app — workbench</span>
            </div>

            <div class="flex items-center gap-1">
              <button 
                @click="activeDemoTab = 'analysis'"
                class="px-2.5 py-1 rounded transition-colors"
                :class="activeDemoTab === 'analysis' ? 'bg-zinc-800 text-white font-bold' : 'text-zinc-500 hover:text-zinc-300'"
              >
                [01 / ATS Analysis]
              </button>
              <button 
                @click="activeDemoTab = 'interview'"
                class="px-2.5 py-1 rounded transition-colors"
                :class="activeDemoTab === 'interview' ? 'bg-zinc-800 text-white font-bold' : 'text-zinc-500 hover:text-zinc-300'"
              >
                [02 / Interview Studio]
              </button>
            </div>
          </div>

          <!-- Workbench Content: ATS Analysis -->
          <div v-if="activeDemoTab === 'analysis'" class="p-6 space-y-6">
            <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-zinc-800/80 pb-6">
              <div>
                <div class="text-zinc-500 text-[11px]">MATCHING SCORE</div>
                <div class="text-3xl sm:text-4xl font-bold text-white tracking-tight">88%</div>
              </div>

              <div class="flex items-center gap-2 text-emerald-400 bg-emerald-950/40 border border-emerald-800/60 px-3 py-1.5 rounded">
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                <span>STATUS: MATCH ATS VALIDE</span>
              </div>
            </div>

            <div class="space-y-4">
              <div>
                <div class="text-zinc-500 text-[11px] mb-2">DETECTED SKILLS (12)</div>
                <div class="flex flex-wrap gap-2">
                  <span v-for="skill in ['TypeScript', 'Vue 3 / React', 'Tailwind CSS', 'FastAPI / Python', 'Git CI/CD', 'PostgreSQL']" :key="skill" class="px-2.5 py-1 rounded bg-zinc-900 border border-zinc-800 text-emerald-400 font-mono">
                    ✓ {{ skill }}
                  </span>
                </div>
              </div>

              <div>
                <div class="text-zinc-500 text-[11px] mb-2">MISSING REQUIREMENTS (2)</div>
                <div class="flex flex-wrap gap-2">
                  <span v-for="missing in ['Docker / Containerization', 'Unit Tests (Vitest / Pytest)']" :key="missing" class="px-2.5 py-1 rounded bg-zinc-900 border border-zinc-800 text-rose-400 font-mono">
                    + {{ missing }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Workbench Content: Interview Studio -->
          <div v-else class="p-6 space-y-4">
            <div class="space-y-2 border-b border-zinc-800/80 pb-4">
              <div class="text-zinc-500 text-[11px]">QUESTION 01 / 05 • TECHNICAL PERFORMANCE</div>
              <p class="text-zinc-200 text-sm font-sans font-semibold leading-relaxed">
                "Vous mentionnez l'utilisation de Vue 3 et TypeScript. Comment optimisez-vous les performances de rendu lors du chargement de listes volumineuses ?"
              </p>
            </div>

            <div class="p-4 rounded bg-zinc-900/80 border border-zinc-800 space-y-2">
              <div class="text-indigo-400 text-[11px] font-bold">💡 RECOMMANDATION DE RÉPONSE</div>
              <p class="text-zinc-400 text-xs font-sans leading-relaxed">
                Axez votre réponse sur la virtualisation de liste (Virtual Scrolling), le lazy loading des composants, et la mémoïsation avec <code class="px-1 py-0.5 rounded bg-zinc-800 text-zinc-200 font-mono">computed</code>.
              </p>
            </div>
          </div>
        </div>
      </section>

      <!-- SECTION: SHOWCASE / METRICS -->
      <section class="pt-12 border-t border-zinc-800 space-y-8">
        <div class="space-y-2">
          <p class="text-xs sm:text-sm font-mono italic text-zinc-400">
            _The candidacies that get remembered._
          </p>
          <h2 class="text-2xl sm:text-4xl font-bold tracking-tight text-white leading-tight">
            Built for candidates who target top-tier roles.
          </h2>
        </div>

        <div class="grid grid-cols-2 md:grid-cols-4 gap-6 font-mono text-xs border-t border-b border-zinc-800/80 py-6">
          <div class="space-y-1">
            <div class="text-2xl sm:text-3xl font-bold text-white">94%</div>
            <div class="text-zinc-500 uppercase text-[10px]">ATS Pass Rate</div>
          </div>
          <div class="space-y-1">
            <div class="text-2xl sm:text-3xl font-bold text-white">&lt; 2s</div>
            <div class="text-zinc-500 uppercase text-[10px]">LLM Latency</div>
          </div>
          <div class="space-y-1">
            <div class="text-2xl sm:text-3xl font-bold text-white">100%</div>
            <div class="text-zinc-500 uppercase text-[10px]">Data Privacy</div>
          </div>
          <div class="space-y-1">
            <div class="text-2xl sm:text-3xl font-bold text-white">0</div>
            <div class="text-zinc-500 uppercase text-[10px]">Fluff & Jargon</div>
          </div>
        </div>
      </section>

      <!-- SECTION: ACCESS & PRICING -->
      <section id="pricing" class="pt-12 border-t border-zinc-800 space-y-8">
        <div class="space-y-2">
          <p class="text-xs sm:text-sm font-mono italic text-zinc-400">
            _Access_
          </p>
          <h2 class="text-2xl sm:text-4xl font-bold tracking-tight text-white leading-tight">
            One platform. Free trial included.
          </h2>
        </div>

        <div class="border border-zinc-800 rounded-lg p-6 sm:p-8 bg-[#0c0c0e] space-y-6 font-mono text-xs">
          <div class="flex items-baseline justify-between border-b border-zinc-800 pb-4">
            <span class="text-lg font-bold text-white">FREE TRIAL / ACCOUNT</span>
            <span class="text-emerald-400 font-bold">€0 / START FREE</span>
          </div>

          <ul class="space-y-2.5 text-zinc-300">
            <li class="flex items-center gap-2">• FREE TRIAL AVAILABLE WITH NO CREDIT CARD</li>
            <li class="flex items-center gap-2">• FULL GEMINI LLM STREAMING SSE ENGINE</li>
            <li class="flex items-center gap-2">• CATEGORIZED ATS GAP ANALYSIS & REFORMULATIONS</li>
            <li class="flex items-center gap-2">• INTERVIEW STUDIO & RESPONSE FEEDBACK</li>
            <li class="flex items-center gap-2">• PDF UPLOAD & AUTOMATIC TEXT EXTRACTION</li>
            <li class="flex items-center gap-2">• SECURE POSTGRESQL + REDIS SESSION CONTROL</li>
          </ul>

          <div class="pt-4 border-t border-zinc-800 flex flex-col sm:flex-row items-center justify-between gap-4">
            <a @click="startAnalysis" class="cursor-pointer w-full sm:w-auto text-center px-6 py-3 rounded bg-white text-zinc-950 font-bold hover:bg-zinc-200 transition-colors">
              [Get free access]
            </a>
            <span class="text-zinc-500 text-[11px]">_Ready in under 30 seconds._</span>
          </div>
        </div>
      </section>

      <!-- SECTION: BEFORE YOU USE / FAQ (ContentArchitecture Style) -->
      <section class="pt-12 border-t border-zinc-800 space-y-8">
        <div class="space-y-2">
          <p class="text-xs sm:text-sm font-mono italic text-zinc-400">
            _Before you start_
          </p>
          <h3 class="text-xl sm:text-2xl font-bold tracking-tight text-white">
            Frequently asked questions.
          </h3>
        </div>

        <div class="space-y-6 text-sm text-zinc-300">
          <div class="space-y-1">
            <h4 class="font-bold text-white">What stack is this built on?</h4>
            <p class="text-zinc-400 text-xs sm:text-sm leading-relaxed">
              Vue 3, TypeScript, Pinia, Tailwind CSS, Lenis, and FastAPI backed by PostgreSQL, Redis, and Google Gemini LLM (`google-genai`). Deployed on Railway via Docker.
            </p>
          </div>

          <div class="space-y-1">
            <h4 class="font-bold text-white">How is this different from generic resume builders?</h4>
            <p class="text-zinc-400 text-xs sm:text-sm leading-relaxed">
              Most tools give you a pile of visual templates. This gives you architectural decisions: exact semantic matching, gap analysis, and tailored interview preparation based on your actual target job description.
            </p>
          </div>

          <div class="space-y-1">
            <h4 class="font-bold text-white">Are my documents private?</h4>
            <p class="text-zinc-400 text-xs sm:text-sm leading-relaxed">
              Yes. Your CV and job descriptions are processed in memory during the analysis session and never sold or shared.
            </p>
          </div>
        </div>
      </section>

      <!-- FOOTER -->
      <footer class="pt-12 border-t border-zinc-800 text-xs font-mono text-zinc-500 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div class="flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
          <span>CV Offer Comparer — ATS Architecture Platform</span>
        </div>
        <div>
          © 2026 Mickael Rebeau & contributors. MIT License.
        </div>
      </footer>

    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Lenis from 'lenis'

const router = useRouter()
const authStore = useAuthStore()

const activeDemoTab = ref<'analysis' | 'interview'>('analysis')
let lenis: Lenis | null = null

const startAnalysis = () => {
  router.push('/free-trial')
}

const navigateTo = (path: string) => {
  router.push(path)
}

const handleLogoClick = () => {
  if (authStore.isAuthenticated) {
    router.push('/dashboard')
  } else {
    router.push('/')
  }
}

onMounted(() => {
  lenis = new Lenis({
    duration: 1.2,
    easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
    smoothWheel: true,
  })

  function raf(time: number) {
    lenis?.raf(time)
    requestAnimationFrame(raf)
  }

  requestAnimationFrame(raf)
})

onUnmounted(() => {
  if (lenis) {
    lenis.destroy()
    lenis = null
  }
})
</script>
