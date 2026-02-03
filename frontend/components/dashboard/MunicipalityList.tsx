'use client';

import { useState, useEffect } from 'react';

interface Municipality {
    id: number;
    code: string;
    prefecture: string;
    name: string;
    region: string;
    population: number;
    score_total: number;
}

interface MunicipalityListProps {
    filters: {
        region: string[];
        scoreRange: [number, number];
        searchQuery: string;
    };
}

function getScoreColor(score: number): string {
    if (score >= 80) return 'text-blue-600 bg-blue-50 border-blue-200';
    if (score >= 60) return 'text-green-600 bg-green-50 border-green-200';
    if (score >= 40) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    return 'text-red-600 bg-red-50 border-red-200';
}

function getScoreLabel(score: number): string {
    if (score >= 80) return '優良';
    if (score >= 60) return '良好';
    if (score >= 40) return '普通';
    return '要注意';
}

export default function MunicipalityList({ filters }: MunicipalityListProps) {
    const [municipalities, setMunicipalities] = useState<Municipality[]>([]);
    const [loading, setLoading] = useState(true);
    const [sortBy, setSortBy] = useState<'score' | 'name' | 'population'>('score');

    useEffect(() => {
        fetchMunicipalities();
    }, []);

    const fetchMunicipalities = async () => {
        setLoading(true);
        try {
            const res = await fetch('/api/municipalities');
            if (res.ok) {
                const data = await res.json();
                setMunicipalities(data);
            }
        } catch (error) {
            console.error('Failed to fetch municipalities:', error);
        } finally {
            setLoading(false);
        }
    };

    // フィルタリング
    const filteredMunicipalities = municipalities.filter((m) => {
        // 検索クエリ
        if (filters.searchQuery) {
            const query = filters.searchQuery.toLowerCase();
            if (!m.name.toLowerCase().includes(query) &&
                !m.prefecture.toLowerCase().includes(query)) {
                return false;
            }
        }
        // 地方フィルター
        if (filters.region.length > 0) {
            const regionMap: Record<string, string> = {
                'hokkaido': '北海道',
                'tohoku': '東北',
                'kanto': '関東',
                'chubu': '中部',
                'kinki': '近畿',
                'chugoku': '中国',
                'shikoku': '四国',
                'kyushu': '九州',
            };
            const regionNames = filters.region.map(r => regionMap[r]);
            if (!regionNames.includes(m.region)) {
                return false;
            }
        }
        // スコア範囲
        if (m.score_total < filters.scoreRange[0] || m.score_total > filters.scoreRange[1]) {
            return false;
        }
        return true;
    });

    // ソート
    const sortedMunicipalities = [...filteredMunicipalities].sort((a, b) => {
        switch (sortBy) {
            case 'score':
                return b.score_total - a.score_total;
            case 'population':
                return b.population - a.population;
            case 'name':
                return a.name.localeCompare(b.name);
            default:
                return 0;
        }
    });

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
            </div>
        );
    }

    return (
        <div>
            {/* ヘッダー */}
            <div className="flex items-center justify-between mb-4">
                <div>
                    <h2 className="text-lg font-semibold text-gray-900">自治体一覧</h2>
                    <p className="text-sm text-gray-500">{sortedMunicipalities.length}件</p>
                </div>
                <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value as 'score' | 'name' | 'population')}
                    className="px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                    <option value="score">スコア順</option>
                    <option value="population">人口順</option>
                    <option value="name">名前順</option>
                </select>
            </div>

            {/* リスト */}
            <div className="space-y-3">
                {sortedMunicipalities.length === 0 ? (
                    <div className="text-center py-12 bg-white rounded-xl">
                        <svg className="w-12 h-12 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <p className="text-gray-500">条件に一致する自治体がありません</p>
                    </div>
                ) : (
                    sortedMunicipalities.map((m) => (
                        <div
                            key={m.id}
                            className="p-4 bg-white rounded-xl shadow-sm hover:shadow-md transition-all cursor-pointer border border-gray-100 hover:border-blue-200"
                        >
                            <div className="flex items-center justify-between">
                                <div className="flex-1">
                                    <div className="flex items-center gap-2">
                                        <h3 className="font-semibold text-gray-900">{m.name}</h3>
                                        <span className={`px-2 py-0.5 rounded text-xs font-medium border ${getScoreColor(m.score_total)}`}>
                                            {getScoreLabel(m.score_total)}
                                        </span>
                                    </div>
                                    <p className="text-sm text-gray-500 mt-1">
                                        {m.prefecture} / {m.region}
                                    </p>
                                    <div className="flex gap-4 mt-2 text-xs text-gray-400">
                                        <span>人口: {m.population.toLocaleString()}人</span>
                                        <span>コード: {m.code}</span>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <div className={`text-2xl font-bold ${m.score_total >= 80 ? 'text-blue-600' :
                                            m.score_total >= 60 ? 'text-green-600' :
                                                m.score_total >= 40 ? 'text-yellow-600' : 'text-red-600'
                                        }`}>
                                        {m.score_total.toFixed(1)}
                                    </div>
                                    <p className="text-xs text-gray-400">スコア</p>
                                </div>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}
