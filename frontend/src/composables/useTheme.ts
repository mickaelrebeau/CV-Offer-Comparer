import { ref, watch } from 'vue'

export function useTheme() {
  const isDark = ref(false)

  const savedTheme = localStorage.getItem('theme')
  if (savedTheme) {
    isDark.value = savedTheme === 'dark'
  } else {
    isDark.value = false // thème par défaut = light
  }

  function applyTheme() {
    if (isDark.value) {
      document.documentElement.classList.add('dark')
      localStorage.setItem('theme', 'dark')
    } else {
      document.documentElement.classList.remove('dark')
      localStorage.setItem('theme', 'light')
    }
  }

  function toggleTheme() {
    isDark.value = !isDark.value
  }

  watch(isDark, () => {
    applyTheme()
  })

  applyTheme()

  return {
    isDark,
    toggleTheme,
  }
} 
