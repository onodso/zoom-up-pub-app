// パンくずナビゲーション
// 日本全国 > 関東地方 > 東京都 > 渋谷区
import type { ViewLevel } from '../api/mapApi';

interface Props {
    viewLevel: ViewLevel;
    selectedRegion: string | null;
    selectedPrefecture: string | null;
    selectedMunicipality: string | null;
    onNavigateNational: () => void;
    onNavigateRegion: (region: string) => void;
    onNavigatePrefecture: (prefecture: string) => void;
}

export default function Breadcrumb({
    viewLevel,
    selectedRegion,
    selectedPrefecture,
    selectedMunicipality,
    onNavigateNational,
    onNavigateRegion,
    onNavigatePrefecture,
}: Props) {
    return (
        <nav className="breadcrumb">
            <span
                className={`crumb ${viewLevel === 'national' ? 'active' : 'clickable'}`}
                onClick={onNavigateNational}
            >
                🗾 日本全国
            </span>

            {selectedRegion && (
                <>
                    <span className="separator">›</span>
                    <span
                        className={`crumb ${viewLevel === 'region' ? 'active' : 'clickable'}`}
                        onClick={() => onNavigateRegion(selectedRegion)}
                    >
                        {selectedRegion}
                    </span>
                </>
            )}

            {selectedPrefecture && (
                <>
                    <span className="separator">›</span>
                    <span
                        className={`crumb ${viewLevel === 'prefecture' ? 'active' : 'clickable'}`}
                        onClick={() => onNavigatePrefecture(selectedPrefecture)}
                    >
                        {selectedPrefecture}
                    </span>
                </>
            )}

            {selectedMunicipality && viewLevel === 'municipality' && (
                <>
                    <span className="separator">›</span>
                    <span className="crumb active">{selectedMunicipality}</span>
                </>
            )}
        </nav>
    );
}
