// 地図表示コンポーネント - Mapbox GL JS
// ドリルダウンのレベルに応じてマーカーを描画
import { useRef, useEffect, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import type {
    ViewLevel,
    RegionData,
    PrefectureData,
    MunicipalityData,
} from '../api/mapApi';
import {
    getScoreColor,
    REGION_CENTERS,
} from '../api/mapApi';

// Mapboxの公開トークン（制限付き・無料枠）
// 本番では環境変数から取得
mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN || '';

interface Props {
    viewLevel: ViewLevel;
    regions: RegionData[];
    prefectures: PrefectureData[];
    municipalities: MunicipalityData[];
    selectedRegion: string | null;
    onRegionClick: (region: string) => void;
    onPrefectureClick: (prefecture: string) => void;
    onMunicipalityClick: (cityCode: string) => void;
}

// 都道府県の中心座標（概算）
const PREFECTURE_CENTERS: Record<string, { lat: number; lng: number }> = {
    '北海道': { lat: 43.06, lng: 141.35 },
    '青森県': { lat: 40.82, lng: 140.74 }, '岩手県': { lat: 39.70, lng: 141.15 },
    '宮城県': { lat: 38.27, lng: 140.87 }, '秋田県': { lat: 39.72, lng: 140.10 },
    '山形県': { lat: 38.24, lng: 140.34 }, '福島県': { lat: 37.75, lng: 140.47 },
    '茨城県': { lat: 36.34, lng: 140.45 }, '栃木県': { lat: 36.57, lng: 139.88 },
    '群馬県': { lat: 36.39, lng: 139.06 }, '埼玉県': { lat: 35.86, lng: 139.65 },
    '千葉県': { lat: 35.61, lng: 140.12 }, '東京都': { lat: 35.68, lng: 139.69 },
    '神奈川県': { lat: 35.45, lng: 139.64 },
    '新潟県': { lat: 37.90, lng: 139.02 }, '富山県': { lat: 36.70, lng: 137.21 },
    '石川県': { lat: 36.59, lng: 136.63 }, '福井県': { lat: 36.07, lng: 136.22 },
    '山梨県': { lat: 35.66, lng: 138.57 }, '長野県': { lat: 36.23, lng: 138.18 },
    '岐阜県': { lat: 35.39, lng: 136.72 }, '静岡県': { lat: 34.98, lng: 138.38 },
    '愛知県': { lat: 35.18, lng: 136.91 },
    '三重県': { lat: 34.73, lng: 136.51 }, '滋賀県': { lat: 35.00, lng: 135.87 },
    '京都府': { lat: 35.02, lng: 135.76 }, '大阪府': { lat: 34.69, lng: 135.52 },
    '兵庫県': { lat: 34.69, lng: 135.18 }, '奈良県': { lat: 34.69, lng: 135.83 },
    '和歌山県': { lat: 34.23, lng: 135.17 },
    '鳥取県': { lat: 35.50, lng: 134.24 }, '島根県': { lat: 35.47, lng: 133.05 },
    '岡山県': { lat: 34.66, lng: 133.93 }, '広島県': { lat: 34.40, lng: 132.46 },
    '山口県': { lat: 34.19, lng: 131.47 },
    '徳島県': { lat: 34.07, lng: 134.56 }, '香川県': { lat: 34.34, lng: 134.04 },
    '愛媛県': { lat: 33.84, lng: 132.77 }, '高知県': { lat: 33.56, lng: 133.53 },
    '福岡県': { lat: 33.61, lng: 130.42 }, '佐賀県': { lat: 33.25, lng: 130.30 },
    '長崎県': { lat: 32.75, lng: 129.87 }, '熊本県': { lat: 32.79, lng: 130.74 },
    '大分県': { lat: 33.24, lng: 131.61 }, '宮崎県': { lat: 31.91, lng: 131.42 },
    '鹿児島県': { lat: 31.56, lng: 130.56 }, '沖縄県': { lat: 26.34, lng: 127.80 },
};

// XSSを防止するHTMLエスケープ関数
function escapeHtml(text: string): string {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

export default function MapView({
    viewLevel,
    regions,
    prefectures,
    municipalities,
    selectedRegion,
    onRegionClick,
    onPrefectureClick,
    onMunicipalityClick,
}: Props) {
    const mapContainer = useRef<HTMLDivElement>(null);
    const map = useRef<mapboxgl.Map | null>(null);
    const markersRef = useRef<mapboxgl.Marker[]>([]);
    const [mapReady, setMapReady] = useState(false);

    // Mapbox初期化
    useEffect(() => {
        if (!mapContainer.current) return;

        // トークンがない場合、OpenStreetMapスタイルを使用
        const useMapbox = !!mapboxgl.accessToken;

        map.current = new mapboxgl.Map({
            container: mapContainer.current,
            style: useMapbox
                ? 'mapbox://styles/mapbox/dark-v11'
                : 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
            center: [137.0, 38.0],
            zoom: 4.5,
            attributionControl: false,
        });

        map.current.addControl(new mapboxgl.NavigationControl(), 'top-right');
        map.current.addControl(new mapboxgl.AttributionControl({ compact: true }));

        map.current.on('load', () => {
            setMapReady(true);
        });

        return () => {
            map.current?.remove();
        };
    }, []);

    // マーカーをクリア
    const clearMarkers = () => {
        markersRef.current.forEach(m => m.remove());
        markersRef.current = [];
    };

    // Level 1: 地方マーカー
    useEffect(() => {
        if (!mapReady || viewLevel !== 'national' || !map.current) return;
        clearMarkers();

        // 全国表示にズームアウト
        map.current.flyTo({ center: [137.0, 38.0], zoom: 4.5, duration: 1500 });

        regions.forEach(region => {
            const center = REGION_CENTERS[region.region];
            if (!center) return;

            // カスタムHTMLマーカー
            const el = document.createElement('div');
            el.className = 'region-marker';
            el.style.background = getScoreColor(region.avg_score);
            el.innerHTML = `
        <div class="marker-label">${escapeHtml(region.region.replace('地方', ''))}</div>
        <div class="marker-score">${region.avg_score}</div>
      `;

            el.addEventListener('click', () => onRegionClick(region.region));

            const marker = new mapboxgl.Marker({ element: el })
                .setLngLat([center.lng, center.lat])
                .addTo(map.current!);

            markersRef.current.push(marker);
        });
    }, [mapReady, viewLevel, regions, onRegionClick]);

    // Level 2: 都道府県マーカー
    useEffect(() => {
        if (!mapReady || viewLevel !== 'region' || !map.current || !selectedRegion) return;
        clearMarkers();

        // 地方にズーム
        const regionCenter = REGION_CENTERS[selectedRegion];
        if (regionCenter) {
            map.current.flyTo({
                center: [regionCenter.lng, regionCenter.lat],
                zoom: regionCenter.zoom,
                duration: 1500
            });
        }

        prefectures.forEach(pref => {
            const center = PREFECTURE_CENTERS[pref.prefecture];
            if (!center) return;

            const el = document.createElement('div');
            el.className = 'prefecture-marker';
            el.style.background = getScoreColor(pref.avg_score || 0);
            el.innerHTML = `
        <div class="marker-label">${escapeHtml(pref.prefecture)}</div>
        <div class="marker-score">${pref.avg_score || '-'}</div>
        <div class="marker-count">${pref.municipality_count}市区町村</div>
      `;

            el.addEventListener('click', () => onPrefectureClick(pref.prefecture));

            const marker = new mapboxgl.Marker({ element: el })
                .setLngLat([center.lng, center.lat])
                .addTo(map.current!);

            markersRef.current.push(marker);
        });
    }, [mapReady, viewLevel, prefectures, selectedRegion, onPrefectureClick]);

    // Level 3: 自治体マーカー
    useEffect(() => {
        if (!mapReady || viewLevel !== 'prefecture' || !map.current) return;
        clearMarkers();

        if (municipalities.length === 0) return;

        // 都道府県にズーム - 最初の自治体の座標を基準
        const firstMuni = municipalities.find(m => m.latitude && m.longitude);
        if (firstMuni) {
            // 自治体の座標範囲からバウンディングボックスを計算
            const lats = municipalities.filter(m => m.latitude).map(m => m.latitude);
            const lngs = municipalities.filter(m => m.longitude).map(m => m.longitude);
            const bounds = new mapboxgl.LngLatBounds(
                [Math.min(...lngs) - 0.1, Math.min(...lats) - 0.1],
                [Math.max(...lngs) + 0.1, Math.max(...lats) + 0.1]
            );
            map.current.fitBounds(bounds, { padding: 50, duration: 1500 });
        }

        municipalities.forEach(muni => {
            if (!muni.latitude || !muni.longitude) return;

            const el = document.createElement('div');
            el.className = 'municipality-marker';
            const color = getScoreColor(muni.total_score || 0);
            el.style.background = color;
            el.style.borderColor = color;

            // 人口に応じたサイズ
            const pop = muni.population || 10000;
            // 最小12pxでモバイルでもタッチ可能に
            const size = Math.max(12, Math.min(28, Math.log10(pop) * 5));
            el.style.width = `${size}px`;
            el.style.height = `${size}px`;

            // ツールチップ
            const popup = new mapboxgl.Popup({ offset: 15, closeButton: false })
                .setHTML(`
          <div class="muni-popup">
            <strong>${escapeHtml(muni.city_name)}</strong>
            <div>スコア: <b>${muni.total_score}</b></div>
            <div>人口: ${(muni.population || 0).toLocaleString()}</div>
            <div class="popup-hint">クリックで詳細</div>
          </div>
        `);

            el.addEventListener('click', () => onMunicipalityClick(muni.city_code));

            const marker = new mapboxgl.Marker({ element: el })
                .setLngLat([muni.longitude, muni.latitude])
                .setPopup(popup)
                .addTo(map.current!);

            // ホバーでポップアップ表示（toggleの代わりにopen/closeで安定動作）
            el.addEventListener('mouseenter', () => { if (!marker.getPopup()?.isOpen()) marker.togglePopup(); });
            el.addEventListener('mouseleave', () => { if (marker.getPopup()?.isOpen()) marker.togglePopup(); });

            markersRef.current.push(marker);
        });
    }, [mapReady, viewLevel, municipalities, onMunicipalityClick]);

    return (
        <div ref={mapContainer} className="map-view">
            {/* 凡例 */}
            <div className="legend">
                <div className="legend-title">DXスコア</div>
                <div className="legend-item">
                    <span className="legend-color" style={{ background: '#003f5c' }}></span>
                    <span>80-100 先進</span>
                </div>
                <div className="legend-item">
                    <span className="legend-color" style={{ background: '#2f9e8f' }}></span>
                    <span>65-79 進行中</span>
                </div>
                <div className="legend-item">
                    <span className="legend-color" style={{ background: '#a8d08d' }}></span>
                    <span>50-64 平均的</span>
                </div>
                <div className="legend-item">
                    <span className="legend-color" style={{ background: '#f9a03f' }}></span>
                    <span>30-49 遅延</span>
                </div>
                <div className="legend-item">
                    <span className="legend-color" style={{ background: '#e63946' }}></span>
                    <span>0-29 初期段階</span>
                </div>
            </div>
        </div>
    );
}
