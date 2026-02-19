"""
Test AI proposal generation for cities with different readiness scores
"""
import httpx
import json

test_cities = [
    ('401307', '福岡市', 'High Score (37/100)'),
    ('141003', '横浜市', 'High Score (34/100)'),
    ('11002', '札幌市', 'Medium Score (22/100)'),
    ('16331', '上士幌町', 'Low Score (estimated 15-18/100)'),
]

print('=' * 80)
print('AI PROPOSAL GENERATION TEST - Score-Based Variations')
print('=' * 80)
print()

for city_code, city_name, score_note in test_cities:
    print(f'\n{"=" * 80}')
    print(f'CITY: {city_name} ({city_code}) - {score_note}')
    print('=' * 80)

    try:
        body = {'city_code': city_code, 'focus_area': 'general'}
        response = httpx.post('http://localhost:8000/api/proposals/generate', json=body, timeout=120)

        if response.status_code == 200:
            result = response.json()
            print(f'\nGenerated: {result["generated_at"]}')
            print('\nPROPOSAL:\n')
            print(result['proposal_text'][:500])  # First 500 chars
            if len(result['proposal_text']) > 500:
                print(f'\n... (truncated, total {len(result["proposal_text"])} chars)')
        else:
            print(f'ERROR: Status {response.status_code}')

    except Exception as e:
        print(f'ERROR: {e}')

print('\n' + '=' * 80)
print('TEST COMPLETE')
print('=' * 80)
