import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "home",
      component: () => import("@/views/HomeView.vue"),
      meta: { requiresAuth: false },
    },
    {
      path: "/compare",
      name: "compare",
      component: () => import("@/views/CompareView.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/free-trial",
      name: "free-trial",
      component: () => import("@/views/FreeTrialView.vue"),
      meta: { requiresAuth: false },
    },
    {
      path: "/profile",
      name: "profile",
      component: () => import("@/views/ProfileView.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/login",
      name: "login",
      component: () => import("@/views/LoginView.vue"),
      meta: { requiresAuth: false },
    },
    {
      path: "/register",
      name: "register",
      component: () => import("@/views/RegisterView.vue"),
      meta: { requiresAuth: false },
    },
  ],
});

// Navigation guard
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();

  // Si l'authentification est en cours de chargement, attendre
  if (authStore.loading) {
    // Attendre que l'initialisation soit terminée
    await new Promise((resolve) => {
      const unwatch = authStore.$subscribe(() => {
        if (!authStore.loading) {
          unwatch();
          resolve(true);
        }
      });
    });
  }

  // Les utilisateurs connectés peuvent rester sur la page d'accueil s'ils le souhaitent
  // La redirection automatique est gérée dans HomeView.vue

  // Rediriger les utilisateurs non connectés vers /login pour les routes protégées
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next("/login");
  } else {
    next();
  }
});

export default router 