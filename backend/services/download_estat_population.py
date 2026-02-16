"""
e-Stat Population Data Downloader
総務省統計局から令和2年国勢調査の市区町村別人口データを自動ダウンロード

データソース: e-Stat 政府統計の総合窓口
対象: 全国市区町村別人口・世帯数
"""

import httpx
import pandas as pd
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import zipfile
import io
from pathlib import Path


class EStatPopulationDownloader:
    """e-Statから人口データをダウンロードしてインポート"""

    # e-Stat 令和2年国勢調査 都道府県・市区町村別人口・世帯数
    # このURLは公開されているExcelファイルの直接ダウンロードリンク
    ESTAT_POPULATION_URL = "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000032143614&fileKind=0"

    def __init__(self):
        self.client = httpx.Client(timeout=60.0, follow_redirects=True)

        # データベース接続
        self.conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            user=os.getenv("POSTGRES_USER", "zoom_admin"),
            password=os.getenv("POSTGRES_PASSWORD", "password"),
            dbname=os.getenv("POSTGRES_DB", "zoom_dx_db")
        )
        self.cur = self.conn.cursor(cursor_factory=RealDictCursor)

    def download_excel_data(self) -> pd.DataFrame:
        """
        e-StatからExcelデータをダウンロード

        Returns:
            DataFrame with columns: city_code, city_name, population, households
        """
        print("=" * 80)
        print("e-Stat Population Data Download")
        print("=" * 80)
        print(f"Downloading from e-Stat...")
        print(f"URL: {self.ESTAT_POPULATION_URL}")
        print()

        try:
            # Excelファイルをダウンロード
            response = self.client.get(self.ESTAT_POPULATION_URL)
            response.raise_for_status()

            print(f"✅ Downloaded: {len(response.content):,} bytes")
            print(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
            print()

            # Excelファイルとして読み込み
            # e-StatのExcelは8行目がヘッダー、9行目からデータ
            df = pd.read_excel(io.BytesIO(response.content), sheet_name=0, header=8)

            print(f"✅ Loaded DataFrame: {len(df)} rows × {len(df.columns)} columns")
            print(f"Columns: {list(df.columns)[:5]}")
            print()

            return df

        except httpx.HTTPStatusError as e:
            print(f"❌ Download failed: HTTP {e.response.status_code}")
            print(f"Response: {e.response.text[:500]}")
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return None

    def parse_and_import(self, df: pd.DataFrame):
        """
        DataFrameをパースしてデータベースに保存

        Args:
            df: e-Statから取得したDataFrame
        """
        if df is None or df.empty:
            print("❌ No data to import")
            return

        print("=" * 80)
        print("Parsing and importing data...")
        print("=" * 80)
        print()

        # e-Stat Excelのカラム構造（固定）
        # カラム0: 都道府県名
        # カラム1: 都道府県・市区町村名（形式: "コード_名前"）
        # カラム4: 総人口

        print(f"DataFrame columns: {list(df.columns[:10])}")
        print()

        success_count = 0
        fail_count = 0

        for idx, row in df.iterrows():
            try:
                # カラム1から市区町村コードと名前を抽出
                # 形式: "01100_札幌市" または "00000_全国"
                city_info = str(row.iloc[1])  # カラム1

                if '_' not in city_info:
                    continue  # フォーマットが違う行はスキップ

                city_code_raw, city_name = city_info.split('_', 1)

                # 数字のみ抽出
                city_code = ''.join(filter(str.isdigit, city_code_raw))

                if len(city_code) < 5:
                    continue  # 全国・都道府県レベルはスキップ

                city_code = city_code.zfill(6)  # 6桁に統一

                # 人口を取得（カラム4）
                population = row.iloc[4]  # カラム4: 総人口

                if pd.isna(population):
                    continue

                population = int(population)

                # 世帯数は推定（e-Statの人口データには含まれていない）
                households = int(population * 0.4)  # 平均世帯人数2.5人で推定

                # 市区町村名を正規化（スペースを削除）
                city_name_normalized = city_name.replace(' ', '').replace('　', '')

                # データベース更新（市区町村名でマッチング）
                # e-Statのコードとデータベースのコードが異なるため、名前でマッチング
                self.cur.execute("""
                    UPDATE municipalities
                    SET population = %s,
                        households = %s,
                        updated_at = NOW()
                    WHERE REPLACE(REPLACE(city_name, ' ', ''), '　', '') = %s
                    RETURNING city_name, city_code;
                """, (population, households, city_name_normalized))

                result = self.cur.fetchone()
                if result:
                    print(f"✅ {result['city_name']:20} : 人口 {population:>10,}, 世帯 {households:>10,}")
                    success_count += 1
                else:
                    # データベースにない市区町村（廃止済みなど）
                    fail_count += 1

            except Exception as e:
                fail_count += 1
                continue

            # 100件ごとにコミット
            if (success_count + fail_count) % 100 == 0:
                self.conn.commit()
                print(f"\n💾 Committed {success_count + fail_count} records\n")

        # 最終コミット
        self.conn.commit()

        print()
        print("=" * 80)
        print(f"✅ Success: {success_count:,} municipalities updated")
        print(f"⚠️  Skipped: {fail_count:,} (not in database or invalid)")
        print(f"💰 Cost: 0円 (e-Stat public data)")
        print("=" * 80)

    def get_current_status(self):
        """現在のデータベース状況を表示"""
        self.cur.execute("""
            SELECT
                COUNT(*) as total,
                COUNT(population) as with_pop,
                COUNT(CASE WHEN population IS NULL THEN 1 END) as null_pop,
                ROUND(AVG(population), 0) as avg_pop
            FROM municipalities;
        """)

        status = self.cur.fetchone()

        print("\n📊 Current Database Status:")
        print(f"   Total municipalities: {status['total']:,}")
        print(f"   With population data: {status['with_pop']:,}")
        print(f"   NULL population:      {status['null_pop']:,}")
        if status['avg_pop']:
            print(f"   Average population:   {int(status['avg_pop']):,}")
        print()

    def close(self):
        self.cur.close()
        self.conn.close()
        self.client.close()


def main():
    """メイン実行"""
    downloader = EStatPopulationDownloader()

    try:
        # 実行前の状況
        print("\n🔍 Before import:")
        downloader.get_current_status()

        # データダウンロード
        df = downloader.download_excel_data()

        if df is not None:
            # データインポート
            downloader.parse_and_import(df)

            # 実行後の状況
            print("\n🔍 After import:")
            downloader.get_current_status()

            print("\n✅ Data collection complete!")
            print("Next step: Check data completeness and proceed to DX survey import")
        else:
            print("\n❌ Failed to download data from e-Stat")
            print("\nAlternative: Manual download")
            print("1. Visit: https://www.e-stat.go.jp/stat-search/files?stat_infid=000032143614")
            print("2. Download Excel file")
            print("3. Use estat_csv_importer.py to import")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        downloader.close()


if __name__ == "__main__":
    main()
