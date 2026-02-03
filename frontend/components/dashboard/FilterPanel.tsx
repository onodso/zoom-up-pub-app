'use client';

interface FilterPanelProps {
    filters: {
        region: string[];
        scoreRange: [number, number];
        searchQuery: string;
    };
    onChange: (filters: any) => void;
}

const REGIONS = [
    { id: 'hokkaido', name: '北海道' },
    { id: 'tohoku', name: '東北' },
    { id: 'kanto', name: '関東' },
    { id: 'chubu', name: '中部' },
    { id: 'kinki', name: '近畿' },
    { id: 'chugoku', name: '中国' },
    { id: 'shikoku', name: '四国' },
    { id: 'kyushu', name: '九州' },
];

const SCORE_RANGES = [
    { id: 'all', label: '全て', range: [0, 100] },
    { id: 'high', label: '高スコア (80+)', range: [80, 100] },
    { id: 'mid', label: '中スコア (50-80)', range: [50, 80] },
    { id: 'low', label: '低スコア (0-50)', range: [0, 50] },
];

export default function FilterPanel({ filters, onChange }: FilterPanelProps) {
    const toggleRegion = (regionId: string) => {
        const newRegions = filters.region.includes(regionId)
            ? filters.region.filter((r) => r !== regionId)
            : [...filters.region, regionId];
        onChange({ ...filters, region: newRegions });
    };

    const setScoreRange = (range: [number, number]) => {
        onChange({ ...filters, scoreRange: range });
    };

    const clearFilters = () => {
        onChange({ region: [], scoreRange: [0, 100], searchQuery: '' });
    };

    const hasActiveFilters = filters.region.length > 0 || filters.scoreRange[0] > 0 || filters.scoreRange[1] < 100;

    return (
        <div className="bg-white rounded-2xl shadow-sm p-6">
            <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-gray-900">フィルター</h3>
                {hasActiveFilters && (
                    <button
                        onClick={clearFilters}
                        className="text-sm text-blue-500 hover:text-blue-700 transition-colors"
                    >
                        クリア
                    </button>
                )}
            </div>

            {/* 地方フィルター */}
            <div className="mb-6">
                <p className="text-sm font-medium text-gray-700 mb-3">地方</p>
                <div className="flex flex-wrap gap-2">
                    {REGIONS.map((region) => (
                        <button
                            key={region.id}
                            onClick={() => toggleRegion(region.id)}
                            className={`px-3 py-1.5 rounded-lg text-sm transition-all ${filters.region.includes(region.id)
                                    ? 'bg-blue-500 text-white shadow-md'
                                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                }`}
                        >
                            {region.name}
                        </button>
                    ))}
                </div>
            </div>

            {/* スコアフィルター */}
            <div>
                <p className="text-sm font-medium text-gray-700 mb-3">スコア範囲</p>
                <div className="flex flex-wrap gap-2">
                    {SCORE_RANGES.map((range) => {
                        const isActive =
                            filters.scoreRange[0] === range.range[0] &&
                            filters.scoreRange[1] === range.range[1];
                        return (
                            <button
                                key={range.id}
                                onClick={() => setScoreRange(range.range as [number, number])}
                                className={`px-3 py-1.5 rounded-lg text-sm transition-all ${isActive
                                        ? 'bg-blue-500 text-white shadow-md'
                                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                    }`}
                            >
                                {range.label}
                            </button>
                        );
                    })}
                </div>
            </div>

            {/* アクティブフィルター表示 */}
            {hasActiveFilters && (
                <div className="mt-4 pt-4 border-t border-gray-100">
                    <p className="text-xs text-gray-500">
                        アクティブ:
                        {filters.region.length > 0 && ` ${filters.region.length}地方`}
                        {(filters.scoreRange[0] > 0 || filters.scoreRange[1] < 100) &&
                            ` スコア ${filters.scoreRange[0]}-${filters.scoreRange[1]}`}
                    </p>
                </div>
            )}
        </div>
    );
}
