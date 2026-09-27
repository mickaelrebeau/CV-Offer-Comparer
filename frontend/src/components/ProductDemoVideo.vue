<template>
  <div class="h-full w-full overflow-hidden bg-ink">
    <video
      :key="basePath"
      ref="videoEl"
      class="h-full w-full object-cover"
      muted
      autoplay
      loop
      playsinline
      preload="auto"
      :poster="posterSrc"
      :aria-label="label"
    >
      <!-- MP4 first: Safari ignores WebM and needs a compatible H.264 baseline. -->
      <source :src="mp4Src" type="video/mp4" />
      <source :src="webmSrc" type="video/webm" />
    </video>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useLocale } from '@/i18n/useLocale'

const props = defineProps<{
  variant: 'analyse' | 'entretien' | 'lettre'
  label: string
  inView?: boolean
}>()

const videoEl = ref<HTMLVideoElement | null>(null)
const prefersReducedMotion = ref(false)

const { locale } = useLocale()

// Une vidéo par langue d'interface : /videos/<démo>.mp4 (fr) et /videos/<démo>-en.mp4
const basePath = computed(() => `/videos/${props.variant}${locale.value === 'en' ? '-en' : ''}`)
const webmSrc = computed(() => `${basePath.value}.webm`)
const mp4Src = computed(() => `${basePath.value}.mp4`)
const posterSrc = computed(() => `${basePath.value}-poster.webp`)

const shouldPlay = computed(
  () => props.inView !== false && !prefersReducedMotion.value,
)

let motionQuery: MediaQueryList | null = null

const play = async () => {
  const video = videoEl.value
  if (!video || !shouldPlay.value) return

  video.muted = true
  video.defaultMuted = true
  video.playsInline = true

  try {
    await video.play()
  } catch {
    // Autoplay can still be blocked; poster remains visible.
  }
}

const pause = () => {
  videoEl.value?.pause()
}

const handleMotionChange = (event: MediaQueryListEvent) => {
  prefersReducedMotion.value = event.matches
  if (shouldPlay.value) play()
  else pause()
}

onMounted(async () => {
  motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
  prefersReducedMotion.value = motionQuery.matches
  motionQuery.addEventListener('change', handleMotionChange)

  await nextTick()
  if (shouldPlay.value) play()
})

onUnmounted(() => {
  pause()
  motionQuery?.removeEventListener('change', handleMotionChange)
})

watch(
  () => props.inView,
  (visible) => {
    if (visible && shouldPlay.value) play()
    else pause()
  },
)
</script>
