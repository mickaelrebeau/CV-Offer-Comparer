/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Geist', 'Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        mono: ['"Geist Mono"', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'monospace'],
      },
      fontSize: {
        display: ['clamp(2.5rem, 6.2vw, 4.75rem)', { lineHeight: '0.98', letterSpacing: '-0.02em' }],
        headline: ['clamp(2rem, 4.6vw, 3.25rem)', { lineHeight: '1.04', letterSpacing: '-0.018em' }],
        title: ['clamp(1.5rem, 2.6vw, 2.125rem)', { lineHeight: '1.1', letterSpacing: '-0.015em' }],
        lead: ['clamp(1rem, 1.2vw, 1.125rem)', { lineHeight: '1.55' }],
        caption: ['0.8125rem', { lineHeight: '1.3', letterSpacing: '0.02em' }],
        micro: ['0.6875rem', { lineHeight: '1.3', letterSpacing: '0.06em' }],
      },
      colors: {
        paper: {
          DEFAULT: '#F1EEE7',
          dim: '#E6E2D8',
          line: '#D5D0C4',
        },
        ink: {
          DEFAULT: '#232323',
          deep: '#141414',
          soft: '#5E5C57',
          line: '#3A3A3A',
        },
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        brand: { 
          50: '#f0f3ff',
          100: '#e0e7ff',
          200: '#c7d2fe',
          300: '#a5b4fc',
          400: '#818cf8',
          500: '#6366f1',
          600: '#4f46e5',
          700: '#4338ca',
          800: '#3730a3',
          900: '#312e81',
        },
        match: {
          DEFAULT: "#10b981",
          light: "#34d399",
          dark: "#059669",
        },
        missing: {
          DEFAULT: "#f43f5e",
          light: "#fb7185",
          dark: "#e11d48",
        },
        unclear: {
          DEFAULT: "#f59e0b",
          light: "#fbbf24",
          dark: "#d97706",
        },
      },
      boxShadow: {
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.08)',
        'glow': '0 0 50px -10px rgba(99, 102, 241, 0.25)',
        'glow-lg': '0 0 80px -15px rgba(99, 102, 241, 0.35)',
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      animation: {
        'pulse-subtle': 'pulseSubtle 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 6s ease-in-out infinite',
        'scan': 'scan 3.2s cubic-bezier(0.4, 0, 0.2, 1) infinite',
        'caret': 'caret 1.1s steps(1) infinite',
      },
      keyframes: {
        pulseSubtle: {
          '0%, 100%': { opacity: 1 },
          '50%': { opacity: 0.7 },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        scan: {
          '0%': { transform: 'translateY(-10%)', opacity: '0' },
          '15%, 85%': { opacity: '1' },
          '100%': { transform: 'translateY(1000%)', opacity: '0' },
        },
        caret: {
          '0%, 50%': { opacity: '1' },
          '51%, 100%': { opacity: '0' },
        },
      },
    },
  },
  plugins: [],
}
