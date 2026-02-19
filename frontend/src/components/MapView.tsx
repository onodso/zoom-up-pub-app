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
    PREFECTURE_CENTERS,
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
    // 全都道府県データ（地方情報を含む、ナビゲーション用）
    const [allPrefecturesData, setAllPrefecturesData] = useState<PrefectureData[]>([]);
    // 自治体境界GeoJSON（コロプレスマップ用）
    const [municipalityGeoJson, setMunicipalityGeoJson] = useState<any>(null);

    // MapLibre初期化
    useEffect(() => {
        if (!mapContainer.current) return;

        // CARTOタイルを直接定義したカスタムスタイル（認証不要）
        // Dark Matter (No Labels) - 落ち着いた色調、大陸は目立たない
        const cartoStyle = {
            version: 8,
            sources: {
                'carto-dark': {
                    type: 'raster',
                    tiles: ['https://a.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}.png'],
                    tileSize: 256,
                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
                }
            },
            layers: [{
                id: 'carto-dark-layer',
                type: 'raster',
                source: 'carto-dark',
                minzoom: 0,
                maxzoom: 22,
                paint: {
                    'raster-opacity': 0.85  // やや透明にして眩しさを抑える
                }
            }]
        };

        map.current = new maplibregl.Map({
            container: mapContainer.current,
            style: cartoStyle as any,
            center: [138.5, 37.5],  // 日本中心（やや東寄り）
            zoom: 4.0,  // 日本全体が見える初期表示
            minZoom: 1.8,  // 北海道から沖縄まで完全に見えるズームレベル
            maxZoom: 18,   // 詳細表示の最大ズーム
            maxBounds: [
                [115.0, 17.0],  // 南西端（沖縄南部＋十分な余裕）
                [158.0, 52.0],  // 北東端（北方領土＋十分な余裕）
            ],
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
            setAllPrefecturesData(allPrefs); // 全都道府県データを保存（地方情報を含む）
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
            ) as GeoJSON.FeatureCollection;

            // 都道府県境界ソース（全ての都道府県を通常表示）
            map.current!.addSource('prefecture-boundaries', {
                type: 'geojson',
                data: geo,
            });

            // 境界線（Zoom Blue）
            map.current!.addLayer({
                id: 'prefecture-borders',
                type: 'line',
                source: 'prefecture-boundaries',
                paint: {
                    'line-color': '#2D8CFF',
                    'line-width': 2,
                    'line-opacity': 0.7,
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

            // 都道府県の中心点GeoJSONを作成（1県1ラベル用）
            const prefectureLabelPoints: GeoJSON.FeatureCollection = {
                type: 'FeatureCollection',
                features: Object.entries(PREFECTURE_CENTERS).map(([name, coords]) => ({
                    type: 'Feature',
                    geometry: {
                        type: 'Point',
                        coordinates: coords,
                    },
                    properties: { name },
                })),
            };

            // 都道府県ラベル用ソースを追加
            map.current!.addSource('prefecture-label-points', {
                type: 'geojson',
                data: prefectureLabelPoints,
            });

            // 都道府県名ラベルレイヤー（中心点から1つだけ表示）
            map.current!.addLayer({
                id: 'prefecture-labels',
                type: 'symbol',
                source: 'prefecture-label-points',
                layout: {
                    'text-field': ['get', 'name'],
                    'text-font': ['Open Sans Regular', 'Arial Unicode MS Regular'],
                    'text-size': 14,
                    'text-anchor': 'center',
                    'text-offset': [0, 0],
                    'text-allow-overlap': false,  // ラベルの重複を許可しない
                    'text-optional': false,       // 常に表示を試みる
                    'symbol-avoid-edges': true,   // 画面端を避ける
                    'text-max-width': 10,         // ラベルの最大幅（em単位）
                    'text-padding': 2,            // ラベル周辺の余白
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
                'text-allow-overlap': false,      // ラベルの重複を許可しない
                'text-optional': true,            // スペースがない場合は省略
                'text-ignore-placement': false,   // 他のラベルとの配置を考慮
                'symbol-avoid-edges': true,       // 画面端を避ける
                'symbol-spacing': 200,            // 同じラベル間の最小距離（ピクセル）
                'text-max-width': 8,              // ラベルの最大幅（em単位）
                'text-padding': 2,                // ラベル周辺の余白
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

    // デバッグ: マップ全体のクリックイベントをログ
    useEffect(() => {
        if (!mapReady || !map.current) return;

        const handleMapClick = (e: any) => {
            console.log('🗺️ Map clicked at:', e.lngLat, 'viewLevel:', viewLevel);
            const features = map.current!.queryRenderedFeatures(e.point);
            console.log('📊 Features at click point:', features.map((f: any) => ({
                layer: f.layer.id,
                sourceLayer: f.sourceLayer,
                properties: f.properties
            })));
        };

        map.current.on('click', handleMapClick);

        return () => {
            if (map.current) {
                map.current.off('click', handleMapClick);
            }
        };
    }, [mapReady, viewLevel]);

    // クリック可能なポリゴン領域の設定（都道府県レイヤー）
    useEffect(() => {
        if (!mapReady || !map.current) return;
        if (!map.current.getLayer('prefecture-fill')) return;

        // 都道府県ポリゴンクリックイベント
        const handlePrefectureClick = (e: any) => {
            console.log('🖱️ Prefecture polygon clicked!', { viewLevel, event: e });
            if (!e.features || e.features.length === 0) {
                console.warn('❌ No features found in click event');
                return;
            }
            const prefectureName = e.features[0].properties.nam_ja;
            console.log('📍 Prefecture name:', prefectureName);
            if (!prefectureName) return;

            // Level 1（全国ビュー）では地方に遷移、Level 2（地方ビュー）では都道府県に遷移
            if (viewLevel === 'national') {
                // 全都道府県データから地方を検索
                const pref = allPrefecturesData.find(p => p.prefecture === prefectureName);
                console.log('🗺️ National view - Found prefecture:', pref);
                if (pref && pref.region) {
                    console.log('✅ Navigating to region:', pref.region);
                    onRegionClick(pref.region);
                }
            } else {
                // Level 2（地方ビュー）では通常通り都道府県詳細へ
                console.log('✅ Navigating to prefecture:', prefectureName);
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
    }, [mapReady, viewLevel, allPrefScores, allPrefecturesData, onPrefectureClick, onRegionClick]);

    // クリック可能なポリゴン領域の設定（自治体レイヤー）
    useEffect(() => {
        if (!mapReady || !map.current) return;
        if (!map.current.getLayer('municipality-fill')) return;

        // 自治体ポリゴンクリックイベント
        const handleMunicipalityClick = (e: any) => {
            console.log('🖱️ Municipality polygon clicked!', { viewLevel, event: e });
            if (!e.features || e.features.length === 0) {
                console.warn('❌ No features found in click event');
                return;
            }
            const cityCode = e.features[0].properties.N03_007;
            console.log('📍 City code:', cityCode);
            if (cityCode) {
                console.log('✅ Navigating to municipality:', cityCode);
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

        // デバッグ: 自治体データとGeoJSONデータの確認
        console.log('🔍 Municipality data sample:', municipalities.slice(0, 3).map(m => ({
            city_name: m.city_name,
            city_code: m.city_code,
            total_score: m.total_score
        })));

        // GeoJSONのN03_007サンプルを確認
        const features = municipalityGeoJson?.features?.slice(0, 3);
        console.log('🔍 GeoJSON N03_007 sample:', features?.map((f: any) => ({
            name: f.properties.N03_004,
            code: f.properties.N03_007
        })));

        // 自治体のcity_codeとスコアのマッピング（重複排除）
        const codeToColor: Map<string, string> = new Map();
        const scoreDebug: Array<{name: string, code: string, score: number, color: string}> = [];
        municipalities.forEach(muni => {
            const score = muni.total_score || 0;
            // city_codeを5桁に正規化
            // GeoJSONは5桁標準コード、APIは6桁（末尾にチェックディジット）
            const normalizedCode = muni.city_code.length === 6
                ? muni.city_code.substring(0, 5)  // 末尾1桁を削除して5桁に
                : muni.city_code;

            // 重複を排除（最初のエントリーのみ保持）
            if (!codeToColor.has(normalizedCode)) {
                const color = getScoreColor(score);
                codeToColor.set(normalizedCode, color);
                if (scoreDebug.length < 10) {
                    scoreDebug.push({
                        name: muni.city_name,
                        code: normalizedCode,
                        score,
                        color
                    });
                }
            }
        });

        console.log('📊 Score distribution (first 10):', scoreDebug);

        // MapLibre用のmatch式を構築
        const matchExpr: any[] = ['match', ['get', 'N03_007']];
        codeToColor.forEach((color, code) => {
            matchExpr.push(code, color);
        });
        matchExpr.push('#333333'); // デフォルト色（マッチしない場合）

        map.current.setPaintProperty('municipality-fill', 'fill-color', matchExpr);

        // 境界線もスコアに応じた色に
        if (map.current.getLayer('municipality-borders')) {
            map.current.setPaintProperty('municipality-borders', 'line-color', matchExpr);
        }

        console.log('✅ 自治体コロプレスマップ適用完了:', municipalities.length, '件');
        console.log('📊 Match expression length:', matchExpr.length, 'entries');
        console.log('🔍 First 10 match entries:', matchExpr.slice(3, 23));
    }, [mapReady, municipalities, municipalityGeoJson]);

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
                <div className="legend-title">DXスコア（Zoom導入適性）</div>
                <div className="legend-item">
                    <span className="legend-color" style={{ background: '#003D82' }}></span>
                    <span>48+ Zoom最適</span>
                </div>
                <div className="legend-item">
                    <span className="legend-color" style={{ background: '#0E71EB' }}></span>
                    <span>42-47 Zoom有望</span>
                </div>
                <div className="legend-item">
                    <span className="legend-color" style={{ background: '#89C4F4' }}></span>
                    <span>34-41 平均的</span>
                </div>
                <div className="legend-item">
                    <span className="legend-color" style={{ background: '#FFB84D' }}></span>
                    <span>22-33 要支援</span>
                </div>
                <div className="legend-item">
                    <span className="legend-color" style={{ background: '#F25022' }}></span>
                    <span>15-21 MS領域</span>
                </div>
                <div className="legend-item">
                    <span className="legend-color" style={{ background: '#D13438' }}></span>
                    <span>1-14 要改善</span>
                </div>
            </div>
        </div>
    );
}
