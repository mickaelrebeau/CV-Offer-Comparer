/** Formats de CV acceptés à l'import ; l'extraction (et le contrôle du contenu) est faite par le backend. */
export const CV_EXTENSIONS = ['pdf', 'docx', 'txt'] as const

export type CvExtension = (typeof CV_EXTENSIONS)[number]

/** Valeur de l'attribut `accept` du champ fichier : extensions et types MIME correspondants. */
export const CV_ACCEPT = [
  '.pdf',
  '.docx',
  '.txt',
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'text/plain',
].join(',')

export const MAX_CV_FILE_SIZE = 10 * 1024 * 1024

/** Extension d'un CV accepté, ou null si le format n'est pas pris en charge. */
export function cvExtension(fileName: string): CvExtension | null {
  const extension = fileName.toLowerCase().split('.').pop()
  return CV_EXTENSIONS.find((accepted) => accepted === extension) ?? null
}
