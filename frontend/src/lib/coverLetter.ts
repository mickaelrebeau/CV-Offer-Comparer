import type { CoverLetter, CoverLetterSection } from '@/lib/api'

export type CoverLetterFormat = 'txt' | 'md'

/** Lettre reconstituée à partir des sections reçues dans le flux (ordre de réception). */
export function letterFromSections(sections: CoverLetterSection[]): CoverLetter {
  const letter: CoverLetter = {
    subject: '',
    greeting: '',
    opening: '',
    body: [],
    closing: '',
    signoff: '',
    signature: '',
    language: '',
  }
  for (const { key, text } of sections) {
    if (key === 'body') letter.body.push(text)
    else letter[key] = text
  }
  return letter
}

/** Paragraphes de la lettre dans l'ordre de lecture, objet compris. */
function blocks(letter: CoverLetter, format: CoverLetterFormat): string[] {
  const subject = letter.subject && format === 'md' ? `**${letter.subject}**` : letter.subject
  return [
    subject,
    letter.greeting,
    letter.opening,
    ...letter.body,
    letter.closing,
    letter.signoff,
    letter.signature,
  ].filter((block) => block && block.trim())
}

export function formatCoverLetter(letter: CoverLetter, format: CoverLetterFormat = 'txt'): string {
  return `${blocks(letter, format).join('\n\n')}\n`
}

export function downloadCoverLetter(letter: CoverLetter, format: CoverLetterFormat, basename: string) {
  const type = format === 'md' ? 'text/markdown' : 'text/plain'
  const blob = new Blob([formatCoverLetter(letter, format)], { type: `${type};charset=utf-8` })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${basename}.${format}`
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
}
