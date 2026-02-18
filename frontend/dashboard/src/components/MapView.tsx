// 地図表示コンポーネント - Mapbox GL JS
// ドリルダウンのレベルに応じてマーカーを描画
import { useRef, useEffect, useState } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import * as topojson from 'topojson-client';
import type { Topology, GeometryCollection } from 'topojson-specification';
import type {
    ViewLevel,
    RegionData,
    PrefectureData,
    MunicipalityData,
} from '../api/mapApi';
import {
    getScoreColor,
    REGION_CENTERS,
    fetchPrefectures,
} from '../api/mapApi';

// MapLibre GL JS: トークン不要、CARTOタイルを使用

interface Props {
    viewLevel: ViewLevel;
    regions: RegionData[];
    prefectures: PrefectureData[];
    municipalities: MunicipalityData[];
    selectedRegion: string | null;
    selectedPrefecture?: string | null;
    onRegionClick: (region: string) => void;
    onPrefectureClick: (prefecture: string) => void;
    onMunicipalityClick: (cityCode: string) => void;
    onBack?: () => void;
}

export default function MapView({
    viewLevel,
    regions,
    prefectures,
    municipalities,
    selectedRegion,
    selectedPrefecture,
    onRegionClick,
    onPrefectureClick,
    onMunicipalityClick,
    onBack,
}: Props) {
    const mapContainer = useRef<HTMLDivElement>(null);
    const map = useRef<maplibregl.Map | null>(null);
    const markersRef = useRef<maplibregl.Marker[]>([]);
    const [mapReady, setMapReady] = useState(false);

    // 全都道府県スコア（コロプレスマップ用）
    const [allPrefScores, setAllPrefScores] = useState<Record<string, number>>({});
    // 自治体境界GeoJSON（コロプレスマップ用）
    const [municipalityGeoJson, setMunicipalityGeoJson] = useState<any>(null);

    // MapLibre初期化
    useEffect(() => {
        if (!mapContainer.current) return;

        // CARTOタイルを直接定義したカスタムスタイル（認証不要）
        const cartoStyle = {
            version: 8,
            sources: {
                'carto-dark': {
                    type: 'raster',
                    tiles: ['https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png'],
                    tileSize: 256,
                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
                }
            },
            layers: [{
                id: 'carto-dark-layer',
                type: 'raster',
                source: 'carto-dark',
                minzoom: 0,
                maxzoom: 22
            }]
        };

        map.current = new maplibregl.Map({
            container: mapContainer.current,
            style: cartoStyle as any,
            center: [137.0, 38.0],
            zoom: 4.5,
            attributionControl: false,
        });

        map.current.addControl(new maplibregl.NavigationControl(), 'top-right');
        map.current.addControl(new maplibregl.AttributionControl({ compact: true }));

        map.current.on('load', () => {
            setMapReady(true);
            // 境界線データを読み込み
            loadBoundaries();
            // 全都道府県スコアを取得（コロプレス用）
            loadAllPrefectureScores();
            // 自治体境界データを読み込み（コロプレス用）
            loadMunicipalityBoundaries();
        });

        return () => {
            map.current?.remove();
        };
    }, []);

    // 全都道府県スコアを取得（コロプレス用）
    const loadAllPrefectureScores = async () => {
        try {
            const allPrefs = await fetchPrefectures();
            const scores: Record<string, number> = {};
            allPrefs.forEach(p => {
                scores[p.prefecture] = p.avg_score;
            });
            setAllPrefScores(scores);
            console.log('✅ 全都道府県スコア取得完了:', Object.keys(scores).length, '件');
        } catch (err) {
            console.error('都道府県スコア取得エラー:', err);
        }
    };

    // 自治体境界GeoJSONを読み込み（コロプレス用）
    const loadMunicipalityBoundaries = async () => {
        try {
            const response = await fetch(
                'https://raw.githubusercontent.com/smartnews-smri/japan-topography/main/data/municipality/geojson/s0001/N03-21_210101.json'
            );
            const geojson = await response.json();
            setMunicipalityGeoJson(geojson);
            console.log('✅ 自治体境界データ読み込み完了:', geojson.features.length, '件');
        } catch (err) {
            console.error('自治体境界データ読み込みエラー:', err);
        }
    };

    // 境界線データの読み込みと追加
    const loadBoundaries = async () => {
        if (!map.current) return;

        try {
            // 都道府県境界（TopoJSON from dataofjapan/land）
            const response = await fetch('https://cdn.jsdelivr.net/gh/dataofjapan/land@master/japan.topojson');
            const topo = await response.json() as Topology;

            // TopoJSONをGeoJSONに変換
            const geo = topojson.feature(
                topo,
                topo.objects.japan as GeometryCollection
            );

            // 都道府県境界レイヤー追加
            map.current!.addSource('prefecture-boundaries', {
                type: 'geojson',
                data: geo as GeoJSON.FeatureCollection,
            });

            // 境界線（青色）
            map.current!.addLayer({
                id: 'prefecture-borders',
                type: 'line',
                source: 'prefecture-boundaries',
                paint: {
                    'line-color': '#58a6ff',
                    'line-width': 1.5,
                    'line-opacity': 0.6,
                },
            });

            // 塗りつぶし（初期は透明、スコアデータが来たらコロプレス表示）
            map.current!.addLayer({
                id: 'prefecture-fill',
                type: 'fill',
                source: 'prefecture-boundaries',
                paint: {
                    'fill-color': '#1f6feb',
                    'fill-opacity': 0.05,
                },
            }, 'prefecture-borders'); // 境界線の下に配置

            // 都道府県名ラベルレイヤー（常に表示）
            map.current!.addLayer({
                id: 'prefecture-labels',
                type: 'symbol',
                source: 'prefecture-boundaries',
                layout: {
                    'text-field': ['get', 'nam_ja'],
                    'text-font': ['Open Sans Regular', 'Arial Unicode MS Regular'],
                    'text-size': 14,
                    'text-anchor': 'center',
                    'text-offset': [0, 0],
                    'text-allow-overlap': false,
                    'text-optional': true,
                    'visibility': 'none', // 初期は非表示、ビューレベルで制御
                },
                paint: {
                    'text-color': '#ffffff',
                    'text-halo-color': '#000000',
                    'text-halo-width': 2,
                    'text-opacity': 0.9,
                },
            });

            console.log('✅ 都道府県境界線データ読み込み完了');
        } catch (err) {
            console.error('境界線データ読み込みエラー:', err);
        }
    };

    // 自治体境界レイヤーを追加（コロプレス用）
    const addMunicipalityBoundaryLayers = () => {
        if (!map.current || !municipalityGeoJson) return;
        if (map.current.getSource('municipality-boundaries')) return;

        // 自治体境界ソース追加
        map.current.addSource('municipality-boundaries', {
            type: 'geojson',
            data: municipalityGeoJson,
        });

        // 塗りつぶしレイヤー（初期は非表示）
        map.current.addLayer({
            id: 'municipality-fill',
            type: 'fill',
            source: 'municipality-boundaries',
            paint: {
                'fill-color': '#1f6feb',
                'fill-opacity': 0,
            },
        });

        // 境界線レイヤー（初期は非表示）
        map.current.addLayer({
            id: 'municipality-borders',
            type: 'line',
            source: 'municipality-boundaries',
            paint: {
                'line-color': '#58a6ff',
                'line-width': 1.5, // 太くして見やすく
                'line-opacity': 0,
            },
        });

        // 自治体名ラベルレイヤー（人口5万人以上の自治体のみ表示）
        map.current.addLayer({
            id: 'municipality-labels',
            type: 'symbol',
            source: 'municipality-boundaries',
            layout: {
                'text-field': ['get', 'N03_004'], // 市区町村名
                'text-font': ['Open Sans Regular', 'Arial Unicode MS Regular'],
                'text-size': 12,
                'text-anchor': 'center',
                'text-offset': [0, 0],
                'text-allow-overlap': false,
                'text-optional': true,
                'visibility': 'none', // 初期は非表示、ビューレベルで制御
            },
            paint: {
                'text-color': '#ffffff',
                'text-halo-color': '#000000',
                'text-halo-width': 2,
                'text-opacity': 0.85,
            },
        });

        console.log('✅ 自治体境界レイヤー追加完了');
    };

    // 自治体境界GeoJSONが読み込まれたらレイヤーを追加
    useEffect(() => {
        if (!mapReady || !municipalityGeoJson) return;
        addMunicipalityBoundaryLayers();
    }, [mapReady, municipalityGeoJson]);

    // クリック可能なポリゴン領域の設定（都道府県レイヤー）
    useEffect(() => {
        if (!mapReady || !map.current) return;
        if (!map.current.getLayer('prefecture-fill')) return;

        // 都道府県ポリゴンクリックイベント
        const handlePrefectureClick = (e: any) => {
            if (!e.features || e.features.length === 0) return;
            const prefectureName = e.features[0].properties.nam_ja;
            if (!prefectureName) return;

            // Level 1（全国ビュー）では地方に遷移、Level 2（地方ビュー）では都道府県に遷移
            if (viewLevel === 'national') {
                // 全都道府県データから地方を検索
                const pref = prefectures.find(p => p.prefecture === prefectureName);
                if (pref && pref.region) {
                    onRegionClick(pref.region);
                }
            } else {
                // Level 2（地方ビュー）では通常通り都道府県詳細へ
                onPrefectureClick(prefectureName);
            }
        };

        // ホバー時のカーソル変更（ツールチップなし、シンプルに）
        const handlePrefectureMouseEnter = () => {
            if (!map.current) return;
            map.current.getCanvas().style.cursor = 'pointer';
            // ホバー時に不透明度を上げて視覚的フィードバック
            map.current.setPaintProperty('prefecture-fill', 'fill-opacity', 0.6);
        };

        const handlePrefectureMouseLeave = () => {
            if (map.current) {
                map.current.getCanvas().style.cursor = '';
                // 元の不透明度に戻す（ビューレベルに応じて調整）
                const baseOpacity = viewLevel === 'national' ? 0.35 : viewLevel === 'region' ? 0.45 : 0.1;
                map.current.setPaintProperty('prefecture-fill', 'fill-opacity', baseOpacity);
            }
        };

        // イベントリスナー登録
        map.current.on('click', 'prefecture-fill', handlePrefectureClick);
        map.current.on('mouseenter', 'prefecture-fill', handlePrefectureMouseEnter);
        map.current.on('mouseleave', 'prefecture-fill', handlePrefectureMouseLeave);

        // クリーンアップ
        return () => {
            if (!map.current) return;
            map.current.off('click', 'prefecture-fill', handlePrefectureClick);
            map.current.off('mouseenter', 'prefecture-fill', handlePrefectureMouseEnter);
            map.current.off('mouseleave', 'prefecture-fill', handlePrefectureMouseLeave);
        };
    }, [mapReady, viewLevel, allPrefScores, prefectures, onPrefectureClick, onRegionClick]);

    // クリック可能なポリゴン領域の設定（自治体レイヤー）
    useEffect(() => {
        if (!mapReady || !map.current) return;
        if (!map.current.getLayer('municipality-fill')) return;

        // 自治体ポリゴンクリックイベント
        const handleMunicipalityClick = (e: any) => {
            if (!e.features || e.features.length === 0) return;
            const cityCode = e.features[0].properties.N03_007;
            if (cityCode) {
                onMunicipalityClick(cityCode);
            }
        };

        // ホバー時のカーソル変更（ツールチップなし、シンプルに）
        const handleMunicipalityMouseEnter = () => {
            if (!map.current) return;
            map.current.getCanvas().style.cursor = 'pointer';
            // ホバー時に不透明度を上げて視覚的フィードバック
            map.current.setPaintProperty('municipality-fill', 'fill-opacity', 0.7);
        };

        const handleMunicipalityMouseLeave = () => {
            if (map.current) {
                map.current.getCanvas().style.cursor = '';
                // 元の不透明度に戻す
                map.current.setPaintProperty('municipality-fill', 'fill-opacity', 0.5);
            }
        };

        // イベントリスナー登録
        map.current.on('click', 'municipality-fill', handleMunicipalityClick);
        map.current.on('mouseenter', 'municipality-fill', handleMunicipalityMouseEnter);
        map.current.on('mouseleave', 'municipality-fill', handleMunicipalityMouseLeave);

        // クリーンアップ
        return () => {
            if (!map.current) return;
            map.current.off('click', 'municipality-fill', handleMunicipalityClick);
            map.current.off('mouseenter', 'municipality-fill', handleMunicipalityMouseEnter);
            map.current.off('mouseleave', 'municipality-fill', handleMunicipalityMouseLeave);
        };
    }, [mapReady, municipalities, onMunicipalityClick]);

    // コロプレスマップ: 都道府県スコアに基づく色分け
    useEffect(() => {
        if (!mapReady || !map.current || Object.keys(allPrefScores).length === 0) return;
        if (!map.current.getLayer('prefecture-fill')) return;

        // MapLibreのmatch式を構築: ['match', ['get', 'nam_ja'], '北海道', '#色', ...]
        const matchExpr: any[] = ['match', ['get', 'nam_ja']];
        Object.entries(allPrefScores).forEach(([prefName, score]) => {
            matchExpr.push(prefName, getScoreColor(score));
        });
        matchExpr.push('#333333'); // デフォルト色（マッチしない場合）

        map.current.setPaintProperty('prefecture-fill', 'fill-color', matchExpr);
        map.current.setPaintProperty('prefecture-fill', 'fill-opacity', 0.35);

        // 境界線もスコアに応じた色に（さらにリッチな表現）
        map.current.setPaintProperty('prefecture-borders', 'line-color', matchExpr);
        map.current.setPaintProperty('prefecture-borders', 'line-width', 2);
        map.current.setPaintProperty('prefecture-borders', 'line-opacity', 0.8);

        console.log('✅ コロプレスマップ適用完了');
    }, [mapReady, allPrefScores]);

    // コロプレスマップ: 自治体スコアに基づく色分け
    useEffect(() => {
        if (!mapReady || !map.current || municipalities.length === 0) return;
        if (!map.current.getLayer('municipality-fill')) return;

        // 自治体のcity_codeとスコアのマッピング
        const matchExpr: any[] = ['match', ['get', 'N03_007']];
        municipalities.forEach(muni => {
            const score = muni.total_score || 0;
            matchExpr.push(muni.city_code, getScoreColor(score));
        });
        matchExpr.push('#333333'); // デフォルト色（マッチしない場合）

        map.current.setPaintProperty('municipality-fill', 'fill-color', matchExpr);

        // 境界線もスコアに応じた色に
        if (map.current.getLayer('municipality-borders')) {
            map.current.setPaintProperty('municipality-borders', 'line-color', matchExpr);
        }

        console.log('✅ 自治体コロプレスマップ適用完了:', municipalities.length, '件');
    }, [mapReady, municipalities]);

    // マーカーをクリア
    const clearMarkers = () => {
        markersRef.current.forEach(m => m.remove());
        markersRef.current = [];
    };

    // Level 1: 全国ビュー（マーカーなし、地方ラベルのみ）
    useEffect(() => {
        if (!mapReady || viewLevel !== 'national' || !map.current) return;
        clearMarkers();

        // 全国表示にズームアウト
        map.current.flyTo({ center: [137.0, 38.0], zoom: 4.5, duration: 1500 });

        // 全国ビュー: 都道府県境界とコロプレスを鮮やかに表示
        if (map.current!.getLayer('prefecture-borders')) {
            map.current!.setLayoutProperty('prefecture-borders', 'visibility', 'visible');
            map.current!.setPaintProperty('prefecture-borders', 'line-opacity', 0.8);
        }
        if (map.current!.getLayer('prefecture-fill')) {
            map.current!.setLayoutProperty('prefecture-fill', 'visibility', 'visible');
            map.current!.setPaintProperty('prefecture-fill', 'fill-opacity', 0.35);
        }

        // 自治体境界を非表示
        if (map.current!.getLayer('municipality-borders')) {
            map.current!.setLayoutProperty('municipality-borders', 'visibility', 'none');
        }
        if (map.current!.getLayer('municipality-fill')) {
            map.current!.setLayoutProperty('municipality-fill', 'visibility', 'none');
        }

        // ラベルを非表示
        if (map.current!.getLayer('prefecture-labels')) {
            map.current!.setLayoutProperty('prefecture-labels', 'visibility', 'none');
        }
        if (map.current!.getLayer('municipality-labels')) {
            map.current!.setLayoutProperty('municipality-labels', 'visibility', 'none');
        }
    }, [mapReady, viewLevel, regions, onRegionClick]);

    // Level 2: 都道府県ビュー（マーカーなし、ラベルのみ）
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

        // 地方ビュー: コロプレスをより鮮やかに表示
        if (map.current!.getLayer('prefecture-borders')) {
            map.current!.setLayoutProperty('prefecture-borders', 'visibility', 'visible');
            map.current!.setPaintProperty('prefecture-borders', 'line-opacity', 0.9);
        }
        if (map.current!.getLayer('prefecture-fill')) {
            map.current!.setLayoutProperty('prefecture-fill', 'visibility', 'visible');
            map.current!.setPaintProperty('prefecture-fill', 'fill-opacity', 0.45);
        }

        // 自治体境界を非表示
        if (map.current!.getLayer('municipality-borders')) {
            map.current!.setLayoutProperty('municipality-borders', 'visibility', 'none');
        }
        if (map.current!.getLayer('municipality-fill')) {
            map.current!.setLayoutProperty('municipality-fill', 'visibility', 'none');
        }

        // 都道府県ラベルを表示
        if (map.current!.getLayer('prefecture-labels')) {
            map.current!.setLayoutProperty('prefecture-labels', 'visibility', 'visible');
        }

        // 自治体ラベルを非表示
        if (map.current!.getLayer('municipality-labels')) {
            map.current!.setLayoutProperty('municipality-labels', 'visibility', 'none');
        }
    }, [mapReady, viewLevel, prefectures, selectedRegion, onPrefectureClick]);

    // Level 3: 自治体ビュー（マーカーなし、ラベルのみ）
    useEffect(() => {
        if (!mapReady || viewLevel !== 'prefecture' || !map.current) return;
        clearMarkers();

        if (municipalities.length === 0) return;

        // 都道府県にズーム - 自治体の座標範囲からバウンディングボックスを計算
        const lats = municipalities.filter(m => m.latitude).map(m => m.latitude);
        const lngs = municipalities.filter(m => m.longitude).map(m => m.longitude);
        if (lats.length > 0 && lngs.length > 0) {
            const bounds = new maplibregl.LngLatBounds(
                [Math.min(...lngs) - 0.1, Math.min(...lats) - 0.1],
                [Math.max(...lngs) + 0.1, Math.max(...lats) + 0.1]
            );
            map.current.fitBounds(bounds, { padding: 50, duration: 1500 });
        }

        // 都道府県ビュー: 都道府県コロプレスを薄く、自治体コロプレスを鮮やかに表示
        if (map.current!.getLayer('prefecture-borders')) {
            map.current!.setPaintProperty('prefecture-borders', 'line-opacity', 0.3);
            map.current!.setLayoutProperty('prefecture-borders', 'visibility', 'visible');
        }
        if (map.current!.getLayer('prefecture-fill')) {
            map.current!.setLayoutProperty('prefecture-fill', 'visibility', 'visible');
            map.current!.setPaintProperty('prefecture-fill', 'fill-opacity', 0.1);
        }

        // 都道府県ラベルを非表示
        if (map.current!.getLayer('prefecture-labels')) {
            map.current!.setLayoutProperty('prefecture-labels', 'visibility', 'none');
        }

        // 自治体境界を表示（スコアで色分け）
        if (map.current!.getLayer('municipality-borders')) {
            map.current!.setLayoutProperty('municipality-borders', 'visibility', 'visible');
            map.current!.setPaintProperty('municipality-borders', 'line-opacity', 0.9);
            map.current!.setPaintProperty('municipality-borders', 'line-width', 2);
        }
        if (map.current!.getLayer('municipality-fill')) {
            map.current!.setLayoutProperty('municipality-fill', 'visibility', 'visible');
            map.current!.setPaintProperty('municipality-fill', 'fill-opacity', 0.5);
        }

        // 自治体ラベルを表示
        if (map.current!.getLayer('municipality-labels')) {
            map.current!.setLayoutProperty('municipality-labels', 'visibility', 'visible');
        }
    }, [mapReady, viewLevel, municipalities, onMunicipalityClick]);

    return (
        <div ref={mapContainer} className="map-view">
            {/* 戻るボタン */}
            {viewLevel !== 'national' && onBack && (
                <button
                    className="back-button"
                    onClick={onBack}
                    title={viewLevel === 'region' ? '全国に戻る' : '地方に戻る'}
                >
                    ← {viewLevel === 'region' ? '全国' : viewLevel === 'prefecture' ? (selectedPrefecture || '地方') : '戻る'}
                </button>
            )}

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
