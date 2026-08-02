import { ref } from 'vue'

/** Thème unique papier/encre — aligné sur la landing. */
export function useTheme() {
  const isDark = ref(false)

  function applyTheme() {
    document.documentElement.classList.remove('dark')
    localStorage.setItem('theme', 'light')
  }

  applyTheme()

  return {
    isDark,
    toggleTheme: () => {},
  }
}
