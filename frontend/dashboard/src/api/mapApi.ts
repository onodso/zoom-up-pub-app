// APIクライアント - バックエンドのMap Data APIとの通信
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE,
    timeout: 10000,
});

// ===== 型定義 =====

export interface RegionData {
    region: string;
    avg_score: number;
    municipality_count: number;
    prefecture_count: number;
    total_population: number;
    prefectures: string[];
}

export interface PrefectureData {
    prefecture: string;
    region: string;
    avg_score: number;
    avg_citizen: number;
    avg_promotion: number;
    avg_business: number;
    avg_education: number;
    avg_information: number;
    municipality_count: number;
    total_population: number;
}

export interface MunicipalityData {
    city_code: string;
    city_name: string;
    prefecture: string;
    region: string;
    population: number;
    latitude: number;
    longitude: number;
    total_score: number;
    cat_citizen_services: number;
    cat_promotion_system: number;
    cat_business_dx: number;
    cat_education_dx: number;
    cat_information: number;
    pattern_id: number;
    pattern_name: string;
}

export interface NewsItem {
    title: string;
    url: string;
    source: string;
    category: string;
    published_at: string;
    collected_at: string;
}

export interface MunicipalityDetail extends MunicipalityData {
    dx_status: Record<string, string>;
    total_score: number;
    pattern_id: number;
    pattern_name: string;
    confidence_score: number;
    policy_status: string;
    mynumber_rate: number;
    online_proc_rate: number;
    computer_per_student: number;
    terminal_os_type: string;
    survey_year: string;
    news: NewsItem[];
    national_rank: number;
    total_municipalities: number;
    similar_municipalities: Array<{
        city_name: string;
        population: number;
        total_score: number;
    }>;
}

export interface StatsData {
    total_municipalities: number;
    avg_score: number;
    min_score: number;
    max_score: number;
    stddev_score: number;
    pattern_distribution: Array<{
        pattern_name: string;
        count: number;
    }>;
}

// ドリルダウンの階層レベル
export type ViewLevel = 'national' | 'region' | 'prefecture' | 'municipality';

// ===== API関数 =====

export async function fetchRegions(): Promise<RegionData[]> {
    const { data } = await api.get<RegionData[]>('/api/v1/map/regions');
    return data;
}

export async function fetchPrefectures(region?: string): Promise<PrefectureData[]> {
    const params = region ? { region } : {};
    const { data } = await api.get<PrefectureData[]>('/api/v1/map/prefectures', { params });
    return data;
}

export async function fetchMunicipalities(
    prefecture?: string,
    region?: string
): Promise<MunicipalityData[]> {
    const params: Record<string, string> = {};
    if (prefecture) params.prefecture = prefecture;
    if (region) params.region = region;
    const { data } = await api.get<MunicipalityData[]>('/api/v1/map/municipalities', { params });
    return data;
}

export async function fetchMunicipalityDetail(cityCode: string): Promise<MunicipalityDetail> {
    const { data } = await api.get<MunicipalityDetail>(`/api/v1/map/municipality/${cityCode}`);
    return data;
}

export async function fetchStats(): Promise<StatsData> {
    const { data } = await api.get<StatsData>('/api/v1/map/stats');
    return data;
}

// ===== ユーティリティ =====

// DXスコアに対応する色を返す（改善版スコア対応: 10-54点範囲）
export function getScoreColor(score: number): string {
    // 統一デザインシステム: Zoom Blue → Microsoft Red
    // ColorBrewer準拠 + 色覚多様性対応
    // 新スコア分布:
    // 48+点: Zoom最適 (濃紺 #003D82)
    // 42-47点: Zoom有望 (Zoom Blue #0E71EB)
    // 38-41点: 良好 (明るいZoom Blue #2D8CFF)
    // 34-37点: 平均 (水色 #89C4F4) - 最多層
    // 28-33点: やや課題 (アンバー #FFB84D)
    // 22-27点: 課題あり (オレンジ #FF8A65)
    // 15-21点: MS領域 (Microsoft Red #F25022)
    // 1-14点: 要改善 (濃い赤 #D13438)
    if (score >= 48) return '#003D82';   // 濃紺 (Zoom Blue 900) - Zoom最適
    if (score >= 42) return '#0E71EB';   // Zoom Blue - Zoom有望
    if (score >= 38) return '#2D8CFF';   // 明るいZoom Blue - 良好
    if (score >= 34) return '#89C4F4';   // 水色 - 平均
    if (score >= 28) return '#FFB84D';   // アンバー - やや課題
    if (score >= 22) return '#FF8A65';   // オレンジ - 課題あり
    if (score >= 15) return '#F25022';   // Microsoft Red - MS領域
    if (score > 0)  return '#D13438';    // 濃い赤 - 要改善
    return '#9CA3AF';                    // グレー - データなし
}

