"""
GIGA School Data Downloader
文部科学省「学校における教育の情報化の実態等に関する調査（令和5年度）」データを収集

Data Source: e-Stat
https://www.e-stat.go.jp/stat-search/files?statInfId=000040221910&fileKind=0
"""

import httpx
import pandas as pd
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import io
import time

import zipfile
import io

class GigaDataDownloader:
    # e-Stat 令和5年度教育情報化調査 47都道府県別Excel URLリスト
    PREFECTURE_URLS = [
        {"title": "01 北海道", "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040221906&fileKind=0"},
        {"title": "02 青森県", "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040221907&fileKind=0"},
        {"title": "03 岩手県", "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040221908&fileKind=0"},
        {"title": "04 宮城県", "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040221909&fileKind=0"},
        {"title": "05 秋田県", "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040221910&fileKind=0"},
        {"title": "06 山形県", "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040221911&fileKind=0"},
        {"title": "07 福島県", "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040221912&fileKind=0"},
        {"title": "08 茨城県", "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040221913&fileKind=0"},
        {"title": "09 栃木県", "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040221914&fileKind=0"},
        {"title": "10 群馬県", "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040221915&fileKind=0"},
        {"title": "11 埼玉県", "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040221916&fileKind=0"},
        {"title": "12 千葉県", "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040221917&fileKind=0"},
        {"title": "13 東京都", "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040221918&fileKind=0"},
        {"title": "14 神奈川県", "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040221919&fileKind=0"},
        {"title": "15 新潟県", "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040221920&fileKind=0"},
        {"title": "16 富山県", "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040221921&fileKind=0"},
        {"title": "17 石川県", "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040221922&fileKind=0"},
        {"title": "18 福井県", "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040221923&fileKind=0"},
        {"title": "19 山梨県", "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040221924&fileKind=0"},
        {"title": "20 長野県", "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040221925&fileKind=0"},
        {"title": "21 岐阜県", "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040221926&fileKind=0"},
        {"title": "22 静岡県", "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040221927&fileKind=0"},
        {"title": "23 愛知県", "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040221928&fileKind=0"},
        {"title": "24 三重県", "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040221929&fileKind=0"},
        {"title": "25 滋賀県", "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040221930&fileKind=0"},
        {"title": "26 京都府", "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040221931&fileKind=0"},
        {"title": "27 大阪府", "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040221932&fileKind=0"},
        {"title": "28 兵庫県", "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040221933&fileKind=0"},
        {"title": "29 奈良県", "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040221934&fileKind=0"},
        {"title": "30 和歌山県", "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040221935&fileKind=0"},
        {"title": "31 鳥取県", "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040221936&fileKind=0"},
        {"title": "32 島根県", "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040221937&fileKind=0"},
        {"title": "33 岡山県", "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040221938&fileKind=0"},
        {"title": "34 広島県", "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040221939&fileKind=0"},
        {"title": "35 山口県", "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040221940&fileKind=0"},
        {"title": "36 徳島県", "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040221941&fileKind=0"},
        {"title": "37 香川県", "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040221942&fileKind=0"},
        {"title": "38 愛媛県", "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040221943&fileKind=0"},
        {"title": "39 高知県", "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040221944&fileKind=0"},
        {"title": "40 福岡県", "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040221945&fileKind=0"},
        {"title": "41 佐賀県", "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040221946&fileKind=0"},
        {"title": "42 長崎県", "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040221947&fileKind=0"},
        {"title": "43 熊本県", "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040221948&fileKind=0"},
        {"title": "44 大分県", "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040221949&fileKind=0"},
        {"title": "45 宮崎県", "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040221950&fileKind=0"},
        {"title": "46 鹿児島県", "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040221951&fileKind=0"},
        {"title": "47 沖縄県", "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040221952&fileKind=0"}
    ]

    def __init__(self):
        self.client = httpx.Client(timeout=30.0, follow_redirects=True)
        self.conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            user=os.getenv("POSTGRES_USER", "zoom_admin"),
            password=os.getenv("POSTGRES_PASSWORD", "password"),
            dbname=os.getenv("POSTGRES_DB", "zoom_dx_db")
        )
        self.cur = self.conn.cursor(cursor_factory=RealDictCursor)

    def download_and_import_all(self):
        """全47都道府県のデータを処理"""
        total = len(self.PREFECTURE_URLS)
        print(f"🚀 Starting Import for {total} prefectures...")
        
        success_total = 0
        error_total = 0
        
        for i, item in enumerate(self.PREFECTURE_URLS):
            title = item['title']
            url = item['url']
            print(f"\n[{i+1}/{total}] Processing {title}...")
            
            try:
                time.sleep(1) # E-Statへの負荷軽減
                response = self.client.get(url)
                response.raise_for_status()
                
                # Header=Noneで読み込む
                df = pd.read_excel(io.BytesIO(response.content), sheet_name=0, header=None)
                
                # デバッグ検査 (最初の1件のみ)
                # if i == 0:
                #    self.inspect_data(df)

                # インポート実行
                count = self.import_data(df)
                success_total += count
                
            except Exception as e:
                print(f"❌ Failed to process {title}: {e}")
                error_total += 1
                # traceback.print_exc()
        
        print(f"\n🎉 All Done! Total Success Records: {success_total}, Errors (Prefectures): {error_total}")

    def import_data(self, df):
        """データを解析してインポート (Returns: processed count)"""
        # マッピング用辞書 (これをキャッシュしても良いが、件数少ないので都度呼ぶか、__init__で呼ぶか)
        # 毎回呼ぶとDB負荷になるので、__init__でロード済みにしておくのがベターだが、
        # ここでは簡易にself.curを使う
        
        # ヘッダー検索ロジック (既存)
        # ... (中略) ...
        # return success_count を追加する必要がある
        return self._process_dataframe(df)

    def _process_dataframe(self, df):
        # 既存のimport_dataのロジックをここに移動
        # 戻り値として success_count を返す
        
        # マッピング用辞書作成
        city_map = self.get_city_code_map() # 毎回これ呼ぶのは無駄だが、一旦そのまま
        
        # ヘッダー行を検索
        header_row_idx = -1
        # 令和5年度調査のヘッダーキーワード
        target_keywords = ['市区町村別', '学習者用PC総台数', '児童生徒数']
        
        for i in range(20):
            row_vals = [str(x) for x in df.iloc[i].tolist()]
            row_str = "".join(row_vals)
            if all(k in row_str for k in target_keywords):
                header_row_idx = i
                break
        
        if header_row_idx == -1:
            print("❌ Header row not found in this file.")
            return 0

        header_row = df.iloc[header_row_idx]
        col_indices = {}
        
        target_cols_map = {
            '市区町村別': 'municipality',
            '児童生徒数': 'students',
            '学習者用PC総台数': 'learner_pcs',
            '児童生徒一人当たりの学習者用PC台数': 'pc_per_student',
        }
        
        for i in range(len(header_row)):
            val = header_row[i]
            if pd.notna(val):
                s = str(val).replace('\n', '').replace(' ', '').replace('　', '')
                for t_key, t_orig in target_cols_map.items():
                    if t_key in s:
                        col_indices[t_orig] = i
        
        # 都道府県・市区町村列
        pref_col_idx = -1
        city_col_idx = -1
        
        for i in range(header_row_idx):
            row_vals = [str(x) for x in df.iloc[i].tolist()]
            for j, val in enumerate(row_vals):
                if '都道府県名' in val:
                    pref_col_idx = j
                if '市区町村名' in val:
                    city_col_idx = j
        
        if pref_col_idx == -1: pref_col_idx = 1
        # Municipality col index might be determined by 'municipality' key if found
        if 'municipality' in col_indices:
            city_col_idx = col_indices['municipality']
        
        if city_col_idx == -1: city_col_idx = 2

        success_count = 0
        start_row = header_row_idx + 1
        
        current_pref = None
        # 都道府県名のセット (判定用)
        all_prefs = set(k[0] for k in city_map.keys())

        for i in range(start_row, len(df)):
            row = df.iloc[i]
            # 市区町村列(または名前列)の値
            name_val = row[city_col_idx]
            if pd.isna(name_val):
                continue
            
            name = str(name_val).replace(' ', '').replace('　', '')
            if name == 'nan' or '平均' in name or '合計' in name:
                continue
            
            # 都道府県名かどうか判定
            if name in all_prefs:
                current_pref = name
                continue # 都道府県行はスキップ
            
            # 現在の都道府県が未設定で、かつ名前が都道府県っぽい場合(フォールバック)
            if current_pref is None and (name.endswith('都') or name.endswith('道') or name.endswith('府') or name.endswith('県')):
                 current_pref = name
                 continue

            if current_pref is None:
                continue

            city_code = city_map.get((current_pref, name))
            if not city_code:
                 city_normalized = name.replace('ヶ', 'ケ')
                 city_code = city_map.get((current_pref, city_normalized))
            
            if not city_code:
                # ログを出して確認したいが、大量に出るので控えるか、エラーカウントに含める
                # print(f"  Mapping failed: {current_pref} {name}")
                continue
                
            # OS Type -> Unknown
            os_type = 'Unknown'
            
            # Student per PC
            # Computers per Student
            computer_per_student = None
            if 'pc_per_student' in col_indices:
                # 既存のカラム(端末/生徒)がある場合
                val = row[col_indices['pc_per_student']]
                try:
                    computer_per_student = float(str(val).replace(',', ''))
                except:
                    pass
            
            if computer_per_student is None and 'students' in col_indices and 'learner_pcs' in col_indices:
                 try:
                     s_val = float(str(row[col_indices['students']]).replace(',', ''))
                     p_val = float(str(row[col_indices['learner_pcs']]).replace(',', ''))
                     if s_val > 0 and p_val > 0:
                         # 修正: PC台数 / 生徒数 (1人あたりの端末数)
                         computer_per_student = p_val / s_val
                 except:
                     pass

            try:
                self.cur.execute("""
                    INSERT INTO education_info (city_code, terminal_os_type, computer_per_student, survey_year, updated_at)
                    VALUES (%s, %s, %s, 2023, NOW())
                    ON CONFLICT (city_code) DO UPDATE SET
                        terminal_os_type = EXCLUDED.terminal_os_type,
                        computer_per_student = EXCLUDED.computer_per_student,
                        updated_at = NOW();
                """, (city_code, os_type, computer_per_student))
                success_count += 1
            except Exception as e:
                print(f"❌ DB Error for {city}: {e}")
                self.conn.rollback()
        
        self.conn.commit()
        print(f"  -> Imported {success_count} records")
        return success_count

    def inspect_data(self, df):
        """データ構造を確認"""
        if df is None:
            return

        print("\n📊 Data Inspection:")
        print(f"Rows: {len(df)}")
        print(f"Columns: {len(df.columns)}")
        
        # 省略せずに表示
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)

        print("\n--- First 30 rows (Raw) ---")
        print(df.head(30).to_string())
        
        print("-" * 60)

    def get_city_code_map(self):
        """自治体名からcity_codeへのマッピングを作成"""
        self.cur.execute("SELECT city_code, prefecture, city_name FROM municipalities")
        results = self.cur.fetchall()
        
        # (都道府県, 市区町村) -> city_code
        mapping = {}
        for r in results:
            key = (r['prefecture'], r['city_name'])
            mapping[key] = r['city_code']
        return mapping

    def determine_os_type(self, row, cols):
        """OSごとの台数から主要OSを判定"""
        os_counts = {
            'Chromebook': row.get(cols.get('Chrome OS端末', -1), 0),
            'Windows': row.get(cols.get('Windows端末', -1), 0),
            'iOS': row.get(cols.get('iPadOS端末', -1), 0),
            'macOS': row.get(cols.get('macOS端末', -1), 0),
            'Android': row.get(cols.get('Android端末', -1), 0),
        }
        
        # 数値に変換（NaNや文字列を除去）
        valid_counts = {}
        total = 0
        for os_name, val in os_counts.items():
            try:
                # 整備済み端末のうちの台数なので、ここには数値が入るはず
                # ただし'***'や'-'が入る可能性がある
                if isinstance(val, (int, float)) and not pd.isna(val):
                   count = int(val)
                elif isinstance(val, str) and val.isnumeric():
                   count = int(val)
                else:
                   count = 0
                
                valid_counts[os_name] = count
                total += count
            except:
                pass
        
        if total == 0:
            return None

        # 最大のOSを探す
        sorted_os = sorted(valid_counts.items(), key=lambda x: x[1], reverse=True)
        top_os, top_count = sorted_os[0]
        
        # 70%以上ならそのOS単独、そうでなければMix
        if top_count / total >= 0.7:
            return top_os
        else:
            return 'Mixed'

    def close(self):
        self.cur.close()
        self.conn.close()
        self.client.close()

if __name__ == "__main__":
    downloader = GigaDataDownloader()
    try:
        downloader.download_and_import_all()
    finally:
        downloader.close()
