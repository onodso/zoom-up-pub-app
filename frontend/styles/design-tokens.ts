/**
 * デザインシステム - Zoom DX Intelligence
 */

export const colors = {
    // Zoomブランドカラー
    primary: {
        50: '#E6F0FF',
        100: '#B3D7FF',
        500: '#2D8CFF',  // Zoom Blue
        700: '#1A5FB4',
        900: '#0D3A6F'
    },
    // 温もりカラー
    warmth: {
        orange: '#FF8A3D',
        coral: '#FF6B9D',
        amber: '#FFC857'
    },
    // ニュートラル
    gray: {
        50: '#F9FAFB',
        100: '#F3F4F6',
        200: '#E5E7EB',
        300: '#D1D5DB',
        500: '#6B7280',
        700: '#374151',
        900: '#111827'
    },
    // スコアカラー（12段階）
    score: [
        '#0D47A1', // 最高（青）
        '#1565C0',
        '#1976D2',
        '#1E88E5',
        '#42A5F5',
        '#66BB6A', // 中間（緑）
        '#9CCC65',
        '#FFEB3B', // やや低（黄）
        '#FFC107',
        '#FF9800',
        '#FF5722',
        '#D32F2F'  // 最低（赤）
    ]
};

export const typography = {
    fontFamily: {
        sans: ['Inter', 'Noto Sans JP', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace']
    },
    fontSize: {
        xs: '0.75rem',    // 12px
        sm: '0.875rem',   // 14px
        base: '1rem',     // 16px
        lg: '1.125rem',   // 18px
        xl: '1.25rem',    // 20px
        '2xl': '1.5rem',  // 24px
        '3xl': '1.875rem',// 30px
        '4xl': '2.25rem'  // 36px
    }
};

export const spacing = {
    xs: '0.5rem',   // 8px
    sm: '0.75rem',  // 12px
    md: '1rem',     // 16px
    lg: '1.5rem',   // 24px
    xl: '2rem',     // 32px
    '2xl': '3rem'   // 48px
};

export const borderRadius = {
    sm: '0.375rem',  // 6px
    md: '0.5rem',    // 8px
    lg: '0.75rem',   // 12px
    xl: '1rem',      // 16px
    full: '9999px'
};

export const shadows = {
    sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    md: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
    lg: '0 10px 15px -3px rgb(0 0 0 / 0.1)',
    xl: '0 20px 25px -5px rgb(0 0 0 / 0.1)',
    glass: '0 8px 32px 0 rgba(31, 38, 135, 0.15)'
};

/**
 * スコアを12段階カラーに変換
 */
export function getScoreColor(score: number): string {
    const index = Math.min(Math.floor((100 - score) / 8.34), 11);
    return colors.score[index];
}

/**
 * スコアをRGBA配列に変換（Deck.gl用）
 */
export function getScoreColorRGBA(score: number): [number, number, number, number] {
    const hex = getScoreColor(score);
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return [r, g, b, 200];
}
