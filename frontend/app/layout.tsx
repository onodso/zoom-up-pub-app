import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
    title: 'Local Gov DX Intelligence | Zoom営業支援ダッシュボード',
    description: '全国1,741自治体＋47都道府県教育委員会を対象としたZoom営業支援ダッシュボード',
}

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="ja">
            <body>{children}</body>
        </html>
    )
}
