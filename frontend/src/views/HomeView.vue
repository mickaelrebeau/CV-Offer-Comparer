<template>
  <div ref="rootEl" class="bg-paper text-ink font-sans antialiased selection:bg-ink selection:text-paper">

    <!-- ────────────────────────── NAVIGATION (fixe, centrée) ────────────────────────── -->
    <header class="pointer-events-none fixed inset-x-0 top-0 z-50 flex justify-between items-start p-5 lg:justify-center lg:p-8">
      <RouterLink
        :to="homePath"
        class="pointer-events-auto lg:absolute lg:left-8"
        :aria-label="t('nav.homeAria')"
      >
        <BrandLogo tag="span" size="sm" />
      </RouterLink>
      <nav
        :aria-label="t('landing.nav.sections')"
        class="pointer-events-auto hidden lg:flex items-center gap-7 rounded-full border border-ink/12 bg-paper/95 px-6 py-2.5 font-mono text-caption uppercase backdrop-blur-md"
      >
        <a href="#probleme" class="text-ink-soft transition-colors hover:text-ink">{{ t('landing.nav.problem') }}</a>
        <a href="#methode" class="text-ink-soft transition-colors hover:text-ink">{{ t('landing.nav.method') }}</a>
        <a href="#apercu" class="text-ink-soft transition-colors hover:text-ink">{{ t('landing.nav.preview') }}</a>
        <a href="#stats" class="text-ink-soft transition-colors hover:text-ink">{{ t('landing.nav.steps') }}</a>
        <a href="#acces" class="text-ink-soft transition-colors hover:text-ink">{{ t('landing.nav.access') }}</a>
        <a href="#faq" class="text-ink-soft transition-colors hover:text-ink">{{ t('landing.nav.faq') }}</a>
      </nav>

      <div
        class="pointer-events-auto flex items-center gap-1 rounded-full border border-ink/12 bg-paper/95 p-1 pl-1.5 backdrop-blur-md lg:absolute lg:right-8"
      >
        <LanguageSwitcher class="px-2" />
        <RouterLink
          v-if="!authStore.isAuthenticated"
          :to="localePath('/login')"
          class="hidden px-4 py-1.5 font-mono text-caption uppercase text-ink-soft transition-colors hover:text-ink sm:block"
        >
          {{ t('landing.nav.login') }}
        </RouterLink>
        <RouterLink
          :to="primaryPath"
          class="rounded-full bg-ink px-5 py-2 font-mono text-caption uppercase text-paper transition-opacity hover:opacity-85"
        >
          {{ authStore.isAuthenticated ? t('landing.nav.dashboard') : t('landing.nav.analyze') }}
        </RouterLink>
      </div>
    </header>

    <div>

      <!-- ────────────────────────── 01 · HERO ────────────────────────── -->
      <section class="grid min-h-svh grid-cols-1 lg:grid-cols-12" :aria-label="t('landing.hero.aria')">
        <div class="flex flex-col justify-center px-5 pt-32 pb-16 sm:px-8 lg:col-span-6 lg:px-16 lg:py-24 xl:pl-20">
          <p data-reveal="hero" class="mb-3 font-mono text-caption uppercase tracking-[0.14em] text-ink">
            Talento
          </p>
          <p data-reveal="hero" class="mb-5 font-mono text-caption uppercase text-ink-soft">
            {{ t('landing.hero.kicker') }}
          </p>

          <h1 data-reveal="hero" class="mb-8 max-w-[16ch] text-balance font-medium text-display">
            {{ t('landing.hero.title') }}
          </h1>

          <p data-reveal="hero" class="mb-6 max-w-[52ch] text-lead text-ink-soft">
            {{ t('landing.hero.lead') }}
          </p>

          <p data-reveal="hero" class="mb-10 font-mono text-caption uppercase text-ink-soft">
            {{ t('landing.hero.audience') }}
          </p>

          <div data-reveal="hero" class="flex flex-col gap-3 sm:flex-row sm:items-center">
            <RouterLink
              :to="primaryPath"
              class="inline-flex h-12 items-center justify-center rounded-lg bg-ink px-6 font-mono text-caption uppercase text-paper transition-opacity hover:opacity-85"
            >
              {{ t('landing.hero.ctaPrimary') }}
            </RouterLink>
            <a
              href="#methode"
              class="inline-flex h-12 items-center justify-center rounded-lg border border-ink/20 px-6 font-mono text-caption uppercase text-ink transition-colors hover:border-ink/50"
            >
              {{ t('landing.hero.ctaSecondary') }}
            </a>
          </div>

          <div data-reveal="hero" class="mt-12 flex flex-wrap gap-x-6 gap-y-2 border-t border-paper-line pt-6 font-mono text-micro uppercase text-ink-soft">
            <span v-for="badge in list('landing.hero.badges')" :key="badge">{{ badge }}</span>
          </div>
        </div>

        <!-- Panneau terminal -->
        <div data-reveal="hero-panel" class="relative min-h-[70svh] bg-ink p-5 pt-24 sm:p-8 sm:pt-28 lg:col-span-6 lg:min-h-svh lg:p-12 lg:pt-28">
          <div class="flex h-full flex-col overflow-hidden rounded-xl bg-ink-deep font-mono text-caption text-paper/90 ring-1 ring-white/10">
            <div class="flex h-9 shrink-0 items-center justify-between border-b border-white/10 px-4 text-micro uppercase text-paper/60">
              <span>{{ t('landing.terminal.title') }}</span>
              <span class="flex items-center gap-1.5">
                <span class="h-1.5 w-1.5 rounded-full bg-emerald-400" aria-hidden="true"></span>
                {{ t('landing.terminal.streaming') }}
              </span>
            </div>

            <div class="relative flex flex-1 flex-col overflow-hidden p-4 sm:p-6">
              <div class="pointer-events-none absolute inset-x-0 top-0 h-px animate-scan bg-gradient-to-r from-transparent via-emerald-400/50 to-transparent"></div>

              <div class="space-y-1.5 text-paper/60">
                <p><span class="text-paper/30" aria-hidden="true">$</span> {{ t('landing.terminal.readOffer') }} <span class="text-emerald-400">{{ t('landing.terminal.ok') }}</span></p>
                <p><span class="text-paper/30" aria-hidden="true">$</span> {{ t('landing.terminal.readCv') }} <span class="text-emerald-400">{{ t('landing.terminal.ok') }}</span></p>
                <p><span class="text-paper/30" aria-hidden="true">$</span> {{ t('landing.terminal.extract') }} <span class="text-emerald-400">{{ t('landing.terminal.found') }}</span></p>
              </div>

              <div class="my-5 flex items-end justify-between border-y border-white/10 py-5">
                <div>
                  <div class="mb-1 text-micro uppercase text-paper/60">{{ t('landing.terminal.score') }}</div>
                  <div class="text-5xl font-medium tabular-nums text-paper">{{ animatedScore }}%</div>
                </div>
                <div class="text-right text-micro uppercase text-paper/60">
                  <div>{{ t('landing.terminal.criteria') }}</div>
                  <div>{{ t('landing.terminal.covered') }}</div>
                  <div>{{ t('landing.terminal.missing') }}</div>
                </div>
              </div>

              <div class="space-y-1">
                <div
                  v-for="row in streamRows.slice(0, visibleRows)"
                  :key="row.label"
                  class="flex items-baseline justify-between gap-4 border-b border-white/5 py-1.5"
                >
                  <span class="flex items-baseline gap-4">
                    <span class="tabular-nums text-paper/60">{{ row.id }}</span>
                    <span class="text-paper/80">{{ row.label }}</span>
                  </span>
                  <span :class="row.tone">{{ row.status }}</span>
                </div>
              </div>

              <div class="mt-7 space-y-2.5">
                <div class="text-micro uppercase text-paper/60">{{ t('landing.terminal.coverage') }}</div>
                <div v-for="cat in categories" :key="cat.label" class="flex items-center gap-4">
                  <span class="w-28 shrink-0 text-paper/55">{{ cat.label }}</span>
                  <span class="h-px flex-1 bg-white/10">
                    <span class="block h-px bg-paper/60" :style="{ width: cat.value + '%' }"></span>
                  </span>
                  <span class="w-10 shrink-0 text-right tabular-nums text-paper/60">{{ cat.value }}%</span>
                </div>
              </div>

              <p class="mt-auto pt-6 text-paper/60">
                <span class="text-paper/20" aria-hidden="true">$</span> {{ t('landing.terminal.rewrites') }}
                <span class="animate-caret" aria-hidden="true">▍</span>
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
                <div class="flex h-9 items-center border-b border-white/10 px-4 text-micro uppercase text-paper/60">
                  {{ t('landing.problem.log') }}
                </div>
                <div class="overflow-x-auto p-4 sm:p-6">
                  <div class="min-w-max space-y-1.5">
                    <div
                      v-for="item in timeSinks"
                      :key="item.id"
                      class="flex items-baseline justify-between gap-8"
                    >
                      <span class="flex items-baseline gap-5">
                        <span class="tabular-nums text-paper/60">{{ item.id }}</span>
                        <span class="text-paper/85">{{ item.label }}</span>
                      </span>
                      <span class="tabular-nums text-paper/60">{{ item.cost }}</span>
                    </div>
                  </div>
                </div>
                <div class="border-t border-white/10 px-4 py-3 text-micro uppercase text-paper/60 sm:px-6">
                  {{ t('landing.problem.total') }}
                </div>
              </div>
            </div>
          </div>

          <div data-reveal-item class="order-1 lg:order-2 lg:col-span-5 lg:col-start-8 lg:pt-4">
            <p class="mb-5 font-mono text-caption uppercase text-ink-soft">{{ t('landing.problem.kicker') }}</p>
            <h2 class="mb-7 max-w-[18ch] text-balance font-medium text-headline">
              {{ t('landing.problem.title') }}
            </h2>
            <div class="space-y-4 text-lead text-ink-soft">
              <p>{{ t('landing.problem.p1') }}</p>
              <p>{{ t('landing.problem.p2') }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- ────────────────────────── 03 · MÉTHODE (bande encre) ────────────────────────── -->
      <section id="methode" data-reveal="section" data-animate-rows class="bg-ink py-20 text-paper lg:py-40">
        <div class="mx-auto max-w-[100rem] px-5 sm:px-8 lg:px-16">
          <div class="grid grid-cols-1 gap-12 lg:grid-cols-12 lg:gap-8">
            <div data-reveal-item class="lg:col-span-5">
              <p class="mb-5 font-mono text-caption uppercase text-paper/60">{{ t('landing.method.kicker') }}</p>
              <h2 class="max-w-[16ch] text-balance font-medium text-headline">
                {{ t('landing.method.title') }}
              </h2>
            </div>
            <div data-reveal-item class="lg:col-span-6 lg:col-start-7 lg:pt-2">
              <p class="text-lead text-paper/60">{{ t('landing.method.lead') }}</p>
            </div>
          </div>

          <div class="mt-16 border-t border-white/10 lg:mt-24">
            <div
              v-for="decision in decisions"
              :key="decision.id"
              data-reveal-row
              class="grid grid-cols-1 gap-3 border-b border-white/10 py-7 lg:grid-cols-12 lg:gap-8"
            >
              <div class="font-mono text-caption uppercase text-paper/60 lg:col-span-2">
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
              <p class="mb-5 font-mono text-caption uppercase text-ink-soft">{{ t('landing.preview.kicker') }}</p>
              <h2 class="max-w-[14ch] text-balance font-medium text-headline">
                {{ t('landing.preview.title') }}
              </h2>
            </div>

            <div data-reveal-item role="group" :aria-label="t('landing.preview.tabsLabel')" class="flex gap-1 rounded-lg border border-ink/15 p-1 font-mono text-caption uppercase">
              <button
                v-for="tab in tabs"
                :key="tab.id"
                type="button"
                :aria-pressed="activeTab === tab.id"
                @click="activeTab = tab.id"
                class="flex-1 whitespace-nowrap rounded-md px-2 py-2 text-micro transition-colors sm:flex-none sm:px-4 sm:text-caption"
                :class="activeTab === tab.id ? 'bg-ink text-paper' : 'text-ink-soft hover:text-ink'"
              >
                {{ tab.label }}
              </button>
            </div>
          </div>

          <div data-reveal-item class="rounded-xl bg-ink-deep p-1.5 shadow-[0_40px_80px_-40px_rgba(35,35,35,0.55)]">
            <div class="overflow-hidden rounded-lg bg-ink font-mono text-caption text-paper ring-1 ring-white/10">
              <div class="flex h-10 items-center gap-2 border-b border-white/10 px-4 text-micro uppercase text-paper/60">
                <span class="h-2 w-2 rounded-full bg-white/15" aria-hidden="true"></span>
                <span class="h-2 w-2 rounded-full bg-white/15" aria-hidden="true"></span>
                <span class="h-2 w-2 rounded-full bg-white/15" aria-hidden="true"></span>
                <span class="ml-3">{{ currentTab.window }}</span>
              </div>

              <div ref="demoVideoEl" class="relative aspect-video w-full">
                <ProductDemoVideo
                  :key="currentTab.id"
                  class="absolute inset-0"
                  :variant="currentTab.variant"
                  :in-view="demoVideoInView"
                  :label="currentTab.video"
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ────────────────────────── 05 · CHIFFRES + ÉTAPES (bande encre) ────────────────────────── -->
      <section id="stats" data-reveal="section" class="bg-ink py-20 text-paper lg:py-40" :aria-label="t('landing.stats.aria')">
        <div class="mx-auto max-w-[100rem] px-5 sm:px-8 lg:px-16">
          <div class="grid grid-cols-2 gap-8 border-b border-white/10 pb-16 lg:grid-cols-4">
            <div v-for="stat in stats" :key="stat.label" data-reveal-stat>
              <div class="mb-2 text-4xl font-medium tabular-nums lg:text-5xl">{{ stat.value }}</div>
              <div class="font-mono text-micro uppercase text-paper/60">{{ stat.label }}</div>
            </div>
          </div>

          <div class="mt-16 grid grid-cols-1 gap-10 lg:grid-cols-3 lg:gap-8">
            <div v-for="step in steps" :key="step.id" data-reveal-item>
              <div class="mb-4 font-mono text-caption uppercase text-paper/60">{{ step.id }}</div>
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
              <p class="mb-5 font-mono text-caption uppercase text-ink-soft">{{ t('landing.access.kicker') }}</p>
              <h2 class="mb-6 max-w-[14ch] text-balance font-medium text-headline">
                {{ t('landing.access.title') }}
              </h2>
              <p class="max-w-[46ch] text-lead text-ink-soft">
                {{ t('landing.access.lead') }}
              </p>
            </div>

            <div data-reveal-item class="lg:col-span-6 lg:col-start-7">
              <div class="rounded-xl border border-ink/15 p-6 sm:p-8">
                <div class="mb-6 flex items-baseline justify-between border-b border-paper-line pb-5">
                  <span class="font-mono text-caption uppercase">{{ t('landing.access.plan') }}</span>
                  <span class="text-3xl font-medium">{{ t('landing.access.price') }}</span>
                </div>

                <ul class="mb-8 space-y-2.5 font-mono text-caption uppercase text-ink-soft">
                  <li v-for="perk in list('landing.access.perks')" :key="perk" class="flex gap-3">
                    <span class="text-ink/30" aria-hidden="true">—</span>
                    <span>{{ perk }}</span>
                  </li>
                </ul>

                <div class="flex flex-col gap-3 sm:flex-row sm:items-center">
                  <RouterLink
                    :to="authStore.isAuthenticated ? localePath('/dashboard') : localePath('/register')"
                    class="inline-flex h-12 flex-1 items-center justify-center rounded-lg bg-ink px-6 font-mono text-caption uppercase text-paper transition-opacity hover:opacity-85"
                  >
                    {{ t('landing.access.register') }}
                  </RouterLink>
                  <a
                    href="https://github.com/mickaelrebeau/CV-Offer-Comparer"
                    target="_blank"
                    rel="noopener"
                    class="inline-flex h-12 items-center justify-center rounded-lg border border-ink/20 px-6 font-mono text-caption uppercase transition-colors hover:border-ink/50"
                  >
                    {{ t('landing.access.code') }}
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
            <p class="mb-5 font-mono text-caption uppercase text-paper/60">{{ t('landing.faq.kicker') }}</p>
            <h2 class="max-w-[16ch] text-balance font-medium text-headline">
              {{ t('landing.faq.title') }}
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
              <div class="font-mono text-caption uppercase text-paper/60 lg:col-span-4" itemprop="name">
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
            <RouterLink
              :to="primaryPath"
              class="inline-flex h-12 items-center justify-center rounded-lg bg-paper px-6 font-mono text-caption uppercase text-ink transition-opacity hover:opacity-85"
            >
              {{ t('landing.faq.cta') }}
            </RouterLink>
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
            {{ t('landing.footer.slogan') }}
          </div>

          <div class="flex flex-col gap-4 border-t border-paper-line pt-6 font-mono text-micro uppercase text-ink-soft sm:flex-row sm:items-center sm:justify-between">
            <span>{{ t('landing.footer.license') }}</span>
            <div class="flex flex-wrap gap-x-6 gap-y-2">
              <RouterLink :to="localePath('/mentions-legales')" class="transition-colors hover:text-ink">{{ t('landing.footer.legalNotice') }}</RouterLink>
              <RouterLink :to="localePath('/cgv')" class="transition-colors hover:text-ink">{{ t('landing.footer.terms') }}</RouterLink>
              <RouterLink :to="localePath('/confidentialite')" class="transition-colors hover:text-ink">{{ t('landing.footer.privacy') }}</RouterLink>
              <a href="https://github.com/mickaelrebeau/CV-Offer-Comparer" target="_blank" rel="noopener" class="transition-colors hover:text-ink">{{ t('landing.footer.github') }}</a>
              <a href="mailto:rebeau.mickael@gmail.com" class="transition-colors hover:text-ink">{{ t('landing.footer.contact') }}</a>
              <RouterLink :to="localePath('/login')" class="transition-colors hover:text-ink">{{ t('landing.footer.login') }}</RouterLink>
              <InstallAppButton />
            </div>
          </div>
        </div>
      </footer>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink, useRoute } from 'vue-router'
