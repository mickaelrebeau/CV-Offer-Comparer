/** Design tokens aligned with frontend/tailwind.config.js */
export const colors = {
  paper: '#F1EEE7',
  paperDim: '#E6E2D8',
  paperLine: '#D5D0C4',
  ink: '#232323',
  inkDeep: '#141414',
  inkSoft: '#5E5C57',
  emerald400: '#34d399',
  emerald500: '#10b981',
  emerald600: '#059669',
  rose400: '#fb7185',
  rose500: '#f43f5e',
  amber400: '#fbbf24',
  amber500: '#f59e0b',
  amber600: '#d97706',
} as const;

export const fonts = {
  sans: '"Inter", "Geist", system-ui, sans-serif',
  mono: 'ui-monospace, "Geist Mono", "SF Mono", Menlo, monospace',
} as const;

export const FPS = 30;
export const WIDTH = 1920;
export const HEIGHT = 1080;
export const ANALYSIS_DURATION = 450; // 15s
export const INTERVIEW_DURATION = 450; // 15s
