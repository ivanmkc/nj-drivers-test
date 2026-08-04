import type { Config } from 'tailwindcss';

function v(name: string): string {
  return `rgb(var(--color-${name}) / <alpha-value>)`;
}

export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        background: v('background'),
        surface: v('surface'),
        foreground: v('foreground'),
        muted: v('muted'),
        subtle: v('subtle'),
        primary: {
          DEFAULT: v('primary'),
          surface: v('primary-surface'),
          hover: v('primary-hover'),
        },
        success: {
          DEFAULT: v('success'),
          surface: v('success-surface'),
        },
        error: {
          DEFAULT: v('error'),
          surface: v('error-surface'),
        },
        warning: v('warning'),
        'on-accent': v('on-accent'),
        border: {
          DEFAULT: v('border'),
          subtle: v('border-subtle'),
        },
        'gray-surface': v('gray-surface'),
      },
    },
  },
} satisfies Config;
