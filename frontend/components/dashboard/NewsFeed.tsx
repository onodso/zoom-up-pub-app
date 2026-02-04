import { useState, useEffect } from 'react';

interface NewsItem {
    title: string;
    link: string;
    snippet: string;
    source: string;
    published_at: string;
    score?: number;
    reason?: string;
    buying_signal?: boolean;
}

export default function NewsFeed() {
    const [news, setNews] = useState<NewsItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchNews();
    }, []);

    const fetchNews = async () => {
        try {
            const res = await fetch('/api/collector/news?limit=5');
            if (res.ok) {
                const data = await res.json();
                setNews(data);
            } else {
                throw new Error('News fetch failed');
            }
        } catch (err) {
            console.error(err);
            setError('ニュースの取得に失敗しました');
        } finally {
            setLoading(false);
        }
    };

    const getScoreColor = (score: number) => {
        if (score >= 80) return 'text-red-600 bg-red-50 border-red-200';
        if (score >= 60) return 'text-orange-600 bg-orange-50 border-orange-200';
        return 'text-gray-600 bg-gray-50 border-gray-200';
    };

    return (
        <div className="bg-white rounded-2xl shadow-lg overflow-hidden mt-6">
            <div className="p-6 border-b border-gray-100 flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                    <svg className="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                    </svg>
                    最新DXニュース
                </h2>
                <div className="flex gap-2">
                    <span className="animate-pulse relative flex h-3 w-3">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                    </span>
                    <span className="text-xs text-green-600 font-medium">LIVE</span>
                </div>
            </div>

            <div className="p-4">
                {error && <p className="text-red-500 text-sm text-center">{error}</p>}

                {loading ? (
                    <div className="space-y-4">
                        {[1, 2, 3].map((i) => (
                            <div key={i} className="animate-pulse flex space-x-4">
                                <div className="flex-1 space-y-2 py-1">
                                    <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                                    <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="space-y-4">
                        {news.map((item, index) => (
                            <a
                                key={index}
                                href={item.link}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="block group"
                            >
                                <div className="flex items-start gap-3 p-3 rounded-xl hover:bg-gray-50 transition-colors border border-transparent hover:border-gray-100">
                                    <div className="flex-shrink-0 mt-1">
                                        {item.score && item.score > 0 ? (
                                            <div className={`flex flex-col items-center justify-center w-10 h-10 rounded-lg border ${getScoreColor(item.score)}`}>
                                                <span className="text-xs font-bold">{item.score}</span>
                                                <span className="text-[8px] uppercase">Score</span>
                                            </div>
                                        ) : (
                                            <div className="w-2 h-2 rounded-full bg-blue-400 mt-2 ml-1"></div>
                                        )}
                                    </div>
                                    <div className="flex-1">
                                        <h3 className="text-sm font-medium text-gray-900 group-hover:text-blue-600 transition-colors line-clamp-2">
                                            {item.title}
                                        </h3>
                                        <p className="text-xs text-gray-500 mt-1 line-clamp-2">
                                            {item.snippet}
                                        </p>

                                        {/* AI Analysis Reason */}
                                        {item.reason && (
                                            <div className="mt-2 flex items-start gap-1.5 bg-blue-50/50 p-2 rounded-lg">
                                                <svg className="w-3 h-3 text-blue-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                                </svg>
                                                <p className="text-xs text-blue-700 leading-tight">
                                                    {item.reason}
                                                </p>
                                            </div>
                                        )}

                                        <div className="flex items-center gap-2 mt-2">
                                            <span className="text-[10px] bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full">
                                                {item.source}
                                            </span>
                                            <span className="text-[10px] text-gray-400">
                                                {new Date(item.published_at).toLocaleDateString()}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </a>
                        ))}
                        {news.length === 0 && (
                            <p className="text-gray-500 text-sm text-center py-4">ニュースが見つかりませんでした</p>
                        )}
                    </div>
                )}
            </div>
            <div className="bg-gray-50 px-6 py-3 border-t border-gray-100 text-center">
                <button className="text-xs text-blue-600 hover:text-blue-700 font-medium">
                    もっと見る
                </button>
            </div>
        </div>
    );
}
