"""
import_estat_data.py — e-Stat APIから実データを一括取得してDBに投入

原則: Garbage in, Garbage out を避ける
ダミーデータはデータではない。実データだけを投入する。

取得対象:
1. 市区町村別人口（社会人口統計体系 0000020101, cat01=A1101, 最新年）
2. 財政力指数（団体概況 0003172920 から算出）
"""
import os
import sys
import time
import requests
import json
from typing import Dict, List, Optional, Tuple

# models と database をインポート
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from database import SQLALCHEMY_DATABASE_URL

# e-Stat API設定
ESTAT_APP_ID = os.getenv('ESTAT_APP_ID', 'ffaf6bbba7989e72e39d796fd0f62977d42e5731')
ESTAT_BASE_URL = 'https://api.e-stat.go.jp/rest/3.0/app/json'

# APIリクエスト間隔（レート制限対策）
REQUEST_INTERVAL = 1.0


def estat_get(endpoint: str, params: Dict) -> Dict:
    """e-Stat APIリクエスト（エラーハンドリング付き）"""
    params['appId'] = ESTAT_APP_ID
    url = f"{ESTAT_BASE_URL}/{endpoint}"
    
    response = requests.get(url, params=params, timeout=120)
    response.raise_for_status()
    data = response.json()
    
    if 'GET_STATS_DATA' in data:
        result = data['GET_STATS_DATA']
        status = result.get('RESULT', {}).get('STATUS', 0)
        if status != 0:
            error_msg = result.get('RESULT', {}).get('ERROR_MSG', '不明')
            print(f"   ⚠️ APIステータス {status}: {error_msg}")
            return {}  # 空辞書を返す（呼び出し元で処理）
        return result.get('STATISTICAL_DATA', {})
    
    return data


def build_area_code_mapping(session) -> Dict[str, Dict]:
    """
    e-Stat地域コード(5桁) → DBコード(lgcode)のマッピング構築
    
    e-Stat: 01100 (= 都道府県コード01 + 市区町村コード100)
    DB:     11002 (= lgcode)
    """
    rows = session.execute(text(
        "SELECT code, name, id, prefecture FROM municipalities"
    )).fetchall()
    
    # 名前ベースのマッピングも構築（コード変換が困難な場合のフォールバック）
    code_map = {}
    name_map = {}
    for row in rows:
        code_map[row[0]] = {'name': row[1], 'id': row[2], 'prefecture': row[3]}
        # 名前の正規化（スペース除去）
        clean_name = row[1].replace(' ', '').replace('　', '')
        name_map[clean_name] = row[0]
    
    return code_map, name_map


def fetch_population_data() -> List[Dict]:
    """
    人口データを一括取得
    統計表: 0000020101（社会人口統計体系）
    カテゴリ: A1101（総人口）
    時間: 最新年度
    """
    print("\n📊 人口データ取得: 社会人口統計体系 (0000020101)")
    print("   カテゴリ: A1101（総人口）")
    print("   年度: 2020年（令和2年国勢調査）")
    
    # 2020年国勢調査データを一括取得
    # 時間コード: 2020100000 = 2020年度
    CENSUS_TIME = '2020100000'
    
    print(f"   全市区町村データ取得中...")
    stat_data = estat_get('getStatsData', {
        'statsDataId': '0000020101',
        'cdCat01': 'A1101',  # 総人口
        'cdTime': CENSUS_TIME,
        'limit': 100000,
        'lang': 'J'
    })
    
    if not stat_data:
        print("   ❌ 人口データ取得失敗")
        return []
    
    values = stat_data.get('DATA_INF', {}).get('VALUE', [])
    if isinstance(values, dict):
        values = [values]
    
    # 地域名のマッピングも取得
    area_names = {}
    for cls in stat_data.get('CLASS_INF', {}).get('CLASS_OBJ', []):
        if cls.get('@id') == 'area':
            areas = cls.get('CLASS', [])
            if isinstance(areas, dict):
                areas = [areas]
            for a in areas:
                area_names[a.get('@code', '')] = a.get('@name', '')
    
    print(f"   取得件数: {len(values)}件")
    print(f"   地域数: {len(area_names)}件")
    
    # 結果を整形
    population_data = []
    for val in values:
        area_code = val.get('@area', '')
        pop_str = val.get('$', '')
        area_name = area_names.get(area_code, '')
        
        try:
            population = int(pop_str.replace(',', ''))
        except (ValueError, AttributeError):
            continue
        
        population_data.append({
            'area_code': area_code,
            'area_name': area_name,
            'population': population
        })
    
    # サンプル表示
    for pd in population_data[:5]:
        print(f"   サンプル: {pd['area_code']} {pd['area_name']} = {pd['population']:,}人")
    
    return population_data


