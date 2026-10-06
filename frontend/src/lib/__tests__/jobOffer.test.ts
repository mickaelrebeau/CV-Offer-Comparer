import { describe, expect, it } from 'vitest'
import { composeOfferText, offerDomain, safeHttpUrl } from '@/lib/jobOffer'

describe('composeOfferText', () => {
  it('place poste, entreprise et lieu en tête de la description', () => {
    expect(
      composeOfferText({ title: 'Data Analyst', company: 'ACME', location: 'Lyon', text: 'Missions…' }),
    ).toBe('Data Analyst\nACME · Lyon\n\nMissions…')
  })

  it('ignore les champs vides', () => {
    expect(composeOfferText({ title: '', company: 'ACME', location: ' ', text: ' Missions ' })).toBe('ACME\n\nMissions')
    expect(composeOfferText({ title: '', company: '', location: '', text: 'Missions' })).toBe('Missions')
  })
})

describe('offerDomain', () => {
  it('renvoie le domaine sans www (seule donnée envoyée à PostHog)', () => {
    expect(offerDomain('https://www.welcometothejungle.com/fr/companies/x/jobs/y?ref=1')).toBe('welcometothejungle.com')
    expect(offerDomain('https://jobs.lever.co/acme/123')).toBe('jobs.lever.co')
  })

  it('tolère une valeur invalide', () => {
    expect(offerDomain('pas une url')).toBe('')
    expect(offerDomain(null)).toBe('')
  })
})

describe('safeHttpUrl', () => {
  it('accepte uniquement http(s)', () => {
    expect(safeHttpUrl('https://jobs.example.com/a')).toBe('https://jobs.example.com/a')
    expect(safeHttpUrl('javascript:alert(1)')).toBeNull()
    expect(safeHttpUrl('data:text/html,x')).toBeNull()
    expect(safeHttpUrl('')).toBeNull()
  })
})