// Mapbox用にスコアをstopsに変換（統一デザインシステム）
export function getScoreColorStops(): Array<[number, string]> {
    return [
        [0, '#9CA3AF'],    // グレー: データなし
        [1, '#D13438'],    // 濃い赤: 要改善
        [15, '#F25022'],   // Microsoft Red: MS領域
        [22, '#FF8A65'],   // オレンジ: 課題あり
        [28, '#FFB84D'],   // アンバー: やや課題
        [34, '#89C4F4'],   // 水色: 平均 (最多層)
        [38, '#2D8CFF'],   // 明るいZoom Blue: 良好
        [42, '#0E71EB'],   // Zoom Blue: Zoom有望
        [48, '#003D82'],   // 濃紺: Zoom最適
    ];
}

// 地方名の中心座標
export const REGION_CENTERS: Record<string, { lat: number; lng: number; zoom: number }> = {
    '北海道地方': { lat: 43.06, lng: 141.35, zoom: 6 },
    '東北地方': { lat: 39.00, lng: 140.00, zoom: 6.5 },
    '関東地方': { lat: 35.80, lng: 139.80, zoom: 7.5 },
    '中部地方': { lat: 36.20, lng: 137.50, zoom: 7 },
    '近畿地方': { lat: 34.70, lng: 135.50, zoom: 7.5 },
    '中国地方': { lat: 34.60, lng: 132.50, zoom: 7.5 },
    '四国地方': { lat: 33.70, lng: 133.50, zoom: 8 },
    '九州・沖縄地方': { lat: 32.50, lng: 130.70, zoom: 7 },
};

// 都道府県の中心座標（ラベル表示用）
export const PREFECTURE_CENTERS: Record<string, [number, number]> = {
    '北海道': [141.35, 43.06],
    '青森県': [140.74, 40.82],
    '岩手県': [141.15, 39.70],
    '宮城県': [140.87, 38.27],
    '秋田県': [140.10, 39.72],
    '山形県': [140.36, 38.24],
    '福島県': [140.47, 37.75],
    '茨城県': [140.45, 36.34],
    '栃木県': [139.88, 36.57],
    '群馬県': [139.06, 36.39],
    '埼玉県': [139.65, 35.86],
    '千葉県': [140.12, 35.61],
    '東京都': [139.69, 35.69],
    '神奈川県': [139.64, 35.45],
    '新潟県': [139.02, 37.90],
    '富山県': [137.21, 36.70],
    '石川県': [136.63, 36.59],
    '福井県': [136.22, 36.07],
    '山梨県': [138.57, 35.66],
    '長野県': [138.18, 36.65],
    '岐阜県': [136.72, 35.39],
    '静岡県': [138.38, 34.98],
    '愛知県': [136.91, 35.18],
    '三重県': [136.51, 34.73],
    '滋賀県': [135.87, 35.00],
    '京都府': [135.76, 35.02],
    '大阪府': [135.52, 34.69],
    '兵庫県': [135.18, 34.69],
    '奈良県': [135.83, 34.69],
    '和歌山県': [135.17, 34.23],
    '鳥取県': [134.24, 35.50],
    '島根県': [133.05, 35.47],
    '岡山県': [133.92, 34.66],
    '広島県': [132.46, 34.40],
    '山口県': [131.47, 34.19],
    '徳島県': [134.56, 34.07],
    '香川県': [134.04, 34.34],
    '愛媛県': [132.77, 33.84],
    '高知県': [133.53, 33.56],
    '福岡県': [130.42, 33.61],
    '佐賀県': [130.30, 33.25],
    '長崎県': [129.87, 32.75],
    '熊本県': [130.71, 32.79],
    '大分県': [131.61, 33.24],
    '宮崎県': [131.42, 31.91],
    '鹿児島県': [130.56, 31.56],
    '沖縄県': [127.68, 26.21],
};
