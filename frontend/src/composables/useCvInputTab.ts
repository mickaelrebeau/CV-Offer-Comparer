import { ref, watch } from 'vue'
import { useApplicationContextStore } from '@/stores/applicationContext'

export type CvInputTab = 'upload' | 'manual'

/**
 * Onglet PDF / texte du CV. Un CV du contexte partagé sans fichier d'origine
 * (saisi à la main, repris de l'historique) s'affiche en texte pour rester modifiable.
 */
export function useCvInputTab() {
  const context = useApplicationContextStore()
  const textOnly = () => context.hasCv && !context.cvFileName
  const tab = ref<CvInputTab>(textOnly() ? 'manual' : 'upload')

  watch(textOnly, (value) => {
    if (value) tab.value = 'manual'
  })

  return tab
}