import BrandLogo from '@/components/BrandLogo.vue'
import InstallAppButton from '@/components/InstallAppButton.vue'
import LanguageSwitcher from '@/components/LanguageSwitcher.vue'
import ProductDemoVideo from '@/components/ProductDemoVideo.vue'
import { useAuthStore } from '@/stores/auth'
import { useLandingScroll } from '@/composables/useLandingScroll'
import { useLocale } from '@/i18n/useLocale'
import {
  buildFaqJsonLd,
  buildOrganizationJsonLd,
  buildSoftwareJsonLd,
  buildWebSiteJsonLd,
  usePageSeo,
} from '@/composables/usePageSeo'

const { t, tm, rt } = useI18n()
const { locale, localePath } = useLocale()
const route = useRoute()
const authStore = useAuthStore()
const rootEl = ref<HTMLElement | null>(null)
const demoVideoEl = ref<HTMLElement | null>(null)
const demoVideoInView = ref(false)
useLandingScroll({ root: rootEl })

/** Liste de chaînes d'un catalogue (tableau JSON). */
const list = (key: string) => (tm(key) as unknown[]).map((message) => rt(message as string))

/** Liste d'objets d'un catalogue : chaque champ texte est résolu. */
function records(key: string): Record<string, string>[] {
  return (tm(key) as Record<string, unknown>[]).map((record) =>
    Object.fromEntries(Object.entries(record).map(([field, message]) => [field, rt(message as string)])),
  )
}

