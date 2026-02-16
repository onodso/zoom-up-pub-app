import requests
from backend.config import settings

class OllamaAnalyzer:
    def __init__(self):
        self.base_url = settings.OLLAMA_URL
        self.model = settings.OLLAMA_MODEL

    def analyze_mayor_speech(self, text: str) -> dict:
        """
        Analyze Mayor's policy speech to detect commitment.
        """
        prompt = f"""
        You are an expert political analyst. Analyze the following text from a Japanese mayor's policy speech regarding Digital Transformation (DX).

        Text: "{text[:3000]}"

        Your task is to determine:
        1. Does the mayor use strong first-person commitment language (Wait, in Japanese "I" is implicit, look for "私自身が先頭に立って", "私が責任を持って", "不退転の決意で")? Key is *Personal Responsibility*.
        2. Is there a specific budget mention related to DX/Digital? (Look for "予算", "円", "投資")

        Return ONLY a valid JSON object in the following format:
        {{
            "first_person_commitment": true/false,
            "budget_mentioned": true/false,
            "reason": "Short explanation in Japanese"
        }}
        """
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json" 
                },
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            
            # Parse the 'response' field which contains the actual JSON string
            import json
            analysis = json.loads(result.get("response", "{}"))
            
            return {
                "first_person_commitment": analysis.get("first_person_commitment", False),
                "budget_mentioned": analysis.get("budget_mentioned", False),
                # "reason": analysis.get("reason", "")
            }
            
        except Exception as e:
            print(f"Ollama Error: {e}")
            # Fallback
            return {
                "first_person_commitment": False,
                "budget_mentioned": False,
                "error": str(e)
            }
