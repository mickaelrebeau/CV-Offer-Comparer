import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { supabase } from '@/lib/supabase'
import type { User } from '@supabase/supabase-js'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const loading = ref(true) // Commencer avec loading = true

  const isAuthenticated = computed(() => !!user.value)

  // Initialiser l'état d'authentification au démarrage
  async function initializeAuth() {
    loading.value = true
    try {
      const { data: { user: currentUser } } = await supabase.auth.getUser()
      user.value = currentUser
    } catch (error) {
      console.error('Erreur lors de l\'initialisation de l\'authentification:', error)
    } finally {
      loading.value = false
    }
  }

  async function signUp(email: string, password: string) {
    loading.value = true
    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
      })
      if (error) throw error
      return { data, error: null }
    } catch (error) {
      return { data: null, error }
    } finally {
      loading.value = false
    }
  }

  async function signIn(email: string, password: string) {
    loading.value = true
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      })
      if (error) throw error
      user.value = data.user
      return { data, error: null }
    } catch (error) {
      return { data: null, error }
    } finally {
      loading.value = false
    }
  }

  async function signOut() {
    loading.value = true
    try {
      const { error } = await supabase.auth.signOut()
      if (error) throw error
      user.value = null
      return { error: null }
    } catch (error) {
      return { error }
    } finally {
      loading.value = false
    }
  }

  async function getCurrentUser() {
    const { data: { user: currentUser } } = await supabase.auth.getUser()
    user.value = currentUser
    return currentUser
  }

  async function deleteAccount() {
    loading.value = true;
    try {
      const { error } = await supabase.auth.admin.deleteUser(
        user.value?.id || ""
      );
      if (error) throw error;
      user.value = null;
      return { error: null };
    } catch (error) {
      return { error };
    } finally {
      loading.value = false;
    }
  }

  // Écouter les changements d'authentification
  supabase.auth.onAuthStateChange((event, session) => {
    user.value = session?.user ?? null;
  });

  return {
    user,
    loading,
    isAuthenticated,
    signUp,
    signIn,
    signOut,
    deleteAccount,
    getCurrentUser,
    initializeAuth,
  };
}) 