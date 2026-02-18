"""
Map Data API ルーター

ドリルダウン型地図ダッシュボードのためのAPIエンドポイント
- 地方別スコア集計
- 都道府県別スコア集計
- 自治体一覧+スコア
- 自治体詳細（全データ）
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from typing import Optional, List

router = APIRouter(prefix="/api/v1/map", tags=["Map Data"])

# 8地方区分の定義
PREFECTURES_BY_REGION = {
    '北海道地方': ['北海道'],
    '東北地方': ['青森県', '岩手県', '宮城県', '秋田県', '山形県', '福島県'],
    '関東地方': ['茨城県', '栃木県', '群馬県', '埼玉県', '千葉県', '東京都', '神奈川県'],
    '中部地方': ['新潟県', '富山県', '石川県', '福井県', '山梨県', '長野県', '岐阜県', '静岡県', '愛知県'],
    '近畿地方': ['三重県', '滋賀県', '京都府', '大阪府', '兵庫県', '奈良県', '和歌山県'],
    '中国地方': ['鳥取県', '島根県', '岡山県', '広島県', '山口県'],
    '四国地方': ['徳島県', '香川県', '愛媛県', '高知県'],
    '九州・沖縄地方': ['福岡県', '佐賀県', '長崎県', '熊本県', '大分県', '宮崎県', '鹿児島県', '沖縄県'],
}

# 都道府県→地方の逆引き辞書
REGION_BY_PREFECTURE = {}
for region, prefs in PREFECTURES_BY_REGION.items():
    for pref in prefs:
        REGION_BY_PREFECTURE[pref] = region


@router.get("/regions")
async def get_region_scores(db: Session = Depends(get_db)):
    """
    地方別のスコア集計を返す（Level 1: 全国地図）

    Returns:
        各地方の平均スコア、自治体数、都道府県数
    """
    result = db.execute(text("""
        SELECT
            m.prefecture,
            ROUND(AVG(s.total_score), 1) as avg_score,
            COUNT(*) as municipality_count,
            SUM(m.population) as total_population
        FROM municipalities m
        LEFT JOIN dx_scores_improved s ON m.city_code = s.city_code
        WHERE m.prefecture IS NOT NULL
        GROUP BY m.prefecture
        ORDER BY m.prefecture
    """))

    pref_data = [dict(row._mapping) for row in result]

    # 地方ごとに集約
    regions = {}
    for pref in pref_data:
        region_name = REGION_BY_PREFECTURE.get(pref['prefecture'], '不明')
        if region_name not in regions:
            regions[region_name] = {
                'region': region_name,
                'prefectures': [],
                'total_score_sum': 0,
                'total_count': 0,
                'total_population': 0,
            }
        r = regions[region_name]
        r['prefectures'].append(pref['prefecture'])
        score = pref['avg_score'] or 0
        r['total_score_sum'] += float(score) * pref['municipality_count']
        r['total_count'] += pref['municipality_count']
        r['total_population'] += pref['total_population'] or 0

    # 平均スコアを算出
    result_list = []
    for r in regions.values():
        avg = round(r['total_score_sum'] / r['total_count'], 1) if r['total_count'] > 0 else 0
        result_list.append({
            'region': r['region'],
            'avg_score': avg,
            'municipality_count': r['total_count'],
            'prefecture_count': len(r['prefectures']),
            'total_population': r['total_population'],
            'prefectures': r['prefectures'],
        })

    return result_list


@router.get("/prefectures")
async def get_prefecture_scores(
    region: Optional[str] = Query(None, description="地方名でフィルタ"),
    db: Session = Depends(get_db)
):
    """
    都道府県別のスコア集計を返す（Level 2: 地方ビュー）

    Args:
        region: 地方名（'関東地方'など）でフィルタ可能
    """
    query = """
        SELECT
            m.prefecture,
            ROUND(AVG(s.total_score), 1) as avg_score,
            ROUND(AVG(s.cat_citizen_services), 1) as avg_citizen,
            ROUND(AVG(s.cat_promotion_system), 1) as avg_promotion,
            ROUND(AVG(s.cat_business_dx), 1) as avg_business,
            ROUND(AVG(s.cat_education_dx), 1) as avg_education,
            ROUND(AVG(s.cat_information), 1) as avg_information,
            COUNT(*) as municipality_count,
            SUM(m.population) as total_population
        FROM municipalities m
        LEFT JOIN dx_scores_improved s ON m.city_code = s.city_code
        WHERE m.prefecture IS NOT NULL
    """
    params = {}

    if region and region in PREFECTURES_BY_REGION:
        prefs = PREFECTURES_BY_REGION[region]
        placeholders = ', '.join([f':p{i}' for i in range(len(prefs))])
        query += f" AND m.prefecture IN ({placeholders})"
        for i, p in enumerate(prefs):
            params[f'p{i}'] = p

    query += " GROUP BY m.prefecture ORDER BY m.prefecture"

    result = db.execute(text(query), params)
    rows = [dict(row._mapping) for row in result]

    # 地方名を付与
    for row in rows:
        row['region'] = REGION_BY_PREFECTURE.get(row['prefecture'], '不明')

    return rows


@router.get("/municipalities")
async def get_municipality_scores(
    prefecture: Optional[str] = Query(None, description="都道府県名でフィルタ"),
    region: Optional[str] = Query(None, description="地方名でフィルタ"),
    min_score: Optional[float] = Query(None, description="最小スコア"),
    max_score: Optional[float] = Query(None, description="最大スコア"),
    limit: int = Query(2500, description="取得件数上限"),
    db: Session = Depends(get_db)
):
    """
    自治体一覧+スコアを返す（Level 3: 都道府県ビュー）

    Args:
        prefecture: 都道府県名でフィルタ
        region: 地方名でフィルタ
        min_score/max_score: スコア範囲でフィルタ
    """
    query = """
        SELECT
            m.city_code,
            m.city_name,
            m.prefecture,
            m.population,
            m.latitude,
            m.longitude,
            COALESCE(s.total_score, 0) as total_score,
            s.cat_citizen_services,
            s.cat_promotion_system,
            s.cat_business_dx,
            s.cat_education_dx,
            s.cat_information,
            p.pattern_id,
            p.pattern_name
        FROM municipalities m
        LEFT JOIN dx_scores_improved s ON m.city_code = s.city_code
        LEFT JOIN municipality_patterns p ON m.city_code = p.city_code
        WHERE m.latitude IS NOT NULL
    """
    params = {}

    if prefecture:
        query += " AND m.prefecture = :prefecture"
        params['prefecture'] = prefecture
    elif region and region in PREFECTURES_BY_REGION:
        prefs = PREFECTURES_BY_REGION[region]
        placeholders = ', '.join([f':p{i}' for i in range(len(prefs))])
        query += f" AND m.prefecture IN ({placeholders})"
        for i, p in enumerate(prefs):
            params[f'p{i}'] = p

    if min_score is not None:
        query += " AND COALESCE(s.total_score, 0) >= :min_score"
        params['min_score'] = min_score
    if max_score is not None:
        query += " AND COALESCE(s.total_score, 0) <= :max_score"
        params['max_score'] = max_score

    query += " ORDER BY s.total_score DESC NULLS LAST LIMIT :limit"
    params['limit'] = limit

    result = db.execute(text(query), params)
    rows = []
    for row in result:
        r = dict(row._mapping)
        r['region'] = REGION_BY_PREFECTURE.get(r['prefecture'], '不明')
        r['latitude'] = float(r['latitude']) if r['latitude'] else None
        r['longitude'] = float(r['longitude']) if r['longitude'] else None
        rows.append(r)

    return rows


@router.get("/municipality/{city_code}")
async def get_municipality_detail(city_code: str, db: Session = Depends(get_db)):
    """
    自治体の詳細情報を返す（Level 4: 自治体ダッシュボード）

    全データ（DX指標15種、GIGA、ニュース、パターン、スコア）を返す
    """
    # 基本データ + スコア + パターン + GIGA
    result = db.execute(text("""
        SELECT
            m.city_code, m.city_name, m.prefecture, m.population,
            m.latitude, m.longitude, m.dx_status,
            s.total_score,
            s.cat_citizen_services, s.cat_promotion_system,
            s.cat_business_dx, s.cat_education_dx, s.cat_information,
            p.pattern_id, p.pattern_name, p.confidence_score,
            p.policy_status, p.mynumber_rate, p.online_proc_rate,
            e.computer_per_student, e.terminal_os_type, e.survey_year
        FROM municipalities m
        LEFT JOIN dx_scores_improved s ON m.city_code = s.city_code
        LEFT JOIN municipality_patterns p ON m.city_code = p.city_code
        LEFT JOIN education_info e ON m.city_code = e.city_code
        WHERE m.city_code = :city_code
        LIMIT 1
    """), {'city_code': city_code})

    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="自治体が見つかりません")

    data = dict(row._mapping)
    data['region'] = REGION_BY_PREFECTURE.get(data['prefecture'], '不明')

    # ニュース記事を取得
    news_result = db.execute(text("""
        SELECT title, url, source, category, published_at, collected_at
        FROM municipality_news
        WHERE city_code = :city_code
        ORDER BY collected_at DESC
        LIMIT 20
    """), {'city_code': city_code})
    data['news'] = [dict(r._mapping) for r in news_result]

    # 全国ランキング
    rank_result = db.execute(text("""
        SELECT COUNT(*) + 1 as rank
        FROM dx_scores_improved
        WHERE total_score > (SELECT total_score FROM dx_scores_improved WHERE city_code = :city_code)
    """), {'city_code': city_code})
    rank_row = rank_result.fetchone()
    data['national_rank'] = rank_row._mapping['rank'] if rank_row else None

    total_result = db.execute(text("SELECT COUNT(*) as total FROM dx_scores_improved"))
    data['total_municipalities'] = total_result.fetchone()._mapping['total']

    # 同規模自治体の比較データ（人口±30%の自治体Top5）
    if data['population'] is not None and data['population'] > 0:
        pop = data['population']
        comparison_result = db.execute(text("""
            SELECT m.city_name, m.population, s.total_score
            FROM municipalities m
            JOIN dx_scores_improved s ON m.city_code = s.city_code
            WHERE m.population BETWEEN :pop_min AND :pop_max
              AND m.city_code != :city_code
            ORDER BY s.total_score DESC
            LIMIT 5
        """), {
            'pop_min': int(pop * 0.7),
            'pop_max': int(pop * 1.3),
            'city_code': city_code
        })
        data['similar_municipalities'] = [dict(r._mapping) for r in comparison_result]

    return data


@router.get("/stats")
async def get_overall_stats(db: Session = Depends(get_db)):
    """
    全体統計情報を返す

    ダッシュボードのヘッダー部分に表示する統計データ
    """
    result = db.execute(text("""
        SELECT
            COUNT(*) as total_municipalities,
            ROUND(AVG(total_score), 1) as avg_score,
            ROUND(MIN(total_score), 1) as min_score,
            ROUND(MAX(total_score), 1) as max_score,
            ROUND(STDDEV(total_score), 1) as stddev_score
        FROM dx_scores_improved
    """))
    stats = dict(result.fetchone()._mapping)

    # パターン分布
    pattern_result = db.execute(text("""
        SELECT pattern_name, COUNT(*) as count
        FROM municipality_patterns
        WHERE pattern_id != 7
        GROUP BY pattern_name, pattern_id
        ORDER BY pattern_id
    """))
    stats['pattern_distribution'] = [dict(r._mapping) for r in pattern_result]

    return stats
