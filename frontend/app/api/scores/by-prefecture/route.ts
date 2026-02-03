import { NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function GET() {
    try {
        const res = await fetch(`${API_URL}/api/scores/by-prefecture`, {
            headers: { 'Content-Type': 'application/json' },
            cache: 'no-store',
        });

        if (!res.ok) {
            throw new Error(`API error: ${res.status}`);
        }

        const data = await res.json();
        return NextResponse.json(data);
    } catch (error) {
        console.error('Scores API error:', error);

        // フォールバック: モックデータ
        return NextResponse.json({
            '13': { prefecture_code: '13', prefecture_name: '東京都', avg_score: 82.5, municipality_count: 62 },
            '14': { prefecture_code: '14', prefecture_name: '神奈川県', avg_score: 78.3, municipality_count: 33 },
            '23': { prefecture_code: '23', prefecture_name: '愛知県', avg_score: 75.2, municipality_count: 54 },
            '27': { prefecture_code: '27', prefecture_name: '大阪府', avg_score: 76.8, municipality_count: 43 },
            '01': { prefecture_code: '01', prefecture_name: '北海道', avg_score: 65.4, municipality_count: 179 },
            '40': { prefecture_code: '40', prefecture_name: '福岡県', avg_score: 72.1, municipality_count: 60 },
        });
    }
}
