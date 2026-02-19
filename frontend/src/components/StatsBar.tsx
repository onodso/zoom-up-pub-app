// 統計バー - ヘッダーに表示するKPIメトリクス
import type { StatsData } from '../api/mapApi';
import { getScoreColor } from '../api/mapApi';

interface Props {
    stats: StatsData;
}

export default function StatsBar({ stats }: Props) {
    return (
        <div className="stats-bar">
            <div className="stat-item">
                <div className="stat-value">{stats.total_municipalities?.toLocaleString()}</div>
                <div className="stat-label">自治体数</div>
            </div>
            <div className="stat-item">
                <div className="stat-value" style={{ color: getScoreColor(stats.avg_score || 0) }}>
                    {stats.avg_score}
                </div>
                <div className="stat-label">平均スコア</div>
            </div>
            <div className="stat-item">
                <div className="stat-value" style={{ color: getScoreColor(stats.max_score || 0) }}>
                    {stats.max_score}
                </div>
                <div className="stat-label">最高スコア</div>
            </div>
            <div className="stat-item">
                <div className="stat-value" style={{ color: '#e63946' }}>
                    {stats.min_score}
                </div>
                <div className="stat-label">最低スコア</div>
            </div>
        </div>
    );
}
