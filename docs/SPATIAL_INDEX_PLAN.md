# 空間インデックス導入計画 (Spatial Indexing Plan)

## 目的
MLIT-DPF、PLATEAU、gBizINFOという形式の異なるデータを「標準地域メッシュコード (JIS X 0410)」を共通キーとして統合・分析可能にする。

## アーキテクチャ変更

### 1. 共通結合キー: 標準地域メッシュ (Standard Grid Square)
- **採用規格**: 3次メッシュ (約1km四方) または 4次メッシュ (約500m四方)
  - 都市部の分析には4次メッシュ(500m)または5次(250m)が望ましいが、データ量とのバランスで決定。まず3次/4次で実装。
- **H3インデックス**: オプション検討(六角形グリッド)。今回は正規化のしやすさからJISメッシュを優先。

### 2. データソースごとの正規化フロー

| データソース | 元のキー/位置情報 | 正規化処理 (Normalization) | 格納カラム |
|--------------|-------------------|----------------------------|------------|
| **gBizINFO** | 住所文字列 | **Geocoding** -> 緯度経度 -> **Mesh Code** | `lat`, `lon`, `mesh_code` |
| **PLATEAU** | CityGML (3Dモデル) | 中心点/重心 -> **Mesh Code** | `center_lat`, `center_lon`, `mesh_code` |
| **MLIT-DPF** | 座標/行政区画 | 座標 -> **Mesh Code** | `lat`, `lon`, `mesh_code` |
| **e-Stat** | 市区町村コード | (粗い粒度だが) メッシュ集計値を自治体に紐付け | `municipality_code` |

### 3. Geocoding戦略
- **ライブラリ**: `jageocoder` (Python)
  - 特徴: 高速、オフライン、辞書ベース。住所→座標変換に最適。
  - **課題**: 辞書ファイル(数GB)のダウンロードが必要。Dockerイメージサイズへの影響。
  - **代替案**: 国土地理院API (レートリミット厳格), Google Maps API (有料)。`jageocoder`を最優先。

### 4. DBスキーマ変更

#### `meshes` テーブル (新規)
メッシュそのものを管理するマスタ。
- `code` (PK, VARCHAR): メッシュコード
- `lat` (FLOAT): 中心緯度
- `lon` (FLOAT): 中心経度
- `municipality_code` (FK): 代表市区町村コード

#### `companies` テーブル (gBizINFO用, 新規)
- `corporate_number` (PK)
- `name`
- `address`
- `lat`, `lon`
- `mesh_code` (INDEX)
- `cert_flags` (JSONB): DX認定等のフラグ

#### `buildings` テーブル (PLATEAU用, 新規)
- `id` (PK)
- `mesh_code` (INDEX)
- `height`
- `structure`
- `year_built`

## 実装ステップ

1.  **Environment Setup**: `jageocoder` と辞書のインストール。
    - ✅ `jageocoder` (2.x) インストール完了
    - ⚠️ 辞書 (jukyo_all_v21.zip) のダウンロードは完了したが、DB読み込み時に `sqlite3.OperationalError` が発生中。
    - 🔄 **Workaround**: `utils/spatial.py` にMock Geocoder (札幌中心部) を実装済み。

2.  **Schema Update**: `meshes`, `companies`, `buildings` テーブル作成。
    - ✅ `backend/scripts/update_schema_spatial.py` により完了。

3.  **Utility Implementation**: `utils/spatial.py` 作成。
    - ✅ `lat_lon_to_mesh(lat, lon, level)` 実装済み (JIS X 0410)
    - ✅ `geocode_address(address)` 実装済み (jageocoderラップ + Mock Fallback)

4.  **ETL Updates**:
    - **gBizINFO**:
        - ⚠️ API (`/hojin`) が `address` 検索で500エラーを返す。詳細検索(`name`)も動作が不安定。
        - ✅ Mockデータ (札幌市役所、北海道大学など) を用いて、DBへの格納とメッシュ紐付けを実証 (`import_gbizinfo_data.py`)。
    - **PLATEAU**:
        - API (`import_plateau_data.py`) でメタデータ(URL)取得まで完了。
        - 次フェーズで実際のCityGMLパースとデータ格納を行う。

## 今後の課題
- **jageocoder辞書の修復**: コンテナ再構築またはボリュームのクリーンアップ後に再インストールが必要かもしれない。
- **gBizINFO API**: 安定しないため、全件CSVダウンロードによるインポートへの切り替えを推奨。
