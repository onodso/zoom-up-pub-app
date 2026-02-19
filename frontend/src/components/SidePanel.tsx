// サイドパネル - 自治体の詳細情報を表示
// スコアカード、レーダーチャート、ニュース一覧等
import {
    RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
    ResponsiveContainer,
} from 'recharts';
import type { MunicipalityDetail } from '../api/mapApi';
import { getScoreColor } from '../api/mapApi';

interface Props {
    municipality: MunicipalityDetail;
    onClose: () => void;
}

// パターンID → バッジ色
const PATTERN_COLORS: Record<number, string> = {
    1: '#003f5c', 2: '#2f4b7c', 3: '#665191',
    4: '#a05195', 5: '#d45087', 6: '#f95d6a', 7: '#cccccc',
};

export default function SidePanel({ municipality: m, onClose }: Props) {
    const score = m.total_score || 0;
    const scoreColor = getScoreColor(score);

    // レーダーチャート用データ
    const radarData = [
        { subject: '住民サービス', value: (m.cat_citizen_services || 0) / 35 * 100, fullMark: 100 },
        { subject: '推進体制', value: (m.cat_promotion_system || 0) / 25 * 100, fullMark: 100 },
        { subject: '業務DX', value: (m.cat_business_dx || 0) / 20 * 100, fullMark: 100 },
        { subject: '教育DX', value: (m.cat_education_dx || 0) / 10 * 100, fullMark: 100 },
        { subject: '情報発信', value: (m.cat_information || 0) / 10 * 100, fullMark: 100 },
    ];

    // 同規模自治体比較データ
    const comparisonData = [
        { name: m.city_name, score: score },
        ...(m.similar_municipalities || []).map(s => ({
            name: s.city_name.length > 6 ? s.city_name.slice(0, 6) + '…' : s.city_name,
            score: s.total_score,
        })),
    ];

    // DX指標のバーチャートデータ
    const dxIndicators = m.dx_status ? Object.entries(m.dx_status).map(([key, value]) => {
        const shortKey = key
            .replace('住民サービスのDX_', '📱 ')
            .replace('自治体DXの推進体制等_', '🏛️ ')
            .replace('自治体業務のDX_', '💼 ');
        return { name: shortKey, value: String(value) };
    }) : [];

    return (
        <div className="side-panel">
            {/* ヘッダー */}
            <div className="panel-header">
                <button className="close-btn" onClick={onClose}>✕</button>
                <h2>{m.city_name}</h2>
                <div className="panel-meta">
                    {m.prefecture} ・ 人口 {(m.population || 0).toLocaleString()}人
                </div>
            </div>

            {/* スコアカード */}
            <div className="score-card" style={{ borderColor: scoreColor }}>
                <div className="score-big" style={{ color: scoreColor }}>{score}</div>
                <div className="score-label">総合DXスコア</div>
                <div className="score-rank">
                    全国 {m.national_rank || '-'} 位 / {m.total_municipalities || '-'}
                </div>
            </div>

            {/* パターンバッジ */}
            {m.pattern_name && (
                <div className="pattern-section">
                    <h3>DX推進パターン</h3>
                    <span
                        className="pattern-badge"
                        style={{ background: PATTERN_COLORS[m.pattern_id] || '#ccc' }}
                    >
                        {m.pattern_name}
                    </span>
                </div>
            )}

            {/* レーダーチャート */}
            <div className="chart-section">
                <h3>カテゴリ別スコア</h3>
                <ResponsiveContainer width="100%" height={250}>
                    <RadarChart data={radarData}>
                        <PolarGrid stroke="#444" />
                        <PolarAngleAxis dataKey="subject" tick={{ fill: '#ccc', fontSize: 11 }} />
                        <PolarRadiusAxis angle={90} domain={[0, 100]} tick={false} />
                        <Radar
                            name="スコア"
                            dataKey="value"
                            stroke={scoreColor}
                            fill={scoreColor}
                            fillOpacity={0.3}
                        />
                    </RadarChart>
                </ResponsiveContainer>
            </div>

            {/* 同規模自治体比較 */}
            {comparisonData.length > 1 && (
                <div className="chart-section">
                    <h3>同規模自治体との比較</h3>
                    <ResponsiveContainer width="100%" height={200}>
                        <BarChart data={comparisonData} layout="vertical">
                            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                            <XAxis type="number" domain={[0, 100]} tick={{ fill: '#ccc', fontSize: 10 }} />
                            <YAxis type="category" dataKey="name" tick={{ fill: '#ccc', fontSize: 10 }} width={80} />
                            <Tooltip
                                contentStyle={{ background: '#1a1a2e', border: '1px solid #444', color: '#fff' }}
                            />
                            <Bar
                                dataKey="score"
                                fill={scoreColor}
                                radius={[0, 4, 4, 0]}
                            />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            )}

            {/* GIGA情報 */}
            {m.computer_per_student !== null && m.computer_per_student !== undefined && (
                <div className="info-section">
                    <h3>📚 GIGAスクール</h3>
                    <div className="info-row">
                        <span>端末整備率:</span>
                        <strong>{Number(m.computer_per_student).toFixed(2)} 台/人</strong>
                    </div>
                </div>
            )}

            {/* DX指標一覧 */}
            {dxIndicators.length > 0 && (
                <div className="info-section">
                    <h3>📋 DX指標詳細 ({dxIndicators.length}項目)</h3>
                    <div className="indicator-list">
                        {dxIndicators.map((ind, i) => (
                            <div key={i} className="indicator-row">
                                <span className="indicator-name">{ind.name}</span>
                                <span className="indicator-value">{ind.value}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* ニュース */}
            {m.news && m.news.length > 0 && (
                <div className="info-section">
                    <h3>📰 最新ニュース ({m.news.length}件)</h3>
                    <div className="news-list">
                        {m.news.slice(0, 10).map((news, i) => (
                            <a
                                key={i}
                                href={news.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="news-item"
                            >
                                <span className={`news-category cat-${news.category}`}>
                                    {news.category}
                                </span>
                                <span className="news-title">{news.title}</span>
                                <span className="news-date">
                                    {news.published_at ?
                                        new Date(news.published_at).toLocaleDateString('ja-JP') : ''}
                                </span>
                            </a>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
