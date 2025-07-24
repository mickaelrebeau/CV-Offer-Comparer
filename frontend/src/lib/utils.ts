import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatPercentage(value: number): string {
  return `${Math.round(value * 100)}%`
}

export function getStatusColor(status: 'match' | 'missing' | 'unclear'): string {
  switch (status) {
    case 'match':
      return 'bg-match text-white'
    case 'missing':
      return 'bg-missing text-white'
    case 'unclear':
      return 'bg-unclear text-black'
    default:
      return 'bg-gray-500 text-white'
  }
}

export function getStatusIcon(status: 'match' | 'missing' | 'unclear'): string {
  switch (status) {
    case 'match':
      return 'check-circle'
    case 'missing':
      return 'x-circle'
    case 'unclear':
      return 'alert-circle'
    default:
      return 'help-circle'
  }
} 