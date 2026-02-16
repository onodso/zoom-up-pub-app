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

// DXスコアに対応する色を返す（グラデーション）
export function getScoreColor(score: number): string {
    if (score >= 80) return '#003f5c';   // 濃い青: DXが非常に進んでいる
    if (score >= 65) return '#2f9e8f';   // 青緑: 進行中
    if (score >= 50) return '#a8d08d';   // 黄緑: 平均的
    if (score >= 30) return '#f9a03f';   // オレンジ: やや遅れている
    if (score > 0) return '#e63946';    // 赤: 大幅に遅れている
    return '#cccccc';                     // グレー: データなし
}

// Mapbox用にスコアをstopsに変換
export function getScoreColorStops(): Array<[number, string]> {
    return [
        [0, '#cccccc'],
        [1, '#e63946'],
        [30, '#f9a03f'],
        [50, '#a8d08d'],
        [65, '#2f9e8f'],
        [80, '#003f5c'],
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
