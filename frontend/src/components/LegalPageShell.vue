<template>
  <div class="page-shell">
    <AppPageHeader :label="label" :title="title" :description="description" />
    <article class="panel prose-legal mx-auto max-w-3xl space-y-8 p-6 sm:p-10">
      <p class="font-mono text-micro uppercase text-ink-soft">Dernière mise à jour · {{ updatedAt }}</p>
      <slot />
    </article>
    <nav class="mx-auto mt-10 flex max-w-3xl flex-wrap gap-4 font-mono text-micro uppercase text-ink-soft">
      <RouterLink to="/mentions-legales" class="hover:text-ink">Mentions légales</RouterLink>
      <RouterLink to="/cgv" class="hover:text-ink">CGV / CGU</RouterLink>
      <RouterLink to="/confidentialite" class="hover:text-ink">Confidentialité</RouterLink>
      <RouterLink to="/" class="hover:text-ink">Accueil</RouterLink>
    </nav>
  </div>
</template>

<script setup lang="ts">
import AppPageHeader from '@/components/AppPageHeader.vue'

defineProps<{
  label: string
  title: string
  description: string
  updatedAt: string
}>()
</script>

<style scoped>
.prose-legal :deep(h2) {
  margin-top: 1.75rem;
  font-size: clamp(1.25rem, 2vw, 1.5rem);
  font-weight: 500;
  letter-spacing: -0.015em;
}
.prose-legal :deep(h3) {
  margin-top: 1.25rem;
  font-size: 1rem;
  font-weight: 500;
}
.prose-legal :deep(p),
.prose-legal :deep(li) {
  color: #5e5c57;
  line-height: 1.65;
  font-size: 1.05rem;
}
.prose-legal :deep(ul) {
  list-style: disc;
  padding-left: 1.25rem;
  display: grid;
  gap: 0.4rem;
}
.prose-legal :deep(a) {
  color: #232323;
  text-decoration: underline;
  text-underline-offset: 3px;
}
.prose-legal :deep(strong) {
  color: #232323;
  font-weight: 500;
}
</style>
