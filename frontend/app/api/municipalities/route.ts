import { NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function GET(request: Request) {
    const { searchParams } = new URL(request.url);
    const region = searchParams.get('region');
    const prefecture = searchParams.get('prefecture');
    const search = searchParams.get('search');

    try {
        const params = new URLSearchParams();
        if (region) params.append('region', region);
        if (prefecture) params.append('prefecture', prefecture);
        if (search) params.append('search', search);

        const res = await fetch(`${API_URL}/api/municipalities?${params}`, {
            headers: { 'Content-Type': 'application/json' },
            // 開発環境: 60秒キャッシュ、本番環境: 300秒キャッシュを推奨
            next: { revalidate: 60 },
        });

        if (!res.ok) {
            throw new Error(`API error: ${res.status}`);
        }

        const data = await res.json();
        return NextResponse.json(data);
    } catch (error) {
        console.error('Municipalities API error:', error);

        // フォールバック: モックデータ
        return NextResponse.json([
            { id: 1, code: '131130', prefecture: '東京都', name: '渋谷区', region: '関東', population: 229000, score_total: 85.5 },
            { id: 2, code: '131181', prefecture: '東京都', name: '世田谷区', region: '関東', population: 917000, score_total: 78.2 },
            { id: 3, code: '141003', prefecture: '神奈川県', name: '横浜市', region: '関東', population: 3749000, score_total: 82.0 },
            { id: 4, code: '231002', prefecture: '愛知県', name: '名古屋市', region: '中部', population: 2320000, score_total: 75.8 },
            { id: 5, code: '271004', prefecture: '大阪府', name: '大阪市', region: '近畿', population: 2750000, score_total: 80.3 },
        ]);
    }
}
