/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Zoomブランドカラー
        primary: {
          50: '#E6F0FF',
          100: '#B3D7FF',
          500: '#2D8CFF',
          700: '#1A5FB4',
          900: '#0D3A6F'
        },
        // 温もりカラー
        warmth: {
          orange: '#FF8A3D',
          coral: '#FF6B9D',
          amber: '#FFC857'
        }
      },
      fontFamily: {
        sans: ['Inter', 'Noto Sans JP', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace']
      },
      boxShadow: {
        'glass': '0 8px 32px 0 rgba(31, 38, 135, 0.15)'
      },
      backdropBlur: {
        'glass': '10px'
      }
    },
  },
  plugins: [],
}
