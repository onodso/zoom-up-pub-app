import os
import httpx
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class LLMAnalyzer:
    """
    Ollamaを使用してニュースを分析・特定するクラス
    """
    def __init__(self):
        # MacのDockerからホストのOllamaにアクセスする場合、host.docker.internalが便利
        # あるいはOllamaもDocker内ならサービス名指定
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434")
        self.model = os.getenv("OLLAMA_MODEL", "llama3")

    async def analyze_news(self, title: str, snippet: str) -> Dict[str, Any]:
        """
        ニュースのタイトルとスニペットから、導入確度をスコアリングする
        """
        prompt = f"""
You are a professional sales strategist for Zoom Video Communications in Japan.
Your task is to analyze the following local government news and determine if it indicates a buying signal for Zoom or DX solutions.

News Title: {title}
News Snippet: {snippet}

Analyze the content based on these criteria:
- Score 80-100: Specific budget approval, public tender announcement, or direct mention of introducing web conferencing/Zoom.
- Score 60-79: "Consideration started", "Pilot test", "DX promotion plan formulated".
- Score 40-59: General DX topics, hiring digital personnel.
- Score 0-39: Unrelated news, routine announcements.

Output ONLY a JSON object with the following format (no markdown, no explanations outside JSON):
{{
    "score": <int 0-100>,
    "reason": "<Specific reason in Japanese, max 50 chars>",
    "buying_signal": <boolean>
}}
"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "format": "json" # Llama3 recent versions support JSON mode
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(f"{self.ollama_host}/api/generate", json=payload)
                if response.status_code != 200:
                    logger.error(f"Ollama Error: {response.text}")
                    return self._fallback_result()

                result = response.json()
                response_text = result.get("response", "")

                # JSONパース
                try:
                    data = json.loads(response_text)
                    return data
                except json.JSONDecodeError:
                    logger.warning(f"JSON Parse Error: {response_text}")
                    return self._fallback_result()

        except Exception as e:
            logger.error(f"LLM Connection Error: {e}", exc_info=True)
            return self._fallback_result()

    def _fallback_result(self) -> Dict[str, Any]:
        """
        LLMが失敗した場合のデフォルト値
        """
        return {
            "score": 0,
            "reason": "AI分析不可",
            "buying_signal": False
        }