def fetch_fiscal_data() -> List[Dict]:
    """
    財政データを一括取得
    統計表: 0003172920（団体概況 市町村分）
    項目: 基準財政収入額(100200)、基準財政需要額(100300)
    → 財政力指数 = 収入額 / 需要額
    """
    print("\n💰 財政データ取得: 団体概況 市町村分 (0003172920)")
    
    # まず時間軸を確認
    stat_data = estat_get('getStatsData', {
        'statsDataId': '0003172920',
        'limit': 1,
        'lang': 'J'
    })
    
    class_objs = stat_data.get('CLASS_INF', {}).get('CLASS_OBJ', [])
    latest_time = None
    for cls in class_objs:
        if cls.get('@id') == 'time':
            time_classes = cls.get('CLASS', [])
            if isinstance(time_classes, dict):
                time_classes = [time_classes]
            times = sorted(time_classes, key=lambda x: x.get('@code', ''), reverse=True)
            if times:
                latest_time = times[0].get('@code', '')
                latest_name = times[0].get('@name', '')
                print(f"   最新年度: {latest_name} (code: {latest_time})")
    
    time.sleep(REQUEST_INTERVAL)
    
    # 基準財政収入額を取得
    print(f"   基準財政収入額を取得中...")
    stat_income = estat_get('getStatsData', {
        'statsDataId': '0003172920',
        'cdTab': '100200',  # 基準財政収入額
        'cdTime': latest_time,
        'limit': 100000,
        'lang': 'J'
    })
    income_values = stat_income.get('DATA_INF', {}).get('VALUE', [])
    if isinstance(income_values, dict):
        income_values = [income_values]
    
    time.sleep(REQUEST_INTERVAL)
    
    # 基準財政需要額を取得
    print(f"   基準財政需要額を取得中...")
    stat_demand = estat_get('getStatsData', {
        'statsDataId': '0003172920',
        'cdTab': '100300',  # 基準財政需要額
        'cdTime': latest_time,
        'limit': 100000,
        'lang': 'J'
    })
    demand_values = stat_demand.get('DATA_INF', {}).get('VALUE', [])
    if isinstance(demand_values, dict):
        demand_values = [demand_values]
    
    print(f"   収入額: {len(income_values)}件, 需要額: {len(demand_values)}件")
    
    # 地域名のマッピング
    area_names = {}
    for cls in stat_income.get('CLASS_INF', {}).get('CLASS_OBJ', []):
        if cls.get('@id') == 'area':
            areas = cls.get('CLASS', [])
            if isinstance(areas, dict):
                areas = [areas]
            for a in areas:
                area_names[a.get('@code', '')] = a.get('@name', '')
    
    # 収入額をDict化
    income_map = {}
    for val in income_values:
        area_code = val.get('@area', '')
        try:
            income_map[area_code] = int(val.get('$', '0').replace(',', ''))
        except (ValueError, AttributeError):
            continue
    
    # 財政力指数 = 収入額 / 需要額
    fiscal_data = []
    for val in demand_values:
        area_code = val.get('@area', '')
        area_name = area_names.get(area_code, '')
        try:
            demand = int(val.get('$', '0').replace(',', ''))
        except (ValueError, AttributeError):
            continue
        
        income = income_map.get(area_code, 0)
        if demand > 0 and income > 0:
            fiscal_index = round(income / demand, 4)
            fiscal_data.append({
                'area_code': area_code,
                'area_name': area_name,
                'fiscal_index': fiscal_index,
                'income': income,
                'demand': demand
            })
    
    # サンプル表示
    for fd in fiscal_data[:5]:
        print(f"   サンプル: {fd['area_code']} {fd['area_name']} = {fd['fiscal_index']}")
    
    return fiscal_data


