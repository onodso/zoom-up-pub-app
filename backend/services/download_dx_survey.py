"""
DX Survey Data Downloader
デジタル庁「自治体DXの取組に関するダッシュボード」のオープンデータを収集・インポート

Data Source:
https://www.digital.go.jp/resources/govdashboard/local-government-dx
"""

import httpx
import pandas as pd
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.extras import Json
import io
import zipfile
import json
from datetime import datetime

class DXSurveyDownloader:
    # デジタル庁 自治体DXダッシュボード データテーブル
    # 2024年7月12日更新版
    DATA_URL = "https://www.digital.go.jp/assets/contents/node/basic_page/field_ref_resources/51a5a201-e0dd-493f-9c21-0692402d93e6/85162d87/20240712_resources_govdashboard_local_governmentdx_table_01.zip"

    def __init__(self):
        self.client = httpx.Client(timeout=120.0, follow_redirects=True)
        self.conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            user=os.getenv("POSTGRES_USER", "zoom_admin"),
            password=os.getenv("POSTGRES_PASSWORD", "password"),
            dbname=os.getenv("POSTGRES_DB", "zoom_dx_db")
        )
        self.cur = self.conn.cursor(cursor_factory=RealDictCursor)

    def download_and_extract(self):
        """ZIPファイルをダウンロードして中のCSV/Excelを読み込む"""
        print(f"Downloading data from: {self.DATA_URL}")
        try:
            response = self.client.get(self.DATA_URL)
            response.raise_for_status()
            print(f"✅ Downloaded {len(response.content):,} bytes")

            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                print(f"Archive contains: {z.namelist()}")
                
                # 拡張子が.csvまたは.xlsxのファイルを探す
                target_file = None
                for filename in z.namelist():
                    if filename.endswith('.csv') or filename.endswith('.xlsx'):
                        target_file = filename
                        break
                
                if not target_file:
                    print("❌ No CSV or Excel file found in archive")
                    return None

                print(f"Processing file: {target_file}")
                
                with z.open(target_file) as f:
                    if target_file.endswith('.csv'):
                        # Shift-JIS or UTF-8 check might be needed
                        # デジタル庁データはShift-JISの可能性が高いが、pd.read_csvで自動検知を試みる
                        try:
                            df = pd.read_csv(f, encoding='shift_jis')
                        except UnicodeDecodeError:
                            f.seek(0)
                            df = pd.read_csv(f, encoding='utf-8')
                    else:
                        df = pd.read_excel(f)
                    
                    return df

        except Exception as e:
            print(f"❌ Error downloading/extracting data: {e}")
            import traceback
            traceback.print_exc()
            return None

    def inspect_data(self, df):
        """データの構造を確認して表示する"""
        if df is None:
            return

        print("\n📊 Data Inspection:")
        print(f"Rows: {len(df)}")
        print(f"Columns: {len(df.columns)}")
        print("\nColumn Names:")
        for i, col in enumerate(df.columns):
            print(f"{i}: {col}")
        
        print("\nFirst 3 rows:")
        print(df.head(3))

    def import_data(self, df):
        """データをmunicipalitiesテーブルのdx_statusカラムにインポート"""
        if df is None:
            return

        print("\n🚀 Starting Data Import...")
        print("Transforming data structure (Pivot)...")
        
        # 1. 項目名（ヘッダー）を作成
        # Unnamed: 0 (カテゴリー) と Unnamed: 1 (項目名) を結合
        headers = []
        for idx, row in df.iterrows():
            category = str(row.iloc[0]).replace('\n', '') if pd.notna(row.iloc[0]) else ""
            item = str(row.iloc[1]).replace('\n', '') if pd.notna(row.iloc[1]) else ""
            # カテゴリが空の場合は前行の値を埋める処理が必要かもしれないが、
            # 現状のデータを見ると全ての行に入っているか、あるいはカテゴリだけ独立した行ではないようだった。
            # シンプルに結合する
            if category == item:
                headers.append(item)
            else:
                headers.append(f"{category}_{item}")

        # 2. 転置処理
        # データ部分：3列目以降（インデックス2以降）
        # 行：項目、列：自治体
        # これを -> 行：自治体、列：項目 に転置
        
        try:
            # データのDataFrame（自治体列のみ）
            data_df = df.iloc[:, 2:]
            
            # 転置
            df_T = data_df.T
            
            # カラム名を設定
            # headersの長さとdf_Tの列数が一致することを確認
            if len(headers) != len(df_T.columns):
                print(f"⚠️ Header mismatch: Headers={len(headers)}, DataCols={len(df_T.columns)}")
                # 強引に合わせるかエラーにするか。一旦スライスで合わせる
                df_T.columns = headers[:len(df_T.columns)]
            else:
                df_T.columns = headers
            
            print(f"Transformed DataFrame: {len(df_T)} municipalities x {len(df_T.columns)} items")
            
        except Exception as e:
            print(f"❌ Error during data transformation: {e}")
            import traceback
            traceback.print_exc()
            return

        success_count = 0
        skip_count = 0
        
        # 3. インポート実行
        for city_name, row in df_T.iterrows():
            # インデックスが自治体名になっている
            if pd.isna(city_name) or str(city_name).startswith('Unnamed'):
                continue
            
            try:
                # データのNaNをNoneに変換
                dx_data = row.where(pd.notnull(row), None).to_dict()
                
                # DB更新
                # 自治体名の正規化（スペース削除）
                city_name_str = str(city_name)
                city_name_normalized = city_name_str.replace(' ', '').replace('　', '')
                
                self.cur.execute("""
                    UPDATE municipalities 
                    SET dx_status = %s, updated_at = NOW()
                    WHERE REPLACE(REPLACE(city_name, ' ', ''), '　', '') = %s
                    RETURNING city_code;
                """, (Json(dx_data), city_name_normalized))
                
                if self.cur.fetchone():
                    success_count += 1
                else:
                    # DBに存在しない自治体（合併前や名称不一致など）
                    # print(f"Skipped (not found): {city_name_normalized}")
                    skip_count += 1
                    
            except Exception as e:
                print(f"Error importing {city_name}: {e}")
                self.conn.rollback()
                skip_count += 1
            
            # 進捗表示
            if (success_count + skip_count) % 100 == 0:
                self.conn.commit()
                print(f"Processed {success_count + skip_count} / {len(df_T)} municipalities... (Success: {success_count})")

        self.conn.commit()
        print(f"\n✅ Import Completed!")
        print(f"Updated: {success_count}")
        print(f"Skipped: {skip_count}")

    def close(self):
        self.cur.close()
        self.conn.close()
        self.client.close()

if __name__ == "__main__":
    downloader = DXSurveyDownloader()
    try:
        df = downloader.download_and_extract()
        if df is not None:
            # downloader.inspect_data(df)
            
            # インポート実行
            downloader.import_data(df)
            
            # 結果確認
            downloader.cur.execute("SELECT COUNT(dx_status) FROM municipalities;")
            res = downloader.cur.fetchone()
            count = res['count'] if res else 0
            print(f"\n📊 Total municipalities with DX data: {count}")
            
    finally:
        downloader.close()
