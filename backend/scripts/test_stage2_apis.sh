#!/bin/bash
# Stage 2 API Test Suite
# Usage: bash backend/scripts/test_stage2_apis.sh

BASE_URL="http://localhost:8000"

echo "🧪 Stage 2 API Test Suite"
echo "================================"

# Check if server is running
echo -n "1. Health Check... "
response=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/api/health)
if [ "$response" -eq 200 ]; then
    echo "✅ Pass"
else
    echo "❌ Fail (Server not running?)"
    exit 1
fi

# Test Score API
echo -n "2. Score API (札幌市)... "
response=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/api/scores/011002)
if [ "$response" -eq 200 ]; then
    echo "✅ Pass"
    curl -s $BASE_URL/api/scores/011002 | jq -r '"\n   Total Score: \(.total_score)/100\n   Confidence: \(.confidence_level)"'
else
    echo "❌ Fail (Status: $response)"
fi

# Test Ranking API
echo -n "3. Ranking API (北海道)... "
response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/scores/ranking/北海道")
if [ "$response" -eq 200 ]; then
    echo "✅ Pass"
    count=$(curl -s "$BASE_URL/api/scores/ranking/北海道" | jq 'length')
    echo "   Found $count municipalities"
else
    echo "❌ Fail (Status: $response)"
fi

# Test Map API
echo -n "4. Map API (全国)... "
response=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/api/scores/map/all)
if [ "$response" -eq 200 ]; then
    echo "✅ Pass"
    count=$(curl -s $BASE_URL/api/scores/map/all | jq 'length')
    echo "   Found $count municipalities with coordinates"
else
    echo "❌ Fail (Status: $response)"
fi

# Test Proposal API
echo -n "5. Proposal Generation API... "
response=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE_URL/api/proposals/generate \
  -H "Content-Type: application/json" \
  -d '{"city_code":"011002","product":"Zoom Workplace","target_audience":"CIO"}')

if [ "$response" -eq 200 ]; then
    echo "✅ Pass"
    curl -s -X POST $BASE_URL/api/proposals/generate \
      -H "Content-Type: application/json" \
      -d '{"city_code":"011002","product":"Zoom Workplace","target_audience":"CIO"}' \
      | jq -r '"\n   Approach: \(.recommended_approach)\n   Pain Points: \(.key_pain_points | join(", "))"'
else
    echo "❌ Fail (Status: $response)"
fi

# Test Batch API
echo -n "6. Batch Trigger API... "
response=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE_URL/api/scores/batch \
  -H "Content-Type: application/json" \
  -d '{"city_codes":null}')

if [ "$response" -eq 202 ]; then
    echo "✅ Pass (Batch started in background)"
else
    echo "❌ Fail (Status: $response)"
fi

echo ""
echo "================================"
echo "🎉 Test Suite Complete"
echo ""
echo "💡 To view API docs, visit:"
echo "   http://localhost:8000/docs"