def import_to_db(population_data: List[Dict], fiscal_data: List[Dict]):
    """取得した実データをDBに投入"""
    print("\n📥 DBへの投入開始...")
    
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # DBの自治体リスト取得
        muni_rows = session.execute(text(
            "SELECT code, name, id FROM municipalities"
        )).fetchall()
        
        # e-Stat地域コード → DB lgcodeのマッピング
        # e-Stat: 01100 → DB: 11002(札幌市)
        # 名前ベースでマッチング
        db_name_to_code = {}
        db_code_set = set()
        for row in muni_rows:
            clean = row[1].replace(' ', '').replace('　', '')
            db_name_to_code[clean] = row[0]
            db_code_set.add(row[0])
        
        # e-Stat地域コードとDB lgcodeの直接マッチ試行
        estat_to_lgcode = {}
        for pd in population_data:
            acode = pd['area_code']
            aname = pd['area_name'].replace(' ', '').replace('　', '')
            # 名前の「都道府県名 」部分を除去
            parts = aname.split()
            if len(parts) > 1:
                aname = parts[-1]
            # プレフィックス除去（「北海道」「東京都」など）
            for pref in ['北海道', '青森県', '岩手県', '宮城県', '秋田県', '山形県',
                         '福島県', '茨城県', '栃木県', '群馬県', '埼玉県', '千葉県',
                         '東京都', '神奈川県', '新潟県', '富山県', '石川県', '福井県',
                         '山梨県', '長野県', '岐阜県', '静岡県', '愛知県', '三重県',
                         '滋賀県', '京都府', '大阪府', '兵庫県', '奈良県', '和歌山県',
                         '鳥取県', '島根県', '岡山県', '広島県', '山口県', '徳島県',
                         '香川県', '愛媛県', '高知県', '福岡県', '佐賀県', '長崎県',
                         '熊本県', '大分県', '宮崎県', '鹿児島県', '沖縄県']:
                if aname.startswith(pref):
                    aname = aname[len(pref):]
                    break
            
            if aname in db_name_to_code:
                estat_to_lgcode[acode] = db_name_to_code[aname]
            # e-Statコードがそのままlgcodeとして存在する場合
            elif acode in db_code_set:
                estat_to_lgcode[acode] = acode
        
        print(f"   コードマッチ: {len(estat_to_lgcode)}/{len(population_data)}件")
        
        # === 人口データ投入 ===
        pop_updated = 0
        for pd in population_data:
            lgcode = estat_to_lgcode.get(pd['area_code'])
            if lgcode:
                session.execute(text(
                    "UPDATE municipalities SET population = :pop WHERE code = :code"
                ), {'pop': pd['population'], 'code': lgcode})
                session.execute(text(
                    "UPDATE entities SET population = :pop WHERE entity_id = :eid"
                ), {'pop': pd['population'], 'eid': f'M{lgcode}'})
                pop_updated += 1
        
        session.commit()
        print(f"   ✅ 人口: {pop_updated}件 更新完了")
        
        # === 財政力指数投入 ===
        fiscal_updated = 0
        for fd in fiscal_data:
            lgcode = estat_to_lgcode.get(fd['area_code'])
            if lgcode:
                session.execute(text(
                    "UPDATE municipalities SET fiscal_index = :fi WHERE code = :code"
                ), {'fi': fd['fiscal_index'], 'code': lgcode})
                session.execute(text(
                    "UPDATE entities SET fiscal_index = :fi WHERE entity_id = :eid"
                ), {'fi': fd['fiscal_index'], 'eid': f'M{lgcode}'})
                fiscal_updated += 1
        
        session.commit()
        print(f"   ✅ 財政力指数: {fiscal_updated}件 更新完了")
        
        # === 検証 ===
        print("\n🔍 検証:")
        checks = [
            ("札幌市", "人口 ≈ 1,970,000"),
            ("函館市", "人口 ≈ 250,000"),
        ]
        for city_name, expected in checks:
            row = session.execute(text(
                "SELECT name, population, fiscal_index FROM municipalities WHERE name = :name LIMIT 1"
            ), {'name': city_name}).fetchone()
            if row:
                print(f"   {row[0]}: 人口={row[1]:,}, 財政力指数={row[2]}")
                print(f"     期待値: {expected}")
        
        # ユニーク人口値の確認
        uniq = session.execute(text(
            "SELECT COUNT(DISTINCT population) FROM municipalities WHERE population IS NOT NULL"
        )).scalar()
        print(f"   人口ユニーク値: {uniq}件（ダミーなら16、実データなら1000以上）")
        
    except Exception as e:
        session.rollback()
        print(f"   ❌ エラー: {e}")
        raise
    finally:
        session.close()


def main():
    print("=" * 60)
    print("🚀 e-Stat 実データ投入パイプライン")
    print("   原則: Garbage in, Garbage out を避ける")
    print("=" * 60)
    
    # Step 1: 人口データ取得
    population_data = fetch_population_data()
    time.sleep(REQUEST_INTERVAL)
    
    # Step 2: 財政データ取得
    fiscal_data = fetch_fiscal_data()
    time.sleep(REQUEST_INTERVAL)
    
    # Step 3: DB投入
    import_to_db(population_data, fiscal_data)
    
    print("\n✅ 実データ投入完了！")


if __name__ == "__main__":
    main()
