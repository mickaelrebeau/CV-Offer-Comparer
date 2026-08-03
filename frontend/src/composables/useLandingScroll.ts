import { onMounted, onUnmounted, type Ref } from 'vue'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import Lenis from 'lenis'

gsap.registerPlugin(ScrollTrigger)

type Options = {
  root: Ref<HTMLElement | null>
}

export function useLandingScroll({ root }: Options) {
  let lenis: Lenis | null = null
  let mm: gsap.MatchMedia | null = null
  let tickerFn: ((time: number) => void) | null = null

  onMounted(() => {
    const container = root.value
    if (!container) return

    lenis = new Lenis({
      duration: 1.1,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      smoothWheel: true,
    })

    lenis.on('scroll', ScrollTrigger.update)

    tickerFn = (time: number) => {
      lenis?.raf(time * 1000)
    }
    gsap.ticker.add(tickerFn)
    gsap.ticker.lagSmoothing(0)

    mm = gsap.matchMedia()
    mm.add(
      {
        isDesktop: '(min-width: 1024px)',
        reduceMotion: '(prefers-reduced-motion: reduce)',
      },
      (context) => {
        const { reduceMotion } = context.conditions as {
          reduceMotion: boolean
        }

        if (reduceMotion) {
          gsap.set(container.querySelectorAll('[data-reveal]'), {
            clearProps: 'all',
          })
          return
        }

        const heroCopy = container.querySelectorAll('[data-reveal="hero"]')
        if (heroCopy.length) {
          gsap.from(heroCopy, {
            autoAlpha: 0,
            y: 36,
            duration: 0.9,
            ease: 'power3.out',
            stagger: 0.08,
          })
        }

        const heroPanel = container.querySelector('[data-reveal="hero-panel"]')
        if (heroPanel) {
          gsap.from(heroPanel, {
            autoAlpha: 0,
            x: 40,
            duration: 1.1,
            ease: 'power3.out',
            delay: 0.15,
          })
        }

        container.querySelectorAll<HTMLElement>('[data-reveal="section"]').forEach((section) => {
          const targets = section.querySelectorAll('[data-reveal-item]')
          if (!targets.length) return

          gsap.from(targets, {
            autoAlpha: 0,
            y: 40,
            duration: 0.8,
            ease: 'power2.out',
            stagger: 0.08,
            scrollTrigger: {
              trigger: section,
              start: 'top 78%',
              toggleActions: 'play none none none',
            },
          })
        })

        container.querySelectorAll<HTMLElement>('[data-animate-rows]').forEach((section) => {
          const rows = section.querySelectorAll('[data-reveal-row]')
          if (!rows.length) return

          gsap.from(rows, {
            autoAlpha: 0,
            y: 24,
            duration: 0.65,
            ease: 'power2.out',
            stagger: 0.06,
            scrollTrigger: {
              trigger: section,
              start: 'top 75%',
              toggleActions: 'play none none none',
            },
          })
        })

        const stats = container.querySelectorAll('[data-reveal-stat]')
        if (stats.length) {
          gsap.from(stats, {
            autoAlpha: 0,
            y: 28,
            duration: 0.7,
            ease: 'power2.out',
            stagger: 0.1,
            scrollTrigger: {
              trigger: stats[0].parentElement,
              start: 'top 80%',
              toggleActions: 'play none none none',
            },
          })
        }
      },
    )

    ScrollTrigger.refresh()
  })

  onUnmounted(() => {
    mm?.revert()
    mm = null
    if (tickerFn) {
      gsap.ticker.remove(tickerFn)
      tickerFn = null
    }
    lenis?.destroy()
    lenis = null
    ScrollTrigger.getAll().forEach((t) => t.kill())
  })
}
