'use client';

import { useState, useEffect, useCallback } from 'react';
import { getScoreColorRGBA } from '@/styles/design-tokens';

interface PrefectureScore {
    prefecture_code: string;
    prefecture_name: string;
    avg_score: number;
    municipality_count: number;
}

interface JapanMapProps {
    onPrefectureClick?: (prefectureCode: string) => void;
}

const INITIAL_VIEW_STATE = {
    longitude: 138.0,
    latitude: 37.5,
    zoom: 5,
};

// 都道府県データ（仮 - GeoJSON読み込み後に置換）
const PREFECTURE_DATA = [
    { code: '13', name: '東京都', lat: 35.6762, lng: 139.6503, score: 82.5 },
    { code: '14', name: '神奈川県', lat: 35.4478, lng: 139.6425, score: 78.3 },
    { code: '23', name: '愛知県', lat: 35.1802, lng: 136.9066, score: 75.2 },
    { code: '27', name: '大阪府', lat: 34.6937, lng: 135.5023, score: 76.8 },
    { code: '01', name: '北海道', lat: 43.0642, lng: 141.3469, score: 65.4 },
    { code: '40', name: '福岡県', lat: 33.6064, lng: 130.4183, score: 72.1 },
];

export default function JapanMap({ onPrefectureClick }: JapanMapProps) {
    const [scores, setScores] = useState<Record<string, PrefectureScore>>({});
    const [hoveredPrefecture, setHoveredPrefecture] = useState<string | null>(null);

    useEffect(() => {
        // スコアデータ取得
        fetch('/api/scores/by-prefecture')
            .then(res => res.ok ? res.json() : {})
            .then(data => setScores(data))
            .catch(console.error);
    }, []);

    const handleClick = useCallback((prefCode: string) => {
        if (onPrefectureClick) {
            onPrefectureClick(prefCode);
        }
    }, [onPrefectureClick]);

    return (
        <div className="relative w-full h-[600px] bg-gradient-to-br from-blue-50 to-green-50">
            {/* 簡易マップ（Deck.gl完全版は後で追加） */}
            <div className="absolute inset-0 flex items-center justify-center">
                <div className="relative w-[300px] h-[400px]">
                    {PREFECTURE_DATA.map((pref) => {
                        const score = scores[pref.code]?.avg_score || pref.score;
                        const [r, g, b] = getScoreColorRGBA(score);
                        const isHovered = hoveredPrefecture === pref.code;

                        // 簡易的な位置計算
                        const x = ((pref.lng - 128) / 18) * 280;
                        const y = ((45 - pref.lat) / 15) * 380;

                        return (
                            <button
                                key={pref.code}
                                onClick={() => handleClick(pref.code)}
                                onMouseEnter={() => setHoveredPrefecture(pref.code)}
                                onMouseLeave={() => setHoveredPrefecture(null)}
                                className={`absolute w-12 h-12 rounded-full flex items-center justify-center text-white text-xs font-bold transition-all ${isHovered ? 'scale-125 z-10 shadow-lg' : ''
                                    }`}
                                style={{
                                    left: `${x}px`,
                                    top: `${y}px`,
                                    backgroundColor: `rgb(${r}, ${g}, ${b})`,
                                }}
                            >
                                {score.toFixed(0)}
                            </button>
                        );
                    })}
                </div>
            </div>

            {/* 凡例 */}
            <div className="absolute bottom-4 left-4 bg-white/90 rounded-lg p-3 shadow-md">
                <p className="text-xs font-semibold text-gray-700 mb-2">スコア凡例</p>
                <div className="flex gap-1">
                    {[100, 80, 60, 40, 20].map((score) => {
                        const [r, g, b] = getScoreColorRGBA(score);
                        return (
                            <div
                                key={score}
                                className="w-6 h-4 rounded-sm"
                                style={{ backgroundColor: `rgb(${r}, ${g}, ${b})` }}
                                title={`${score}点`}
                            />
                        );
                    })}
                </div>
                <div className="flex justify-between text-[10px] text-gray-500 mt-1">
                    <span>高</span>
                    <span>低</span>
                </div>
            </div>

            {/* ホバーツールチップ */}
            {hoveredPrefecture && (
                <div className="absolute top-4 right-4 bg-white rounded-lg p-3 shadow-lg">
                    <p className="font-semibold text-gray-900">
                        {PREFECTURE_DATA.find(p => p.code === hoveredPrefecture)?.name}
                    </p>
                    <p className="text-sm text-gray-500">
                        平均スコア: {scores[hoveredPrefecture]?.avg_score.toFixed(1) || '-'}
                    </p>
                    <p className="text-xs text-gray-400">
                        自治体数: {scores[hoveredPrefecture]?.municipality_count || '-'}
                    </p>
                </div>
            )}

            {/* Deck.gl読み込み中メッセージ */}
            <div className="absolute top-4 left-4 bg-blue-100 text-blue-700 text-xs px-3 py-1 rounded-full">
                簡易マップ表示中（GeoJSON読み込み後に完全版へ）
            </div>
        </div>
    );
}