const id = (index: number) => String(index + 1).padStart(3, '0')

const homePath = computed(() => localePath(authStore.isAuthenticated ? '/dashboard' : '/'))
const primaryPath = computed(() => localePath(authStore.isAuthenticated ? '/dashboard' : '/free-trial'))

const activeTab = ref<'analyse' | 'simulateur' | 'lettre'>('analyse')

const tabs = computed(() => [
  { id: 'analyse' as const, variant: 'analyse' as const, label: t('landing.preview.tabAnalysis'), window: t('landing.preview.windowAnalysis'), video: t('landing.preview.videoAnalysis') },
  { id: 'simulateur' as const, variant: 'entretien' as const, label: t('landing.preview.tabInterview'), window: t('landing.preview.windowInterview'), video: t('landing.preview.videoInterview') },
  { id: 'lettre' as const, variant: 'lettre' as const, label: t('landing.preview.tabLetter'), window: t('landing.preview.windowLetter'), video: t('landing.preview.videoLetter') },
])
const currentTab = computed(() => tabs.value.find((tab) => tab.id === activeTab.value) ?? tabs.value[0])

const SINK_COSTS = ['~1 H', '~3 H', '~2 H', '~1 H', '~1 H', '~2 H', '~2 H', '∞ H']
const timeSinks = computed(() =>
  list('landing.problem.sinks').map((label, index) => ({ id: id(index), label, cost: SINK_COSTS[index] })),
)

