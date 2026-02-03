'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

interface Municipality {
    id: number;
    code: string;
    prefecture: string;
    name: string;
    region: string;
    population: number;
    score_total: number;
}

interface Region {
    id: string;
    name: string;
}

const REGIONS: Region[] = [
    { id: 'all', name: '全国' },
    { id: '北海道', name: '北海道' },
    { id: '東北', name: '東北' },
    { id: '関東', name: '関東' },
    { id: '中部', name: '中部' },
    { id: '近畿', name: '近畿' },
    { id: '中国', name: '中国' },
    { id: '四国', name: '四国' },
    { id: '九州', name: '九州' },
];

function getScoreColor(score: number): string {
    if (score >= 80) return 'text-blue-600 bg-blue-50';
    if (score >= 60) return 'text-green-600 bg-green-50';
    if (score >= 40) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
}

export default function HomePage() {
    const [municipalities, setMunicipalities] = useState<Municipality[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedRegion, setSelectedRegion] = useState('all');

    useEffect(() => {
        fetchMunicipalities();
    }, [selectedRegion]);

    const fetchMunicipalities = async () => {
        setLoading(true);
        setError(null);
        try {
            const params = new URLSearchParams();
            if (selectedRegion !== 'all') {
                params.append('region', selectedRegion);
            }
            const res = await fetch(`/api/municipalities?${params}`);
            if (res.ok) {
                const data = await res.json();
                setMunicipalities(data);
            } else {
                throw new Error(`サーバーエラー: ${res.status}`);
            }
        } catch (error) {
            console.error('Failed to fetch municipalities:', error);
            setError('データの取得に失敗しました。しばらくしてから再度お試しください。');
        } finally {
            setLoading(false);
        }
    };

    const filteredMunicipalities = municipalities.filter(m =>
        m.name.includes(searchQuery) || m.prefecture.includes(searchQuery)
    );

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
            {/* ヘッダー */}
            <header className="sticky top-0 z-50 glass border-b border-gray-200">
                <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg">
                            <span className="text-white font-bold text-xl">Z</span>
                        </div>
                        <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent">
                            Local Gov DX Intelligence
                        </h1>
                    </div>

                    <div className="flex items-center gap-4">
                        <Link
                            href="/login"
                            className="px-4 py-2 text-sm text-gray-600 hover:text-blue-600 transition-colors"
                        >
                            ログイン
                        </Link>
                    </div>
                </div>
            </header>

            {/* メインコンテンツ */}
            <main className="max-w-7xl mx-auto px-6 py-8">
                {/* 検索バー */}
                <div className="mb-8">
                    <div className="relative">
                        <input
                            type="text"
                            placeholder="自治体名で検索..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="w-full px-6 py-4 text-lg bg-white rounded-2xl shadow-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-shadow"
                            aria-label="自治体名で検索"
                        />
                        <svg
                            className="absolute right-6 top-1/2 -translate-y-1/2 w-6 h-6 text-gray-400"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                            aria-hidden="true"
                        >
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                        </svg>
                    </div>
                </div>

                {/* フィルター */}
                <div className="flex gap-2 mb-8 overflow-x-auto pb-2" role="group" aria-label="地方フィルター">
                    {REGIONS.map(region => (
                        <button
                            key={region.id}
                            onClick={() => setSelectedRegion(region.id)}
                            className={`px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-all ${selectedRegion === region.id
                                    ? 'bg-blue-500 text-white shadow-md'
                                    : 'bg-white text-gray-600 hover:bg-gray-100'
                                }`}
                            aria-pressed={selectedRegion === region.id}
                            aria-label={`${region.name}で絞り込み`}
                        >
                            {region.name}
                        </button>
                    ))}
                </div>

                {/* グリッドレイアウト */}
                <div className="grid grid-cols-12 gap-6">
                    {/* 左: 自治体一覧 */}
                    <div className="col-span-12 lg:col-span-7 space-y-4">
                        <div className="flex items-center justify-between">
                            <h2 className="text-lg font-semibold text-gray-900">
                                自治体一覧
                                <span className="ml-2 text-sm text-gray-500">
                                    {filteredMunicipalities.length}件
                                </span>
                            </h2>
                        </div>

                        {error && (
                            <div className="p-4 bg-red-50 border border-red-200 rounded-xl">
                                <div className="flex items-center gap-2">
                                    <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                    </svg>
                                    <span className="text-sm text-red-800">{error}</span>
                                </div>
                                <button
                                    onClick={fetchMunicipalities}
                                    className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
                                    aria-label="データ取得を再試行"
                                >
                                    再試行
                                </button>
                            </div>
                        )}

                        {loading ? (
                            <div className="flex items-center justify-center h-64" role="status" aria-live="polite">
                                <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                                <span className="sr-only">読み込み中...</span>
                            </div>
                        ) : !error && (
                            <div className="space-y-3">
                                {filteredMunicipalities.map((m) => (
                                    <div
                                        key={m.id}
                                        className="p-4 bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow cursor-pointer"
                                    >
                                        <div className="flex items-center justify-between">
                                            <div>
                                                <h3 className="font-semibold text-gray-900">{m.name}</h3>
                                                <p className="text-sm text-gray-500">
                                                    {m.prefecture} / {m.region}
                                                </p>
                                                <p className="text-xs text-gray-400 mt-1">
                                                    人口: {m.population.toLocaleString()}人
                                                </p>
                                            </div>
                                            <div className={`px-3 py-1 rounded-full text-sm font-semibold ${getScoreColor(m.score_total)}`}>
                                                {m.score_total.toFixed(1)}
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* 右: 地図プレースホルダー */}
                    <div className="col-span-12 lg:col-span-5">
                        <div className="sticky top-24">
                            <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
                                <div className="p-6 border-b border-gray-100">
                                    <h2 className="text-lg font-semibold text-gray-900">全国スコアマップ</h2>
                                    <p className="text-sm text-gray-500 mt-1">クリックで詳細表示</p>
                                </div>
                                <div className="h-96 bg-gradient-to-br from-blue-100 to-green-100 flex items-center justify-center">
                                    <div className="text-center">
                                        <svg className="w-16 h-16 text-blue-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                                        </svg>
                                        <p className="text-gray-500">Deck.gl 地図コンポーネント</p>
                                        <p className="text-sm text-gray-400">（GeoJSON読み込み後に表示）</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </main>

            {/* フッター */}
            <footer className="border-t border-gray-200 bg-white/50 mt-12">
                <div className="max-w-7xl mx-auto px-6 py-4 text-center text-sm text-gray-500">
                    © 2026 Zoom Video Communications, Inc. | Local Gov DX Intelligence
                </div>
            </footer>
        </div>
    );
}
