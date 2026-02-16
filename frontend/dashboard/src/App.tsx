// メインアプリケーション - ドリルダウン型地図ダッシュボード
import { useState, useEffect, useCallback } from 'react';
import MapView from './components/MapView';
import SidePanel from './components/SidePanel';
import Breadcrumb from './components/Breadcrumb';
import StatsBar from './components/StatsBar';
import type {
  ViewLevel,
  RegionData,
  PrefectureData,
  MunicipalityData,
  MunicipalityDetail,
  StatsData,
} from './api/mapApi';
import {
  fetchRegions,
  fetchPrefectures,
  fetchMunicipalities,
  fetchMunicipalityDetail,
  fetchStats,
} from './api/mapApi';
import './App.css';

function App() {
  // ドリルダウンの状態管理
  const [viewLevel, setViewLevel] = useState<ViewLevel>('national');
  const [selectedRegion, setSelectedRegion] = useState<string | null>(null);
  const [selectedPrefecture, setSelectedPrefecture] = useState<string | null>(null);
  const [selectedMunicipality, setSelectedMunicipality] = useState<MunicipalityDetail | null>(null);

  // データ
  const [regions, setRegions] = useState<RegionData[]>([]);
  const [prefectures, setPrefectures] = useState<PrefectureData[]>([]);
  const [municipalities, setMunicipalities] = useState<MunicipalityData[]>([]);
  const [stats, setStats] = useState<StatsData | null>(null);

  // UI状態
  const [sidePanelOpen, setSidePanelOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 初期データ読み込み
  useEffect(() => {
    const loadInitial = async () => {
      setLoading(true);
      setError(null);
      try {
        const [regionsData, statsData] = await Promise.all([
          fetchRegions(),
          fetchStats(),
        ]);
        setRegions(regionsData);
        setStats(statsData);
      } catch (err) {
        console.error('初期データ読み込みエラー:', err);
        setError('データの読み込みに失敗しました。APIサーバーが起動しているか確認してください。');
      }
      setLoading(false);
    };
    loadInitial();
  }, []);

  // 地方クリック → 都道府県ビュー
  const handleRegionClick = useCallback(async (regionName: string) => {
    setLoading(true);
    try {
      const prefsData = await fetchPrefectures(regionName);
      setPrefectures(prefsData);
      setSelectedRegion(regionName);
      setViewLevel('region');
    } catch (err) {
      console.error('都道府県データ読み込みエラー:', err);
    }
    setLoading(false);
  }, []);

  // 都道府県クリック → 自治体ビュー
  const handlePrefectureClick = useCallback(async (prefectureName: string) => {
    setLoading(true);
    try {
      const munisData = await fetchMunicipalities(prefectureName);
      setMunicipalities(munisData);
      setSelectedPrefecture(prefectureName);
      setViewLevel('prefecture');
    } catch (err) {
      console.error('自治体データ読み込みエラー:', err);
    }
    setLoading(false);
  }, []);

  // 自治体クリック → 詳細パネル表示
  const handleMunicipalityClick = useCallback(async (cityCode: string) => {
    setLoading(true);
    try {
      const detail = await fetchMunicipalityDetail(cityCode);
      setSelectedMunicipality(detail);
      setSidePanelOpen(true);
      setViewLevel('municipality');
    } catch (err) {
      console.error('自治体詳細読み込みエラー:', err);
    }
    setLoading(false);
  }, []);

  // パンくずナビでの戻り操作
  const handleNavigateToNational = useCallback(() => {
    setViewLevel('national');
    setSelectedRegion(null);
    setSelectedPrefecture(null);
    setSelectedMunicipality(null);
    setSidePanelOpen(false);
  }, []);

  const handleNavigateToRegion = useCallback((regionName: string) => {
    handleRegionClick(regionName);
    setSelectedPrefecture(null);
    setSelectedMunicipality(null);
    setSidePanelOpen(false);
  }, [handleRegionClick]);

  const handleNavigateToPrefecture = useCallback((prefectureName: string) => {
    handlePrefectureClick(prefectureName);
    setSelectedMunicipality(null);
    setSidePanelOpen(false);
  }, [handlePrefectureClick]);

  return (
    <div className="app">
      {/* ヘッダー */}
      <header className="app-header">
        <div className="header-title">
          <h1>🗾 自治体DX推進状況ダッシュボード</h1>
          <span className="header-subtitle">
            全{stats?.total_municipalities || '...'}自治体のDXスコアを可視化
          </span>
        </div>
        {stats && <StatsBar stats={stats} />}
      </header>

      {/* パンくずナビ */}
      <Breadcrumb
        viewLevel={viewLevel}
        selectedRegion={selectedRegion}
        selectedPrefecture={selectedPrefecture}
        selectedMunicipality={selectedMunicipality?.city_name || null}
        onNavigateNational={handleNavigateToNational}
        onNavigateRegion={handleNavigateToRegion}
        onNavigatePrefecture={handleNavigateToPrefecture}
      />

      {/* メインコンテンツ */}
      <main className="app-main">
        {/* 地図 */}
        <div className={`map-container ${sidePanelOpen ? 'with-panel' : ''}`}>
          {loading && <div className="loading-overlay"><div className="spinner" /></div>}
          {error && (
            <div className="error-overlay">
              <div className="error-message">
                <span className="error-icon">⚠️</span>
                <p>{error}</p>
                <button onClick={() => window.location.reload()}>再読み込み</button>
              </div>
            </div>
          )}
          <MapView
            viewLevel={viewLevel}
            regions={regions}
            prefectures={prefectures}
            municipalities={municipalities}
            selectedRegion={selectedRegion}
            onRegionClick={handleRegionClick}
            onPrefectureClick={handlePrefectureClick}
            onMunicipalityClick={handleMunicipalityClick}
          />
        </div>

        {/* サイドパネル */}
        {sidePanelOpen && selectedMunicipality && (
          <SidePanel
            municipality={selectedMunicipality}
            onClose={() => {
              setSidePanelOpen(false);
              setViewLevel('prefecture');
            }}
          />
        )}
      </main>
    </div>
  );
}

export default App;
