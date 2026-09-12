/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: '#09090b',
        surface: {
          DEFAULT: '#18181b',
          subtle: '#141417',
          hover: '#27272a',
          active: '#2e2e33'
        },
        border: {
          DEFAULT: '#27272a',
          subtle: 'rgba(255, 255, 255, 0.08)',
          strong: '#3f3f46'
        },
        crimson: {
          50: '#fff1f2',
          100: '#ffe4e6',
          400: '#fb7185',
          500: '#f43f5e',
          600: '#ef233c',
          700: '#dc2626',
          glow: 'rgba(239, 35, 60, 0.45)',
          muted: 'rgba(239, 35, 60, 0.12)'
        },
        text: {
          primary: '#f4f4f5',
          secondary: '#a1a1aa',
          muted: '#71717a',
          dim: '#52525b'
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace']
      },
      keyframes: {
        pulseGlow: {
          '0%, 100%': { opacity: '1', transform: 'scale(1)' },
          '50%': { opacity: '0.6', transform: 'scale(1.08)' },
        },
        slideInRight: {
          from: { transform: 'translateX(100%)', opacity: '0' },
          to: { transform: 'translateX(0)', opacity: '1' }
        },
        fadeIn: {
          from: { opacity: '0', transform: 'translateY(6px)' },
          to: { opacity: '1', transform: 'translateY(0)' }
        }
      },
      animation: {
        'pulse-glow': 'pulseGlow 2.2s infinite ease-in-out',
        'slide-in-right': 'slideInRight 0.25s cubic-bezier(0.16, 1, 0.3, 1)',
        'fade-in': 'fadeIn 0.2s ease-out'
      }
    },
  },
  plugins: [],
};
