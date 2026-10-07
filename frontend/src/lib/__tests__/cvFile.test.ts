import { describe, expect, it } from 'vitest'
import { CV_ACCEPT, cvExtension } from '@/lib/cvFile'

describe('cvExtension', () => {
  it('reconnaît PDF, DOCX et TXT sans tenir compte de la casse', () => {
    expect(cvExtension('CV.PDF')).toBe('pdf')
    expect(cvExtension('mon.cv.docx')).toBe('docx')
    expect(cvExtension('cv.txt')).toBe('txt')
  })

  it('refuse les autres formats', () => {
    expect(cvExtension('cv.doc')).toBeNull()
    expect(cvExtension('cv.odt')).toBeNull()
    expect(cvExtension('cv')).toBeNull()
  })
})

describe('CV_ACCEPT', () => {
  it('inclut les trois extensions', () => {
    expect(CV_ACCEPT.split(',')).toEqual(expect.arrayContaining(['.pdf', '.docx', '.txt']))
  })
})