const decisions = computed(() => records('landing.method.decisions').map((decision, index) => ({ id: id(index), ...decision })))

const stats = computed(() => records('landing.stats.items'))

const steps = computed(() => records('landing.stats.steps').map((step, index) => ({ id: id(index), ...step })))

const faq = computed(() => records('landing.faq.items'))

const CATEGORY_VALUES = [92, 85, 100, 78, 90]
const categories = computed(() =>
  list('landing.terminal.categories').map((label, index) => ({ label, value: CATEGORY_VALUES[index] })),
)

const ROW_STATUS = [
  ['covered', 'text-emerald-400'],
  ['covered', 'text-emerald-400'],
  ['partial', 'text-amber-400'],
  ['missing', 'text-rose-400'],
] as const
const streamRows = computed(() =>
  list('landing.terminal.rows').map((label, index) => ({
    id: id(index),
    label,
    status: t(`landing.terminal.status.${ROW_STATUS[index][0]}`),
    tone: ROW_STATUS[index][1],
  })),
)

const animatedScore = ref(0)
const visibleRows = ref(0)

usePageSeo(
  computed(() => ({
    path: route.path,
    jsonLd: [
      buildWebSiteJsonLd(locale.value, t('seo.default.description')),
      buildSoftwareJsonLd(locale.value, t('seo.default.description')),
      buildFaqJsonLd(faq.value.map(({ question, answer }) => ({ question, answer })), locale.value),
      buildOrganizationJsonLd(),
    ],
  })),
)

let scoreTimer: number | undefined
let rowTimer: number | undefined
let demoVideoObserver: IntersectionObserver | undefined

onMounted(() => {
  scoreTimer = window.setInterval(() => {
    if (animatedScore.value >= 88) {
      window.clearInterval(scoreTimer)
      return
    }
    animatedScore.value += 2
  }, 24)

  rowTimer = window.setInterval(() => {
    if (visibleRows.value >= streamRows.value.length) {
      window.clearInterval(rowTimer)
      return
    }
    visibleRows.value += 1
  }, 420)

  demoVideoObserver = new IntersectionObserver(
    ([entry]) => {
      demoVideoInView.value = entry?.isIntersecting ?? false
    },
    { threshold: 0.35 },
  )

  if (demoVideoEl.value) {
    demoVideoObserver.observe(demoVideoEl.value)
  }
})

onUnmounted(() => {
  window.clearInterval(scoreTimer)
  window.clearInterval(rowTimer)
  demoVideoObserver?.disconnect()
})
</script>
