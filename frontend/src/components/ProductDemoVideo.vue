<template>
  <div class="h-full w-full overflow-hidden bg-ink">
    <video
      ref="videoEl"
      class="absolute inset-0 h-full w-full object-cover"
      muted
      loop
      playsinline
      preload="none"
      :poster="posterSrc"
      :aria-label="label"
      @canplay="playWhenReady"
    >
      <source :src="webmSrc" type="video/webm" />
      <source :src="mp4Src" type="video/mp4" />
    </video>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'

const props = defineProps<{
  variant: 'analyse' | 'entretien'
  label: string
  active?: boolean
  inView?: boolean
}>()

const videoEl = ref<HTMLVideoElement | null>(null)
const prefersReducedMotion = ref(false)

const basePath = computed(() => `/videos/${props.variant}`)
const webmSrc = computed(() => `${basePath.value}.webm`)
const mp4Src = computed(() => `${basePath.value}.mp4`)
const posterSrc = computed(() => `/videos/${props.variant}-poster.webp`)

const shouldPlay = computed(
  () =>
    props.active !== false
    && props.inView !== false
    && !prefersReducedMotion.value,
)

let motionQuery: MediaQueryList | null = null

const stopPlayback = () => {
  const video = videoEl.value
  if (!video) return
  video.pause()
  if (video.readyState >= HTMLMediaElement.HAVE_METADATA) {
    video.currentTime = 0
  }
}

const playWhenReady = () => {
  const video = videoEl.value
  if (!video || !shouldPlay.value) return

  void video.play().catch(() => {
    // The browser keeps the poster visible if autoplay is unavailable.
  })
}

const restartAndPlay = async () => {
  await nextTick()

  const video = videoEl.value
  if (!video || !shouldPlay.value) {
    stopPlayback()
    return
  }

  video.pause()
  if (video.readyState >= HTMLMediaElement.HAVE_METADATA) {
    video.currentTime = 0
    playWhenReady()
    return
  }

  // `canplay` invokes playWhenReady once the browser has loaded this source.
  video.load()
}

const handleMotionChange = (event: MediaQueryListEvent) => {
  prefersReducedMotion.value = event.matches
  if (shouldPlay.value) restartAndPlay()
  else stopPlayback()
}

onMounted(() => {
  motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
  prefersReducedMotion.value = motionQuery.matches
  motionQuery.addEventListener('change', handleMotionChange)
  if (shouldPlay.value) restartAndPlay()
})

onUnmounted(() => {
  stopPlayback()
  motionQuery?.removeEventListener('change', handleMotionChange)
})

watch(
  () => [props.active, props.inView] as const,
  () => {
    if (shouldPlay.value) {
      restartAndPlay()
    } else {
      stopPlayback()
    }
  },
)
</script>
