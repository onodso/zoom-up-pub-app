"""
Zoom Team Chat 通知ユーティリティ
（Webhook URL設定後に有効化）
"""
import os
import httpx
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

ZOOM_WEBHOOK_URL = os.getenv('ZOOM_CHAT_WEBHOOK_URL', '')


async def notify_error(
    error_type: str,
    error_message: str,
    endpoint: Optional[str] = None,
    user_id: Optional[int] = None
):
    """エラー通知をZoom Team Chatに送信"""
    
    if not ZOOM_WEBHOOK_URL:
        logger.warning("ZOOM_CHAT_WEBHOOK_URL が設定されていません - 通知をスキップ")
        return
    
    # メッセージ構築
    message = {
        "text": f"🚨 **エラー発生**",
        "body": [
            {
                "type": "message",
                "text": f"**種別**: {error_type}\n**メッセージ**: {error_message}\n**エンドポイント**: {endpoint or 'N/A'}\n**発生時刻**: {datetime.now().isoformat()}"
            }
        ]
    }
    
    # Webhook送信
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(ZOOM_WEBHOOK_URL, json=message, timeout=10.0)
            response.raise_for_status()
            logger.info(f"Zoom通知送信成功: {error_type}")
        except Exception as e:
            logger.error(f"Zoom通知送信失敗: {e}")


async def notify_daily_summary(summary: dict):
    """日次サマリー通知"""
    
    if not ZOOM_WEBHOOK_URL:
        logger.warning("ZOOM_CHAT_WEBHOOK_URL が設定されていません - 通知をスキップ")
        return
    
    message = {
        "text": "📊 **DX Intelligence 日次レポート**",
        "body": [
            {
                "type": "message",
                "text": f"**総アクセス数**: {summary.get('total_access', 0)}\n**アクティブユーザー**: {summary.get('active_users', 0)}\n**エラー数**: {summary.get('error_count', 0)}\n**平均応答時間**: {summary.get('avg_response_time', 0)}ms"
            },
            {
                "type": "message",
                "text": "[詳細ログを確認](https://dx.kikagaku-zoom.com/admin/logs)"
            }
        ]
    }
    
    async with httpx.AsyncClient() as client:
        try:
            await client.post(ZOOM_WEBHOOK_URL, json=message, timeout=10.0)
            logger.info("日次サマリー通知送信成功")
        except Exception as e:
            logger.error(f"日次サマリー通知送信失敗: {e}")
