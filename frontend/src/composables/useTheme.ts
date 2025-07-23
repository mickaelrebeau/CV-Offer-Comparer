import { ref, watch } from 'vue'

export function useTheme() {
  const isDark = ref(false)

  // Initialiser le thème depuis localStorage
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme) {
    isDark.value = savedTheme === 'dark'
  } else {
    // Détecter la préférence système
    isDark.value = window.matchMedia('(prefers-color-scheme: dark)').matches
  }

  // Appliquer le thème
  function applyTheme() {
    if (isDark.value) {
      document.documentElement.classList.add('dark')
      localStorage.setItem('theme', 'dark')
    } else {
      document.documentElement.classList.remove('dark')
      localStorage.setItem('theme', 'light')
    }
  }

  // Toggle du thème
  function toggleTheme() {
    isDark.value = !isDark.value
  }

  // Surveiller les changements de thème
  watch(isDark, () => {
    applyTheme()
  })

  // Appliquer le thème initial
  applyTheme()

  return {
    isDark,
    toggleTheme,
  }
} 