import httpx
import json

body = {'city_code': '401307', 'focus_area': 'general'}

response = httpx.post('http://localhost:8000/api/proposals/generate', json=body, timeout=120)
result = response.json()

print('=' * 60)
print(f'City Code: {result["city_code"]}')
print(f'Generated At: {result["generated_at"]}')
print('=' * 60)
print('AI-GENERATED SALES PROPOSAL:')
print(result['proposal_text'])
print('=' * 60)
print(f'Length: {len(result["proposal_text"])} characters')
