"""
Pilot Campaign: Generate AI Proposals for Top 50 Municipalities
Creates CSV file with proposals for sales team review
"""
import sys
import os
from pathlib import Path
import psycopg2
from psycopg2.extras import RealDictCursor
import httpx
import csv
import time
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))
from config import settings

def generate_proposal(city_code, focus_area='general', retries=2):
    """Generate AI proposal with retry logic"""
    for attempt in range(retries):
        try:
            response = httpx.post(
                'http://localhost:8000/api/proposals/generate',
                json={'city_code': city_code, 'focus_area': focus_area},
                timeout=120.0
            )
            if response.status_code == 200:
                return response.json()['proposal_text']
            else:
                print(f"  ⚠️  API returned status {response.status_code}")
        except Exception as e:
            print(f"  ⚠️  Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(2)

    return "ERROR: Failed to generate proposal after retries"

def main():
    print("=" * 80)
    print("PILOT CAMPAIGN: Top 50 Municipality Proposal Generation")
    print("=" * 80)
    print()

    # Connect to database
    conn = psycopg2.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        database=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD
    )

    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Get top 50 municipalities with score >= 30
        cur.execute("""
            SELECT
                s.city_code,
                m.city_name,
                m.prefecture,
                m.region,
                m.population,
                m.official_url,
                s.total_score,
                s.structural_pressure,
                s.leadership_commitment,
                s.peer_pressure,
                s.feasibility,
                s.accountability,
                s.confidence_level
            FROM decision_readiness_scores s
            JOIN municipalities m ON s.city_code = m.city_code
            WHERE s.total_score >= 30
            ORDER BY s.total_score DESC, m.population DESC
            LIMIT 50
        """)

        targets = cur.fetchall()
        print(f"📊 Found {len(targets)} target municipalities")
        print()

        # Prepare CSV output
        output_file = '/app/pilot_campaign_proposals.csv'

        with open(output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
            fieldnames = [
                'Rank', 'City Code', 'City Name', 'Prefecture', 'Region',
                'Population', 'Total Score', 'Tier',
                'Structural', 'Leadership', 'Peer', 'Feasibility', 'Accountability',
                'Confidence', 'Official URL',
                'AI Proposal', 'Status', 'Generated At'
            ]

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for idx, target in enumerate(targets, 1):
                print(f"[{idx}/50] {target['city_name']} ({target['prefecture']}) - Score: {target['total_score']}")

                # Determine tier
                score = target['total_score']
                if score >= 35:
                    tier = "🏆 Top"
                elif score >= 33:
                    tier = "🥇 High"
                else:
                    tier = "🥈 Medium-High"

                # Generate AI proposal
                print(f"  🤖 Generating AI proposal...")
                proposal_text = generate_proposal(target['city_code'])

                if "ERROR" in proposal_text:
                    status = "⚠️ Generation Failed"
                else:
                    status = "✅ Ready for Review"
                    # Truncate for preview
                    preview = proposal_text[:100] + "..." if len(proposal_text) > 100 else proposal_text
                    print(f"  📝 {preview}")

                # Write to CSV
                writer.writerow({
                    'Rank': idx,
                    'City Code': target['city_code'],
                    'City Name': target['city_name'],
                    'Prefecture': target['prefecture'],
                    'Region': target['region'],
                    'Population': target['population'],
                    'Total Score': target['total_score'],
                    'Tier': tier,
                    'Structural': target['structural_pressure'],
                    'Leadership': target['leadership_commitment'],
                    'Peer': target['peer_pressure'],
                    'Feasibility': target['feasibility'],
                    'Accountability': target['accountability'],
                    'Confidence': target['confidence_level'],
                    'Official URL': target['official_url'] or '',
                    'AI Proposal': proposal_text,
                    'Status': status,
                    'Generated At': datetime.now().isoformat()
                })

                print(f"  {status}")
                print()

                # Rate limit: 1 second between requests
                if idx < len(targets):
                    time.sleep(1)

        print("=" * 80)
        print(f"✅ Campaign file generated: {output_file}")
        print(f"📊 Total proposals: {len(targets)}")
        print("=" * 80)
        print()
        print("Next steps:")
        print("1. Review proposals in Excel/Google Sheets")
        print("2. Customize with specific contact details")
        print("3. Send to municipality contacts")
        print("4. Track responses in CRM")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    main()
