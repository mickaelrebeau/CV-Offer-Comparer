import { STORAGE_KEYS, readStorage, removeStorage } from '@/lib/storageKeys'

export function getAccessToken(): string | null {
  return readStorage(STORAGE_KEYS.accessToken)
}

export function setAccessToken(token: string): void {
  localStorage.setItem(STORAGE_KEYS.accessToken, token)
}

export function clearAccessToken(): void {
  removeStorage(STORAGE_KEYS.accessToken)
}
