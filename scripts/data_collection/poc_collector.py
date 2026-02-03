#!/usr/bin/env python3
"""
PoC用データ収集スクリプト - 10自治体
"""
import asyncio
import httpx
from datetime import datetime
import logging
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# PoC対象10自治体
POC_MUNICIPALITIES = [
    {'code': '131130', 'name': '渋谷区', 'url': 'https://www.city.shibuya.tokyo.jp'},
    {'code': '131181', 'name': '世田谷区', 'url': 'https://www.city.setagaya.lg.jp'},
    {'code': '141003', 'name': '横浜市', 'url': 'https://www.city.yokohama.lg.jp'},
    {'code': '231002', 'name': '名古屋市', 'url': 'https://www.city.nagoya.jp'},
    {'code': '271004', 'name': '大阪市', 'url': 'https://www.city.osaka.lg.jp'},
    {'code': '401005', 'name': '福岡市', 'url': 'https://www.city.fukuoka.lg.jp'},
    {'code': '011002', 'name': '札幌市', 'url': 'https://www.city.sapporo.jp'},
    {'code': '041003', 'name': '仙台市', 'url': 'https://www.city.sendai.jp'},
    {'code': '341002', 'name': '広島市', 'url': 'https://www.city.hiroshima.lg.jp'},
    {'code': '471003', 'name': '那覇市', 'url': 'https://www.city.naha.okinawa.jp'}
]


async def collect_municipality_data(municipality: dict) -> dict:
    """1自治体のデータ収集"""
    start_time = datetime.now()
    logger.info(f"開始: {municipality['name']}")
    
    result = {
        'code': municipality['code'],
        'name': municipality['name'],
        'url': municipality['url'],
        'status': 'success',
        'phases': {},
        'errors': []
    }
    
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        # Phase 1: トップページ取得
        try:
            phase1_start = datetime.now()
            response = await client.get(municipality['url'])
            result['phases']['scraping'] = {
                'duration_sec': (datetime.now() - phase1_start).total_seconds(),
                'status_code': response.status_code,
                'content_length': len(response.text)
            }
            logger.info(f"  スクレイピング完了: {response.status_code}")
        except Exception as e:
            result['status'] = 'partial'
            result['errors'].append(f"スクレイピング失敗: {str(e)}")
            result['phases']['scraping'] = {'error': str(e)}
            logger.error(f"  スクレイピング失敗: {e}")
        
        # Phase 2: PDF抽出（プレースホルダー）
        phase2_start = datetime.now()
        await asyncio.sleep(0.1)  # シミュレート
        result['phases']['pdf_extract'] = {
            'duration_sec': (datetime.now() - phase2_start).total_seconds(),
            'note': 'PDF抽出は後続実装'
        }
        
        # Phase 3: AI分析（プレースホルダー）
        phase3_start = datetime.now()
        await asyncio.sleep(0.1)  # シミュレート
        result['phases']['ai_analysis'] = {
            'duration_sec': (datetime.now() - phase3_start).total_seconds(),
            'note': 'AI分析は後続実装'
        }
        
        # Phase 4: DB保存（プレースホルダー）
        phase4_start = datetime.now()
        await asyncio.sleep(0.05)  # シミュレート
        result['phases']['db_save'] = {
            'duration_sec': (datetime.now() - phase4_start).total_seconds(),
            'note': 'DB保存は後続実装'
        }
    
    result['total_time_sec'] = (datetime.now() - start_time).total_seconds()
    logger.info(f"完了: {municipality['name']} ({result['total_time_sec']:.2f}秒)")
    
    return result


async def run_poc():
    """PoC実行"""
    logger.info("=" * 60)
    logger.info("PoC開始: 10自治体データ収集")
    logger.info("=" * 60)
    
    start_time = datetime.now()
    
    # 並列実行（3並列に制限）
    semaphore = asyncio.Semaphore(3)
    
    async def limited_collect(m):
        async with semaphore:
            return await collect_municipality_data(m)
    
    tasks = [limited_collect(m) for m in POC_MUNICIPALITIES]
    results = await asyncio.gather(*tasks)
    
    total_duration = (datetime.now() - start_time).total_seconds()
    
    # 統計計算
    successful = [r for r in results if r['status'] == 'success']
    avg_time = sum(r['total_time_sec'] for r in results) / len(results)
    
    # レポート出力
    logger.info("")
    logger.info("=" * 60)
    logger.info("PoC結果レポート")
    logger.info("=" * 60)
    logger.info(f"総処理時間: {total_duration:.2f}秒")
    logger.info(f"成功: {len(successful)}/{len(results)}")
    logger.info(f"平均処理時間: {avg_time:.2f}秒/自治体")
    logger.info(f"1,741自治体の推定時間: {avg_time * 1741 / 3600:.2f}時間")
    logger.info("")
    
    # 詳細結果
    for r in results:
        status_icon = "✅" if r['status'] == 'success' else "⚠️"
        logger.info(f"  {status_icon} {r['name']}: {r['total_time_sec']:.2f}秒")
        if r['errors']:
            for err in r['errors']:
                logger.info(f"      └─ {err}")
    
    # JSON出力
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_duration_sec': total_duration,
        'municipalities_count': len(results),
        'successful_count': len(successful),
        'avg_time_per_municipality': avg_time,
        'estimated_full_run_hours': avg_time * 1741 / 3600,
        'results': results
    }
    
    report_path = 'poc_report.json'
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    logger.info("")
    logger.info(f"📄 レポート保存: {report_path}")
    logger.info("=" * 60)
    
    return report


if __name__ == '__main__':
    asyncio.run(run_poc())
