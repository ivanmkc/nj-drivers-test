import type { Config } from 'tailwindcss';

export default {
  content: ['./index.html', './mock.html', './src/**/*.{ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: { DEFAULT: '#1E3A5F', hover: '#2A4A75' },
        accent: { DEFAULT: '#C5A572', light: '#D4B886', dark: '#8B6E3B' },
        success: '#15803D',
        error: '#B91C1C',
        warning: '#B45309',
        surface: {
          light: '#F8FAFC',
          dark: '#0F172A',
          'card-light': '#FFFFFF',
          'card-dark': '#1E293B',
        },
        ink: {
          DEFAULT: '#0F172A',
          muted: '#475569',
          subtle: '#64748B',
          inverse: '#F8FAFC',
        },
        line: {
          light: '#E2E8F0',
          dark: '#334155',
        },
      },
      fontFamily: {
        display: ['"IBM Plex Serif"', 'ui-serif', 'Georgia', 'serif'],
        body: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      spacing: {
        xs: '4px',
        sm: '8px',
        md: '12px',
        lg: '16px',
        xl: '24px',
        '2xl': '32px',
        '3xl': '48px',
      },
      borderRadius: {
        sm: '4px',
        md: '8px',
        lg: '12px',
        pill: '9999px',
      },
      boxShadow: {
        card: '0 1px 2px rgba(15,23,42,0.06), 0 4px 12px rgba(15,23,42,0.04)',
      },
      letterSpacing: {
        eyebrow: '0.12em',
      },
    },
  },
} satisfies Config;
