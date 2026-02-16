from dataclasses import dataclass
from typing import Dict, List, Optional
import psycopg2
from datetime import datetime

# Assuming these data sources are available or mocked for now
# from backend.data_sources.estat_api import EstatAPI 

@dataclass
class DecisionReadinessScore:
    city_code: str
    structural_pressure: int      # 30pts
    leadership_commitment: int    # 25pts
    peer_pressure: int            # 20pts
    feasibility: int              # 15pts
    accountability: int           # 10pts
    total: int                    # 100pts
    confidence: str               # 'high', 'medium', 'low'
    breakdown: Dict

class DecisionReadinessScorerV3:
    def __init__(self, db_conn):
        self.conn = db_conn
        # in real usage, we might fetch e-Stat data live or from DB cache.
        # Here we assume data is already in DB (municipalities table) for Structural/Feasibility
        
    def score(self, city_code: str, analysis_result: dict = {}) -> DecisionReadinessScore:
        """
        Calculate the 100-point Decision Readiness Score.
        analysis_result contains pre-computed AI insights.
        """
        # 1. Structural Pressure (30pts) - Data from DB (e-Stat sourced)
        structural, s_breakdown = self._score_structural_pressure(city_code)
        
        # 2. Leadership Commitment (25pts) - Text Analysis (Ollama/BERT)
        leadership, l_breakdown = self._score_leadership_commitment(city_code, analysis_result)
        
        # 3. Peer Pressure (20pts) - DB Analysis
        peer, p_breakdown = self._score_peer_pressure(city_code)
        
        # 4. Feasibility (15pts) - DB Analysis (Digital Agency CSV)
        feasibility, f_breakdown = self._score_feasibility(city_code)
        
        # 5. Accountability (10pts) - Text/DB Analysis
        accountability, a_breakdown = self._score_accountability(city_code, []) # TODO: Pass text if needed
        
        total = structural + leadership + peer + feasibility + accountability
        confidence = self._determine_confidence(total, 1 if analysis_result else 0)
        
        # Comprehensive Breakdown
        breakdown = {
            'structural': s_breakdown,
            'leadership': l_breakdown,
            'peer': p_breakdown,
            'feasibility': f_breakdown,
            'accountability': a_breakdown
        }
        
        return DecisionReadinessScore(
            city_code=city_code,
            structural_pressure=structural,
            leadership_commitment=leadership,
            peer_pressure=peer,
            feasibility=feasibility,
            accountability=accountability,
            total=total,
            confidence=confidence,
            breakdown=breakdown
        )
    
    # --- 1. Structural Pressure (30pts) ---
    def _score_structural_pressure(self, city_code: str):
        # Fetch data from DB
        cur = self.conn.cursor()
        cur.execute("""
            SELECT 
                COALESCE(population_decline_rate, 0) as pop_decline,
                COALESCE(elderly_ratio, 0) as elderly_ratio,
                COALESCE(fiscal_index, 0.5) as fiscal_index, -- Default to average
                COALESCE(staff_reduction_rate, 0) as staff_reduction
            FROM municipalities 
            WHERE city_code = %s
        """, (city_code,))
        row = cur.fetchone()
        
        if not row:
            return 0, {"error": "No data"}
            
        pop_decline = row[0]
        elderly_ratio = row[1]
        fiscal_index = row[2]
        staff_reduction = row[3]
        
        score = 0
        details = {}
        
        # 1.1 Demographic Crisis (12pts)
        demo_score = 0
        if pop_decline > 0.20: demo_score += 6
        elif pop_decline > 0.10: demo_score += 4
        elif pop_decline > 0.05: demo_score += 2
        
        if elderly_ratio > 0.40: demo_score += 4
        elif elderly_ratio > 0.35: demo_score += 2
        
        # Working age decline (Mock replacement -> derive from decline rate)
        if pop_decline > 0.25: demo_score += 2
        
        score += min(demo_score, 12)
        details['demographic'] = min(demo_score, 12)
        
        # 1.2 Fiscal Pressure (12pts)
        fiscal_score = 0
        if fiscal_index < 0.30: fiscal_score += 6
        elif fiscal_index < 0.50: fiscal_score += 4
        
        # Real Debt Service Ratio (Mock/Placeholder -> Assume fiscal index correlates)
        if fiscal_index < 0.20: fiscal_score += 3
        
        score += min(fiscal_score, 12)
        details['fiscal'] = min(fiscal_score, 12)
        
        # 1.3 Staff Burnout (6pts)
        staff_score = 0
        if staff_reduction > 0.20: staff_score += 4
        elif staff_reduction > 0.10: staff_score += 2
        
        score += min(staff_score, 6)
        details['burnout'] = min(staff_score, 6)
        
        return min(score, 30), details

    # --- 2. Leadership Commitment (25pts) ---
    def _score_leadership_commitment(self, city_code: str, analysis_result: dict):
        """
        analysis_result format:
        {
            "bert_score": int (0-25),
            "ollama_keywords": ["budget", "first_person"],
            "ollama_score": int
        }
        """
        score = 0
        details = {}
        
        # 2.1 Mayor's Direct Speech (12pts) - from BERT/Ollama
        # Use BERT score for "Commitment"
        mayor_score = analysis_result.get("bert_score", 0)
        
        # Augment with Ollama specific keywords
        keywords = analysis_result.get("ollama_keywords", [])
        if "first_person" in keywords: mayor_score += 2
        
        score += min(mayor_score, 12)
        details['mayor_speech'] = min(mayor_score, 12)
        
        # 2.2 Org Structure (8pts)
        # Fetch from DB (enriched by dx_progress.csv -> stored in dx_status JSONB)
        cur = self.conn.cursor()
        cur.execute("SELECT dx_status FROM municipalities WHERE city_code = %s", (city_code,))
        row = cur.fetchone()
        dx_status = row[0] if row else {}
        
        org_score = 0
        if dx_status:
            # Logic based on real CSV column names (mapped)
            if dx_status.get('dept'): org_score += 4
            if dx_status.get('cio') == 'あり': org_score += 2
            if dx_status.get('ext_cio') == 'あり': org_score += 2
            
        score += min(org_score, 8)
        details['org_structure'] = min(org_score, 8)
        
        # 2.3 Budget (5pts)
        budget_score = 0
        if "budget" in keywords: budget_score += 5 # "Specified in Ollama extraction"
        
        score += min(budget_score, 5)
        details['budget'] = min(budget_score, 5)
        
        return min(score, 25), details

    # --- 3. Peer Pressure (20pts) ---
    def _score_peer_pressure(self, city_code: str):
        """
        Calculate peer pressure based on regional DX adoption patterns.
        Enhanced v2: Uses real data from dx_status field.
        """
        score = 0
        details = {}
        cur = self.conn.cursor()

        # Get this city's region and prefecture
        cur.execute("""
            SELECT region, prefecture, dx_status
            FROM municipalities
            WHERE city_code = %s
        """, (city_code,))
        row = cur.fetchone()
        if not row:
            return 0, {"error": "City not found"}

        region, prefecture, dx_status = row
        dx_status = dx_status or {}

        # 3.1 Regional DX Adoption Rate (10pts)
        # Count municipalities in same region with DX departments
        cur.execute("""
            SELECT
                COUNT(*) FILTER (WHERE dx_status->>'dept' = 'true') as with_dept,
                COUNT(*) as total
            FROM municipalities
            WHERE region = %s AND dx_status IS NOT NULL
        """, (region,))
        adoption = cur.fetchone()

        if adoption and adoption[1] > 0:
            adoption_rate = adoption[0] / adoption[1]
            regional_score = int(adoption_rate * 10)  # 0-10 pts
            score += min(regional_score, 10)
            details['regional_adoption'] = f"{adoption_rate:.1%}"
        else:
            details['regional_adoption'] = "0%"

        # 3.2 Prefecture Leadership (5pts)
        # Advanced DX prefectures get bonus points
        advanced_prefectures = ['東京都', '神奈川県', '大阪府', '福岡県', '愛知県', '京都府']
        if prefecture in advanced_prefectures:
            score += 5
            details['prefecture_bonus'] = 5
        else:
            # Partial points for moderate prefectures
            moderate_prefectures = ['北海道', '宮城県', '埼玉県', '千葉県', '兵庫県', '広島県']
            if prefecture in moderate_prefectures:
                score += 3
                details['prefecture_bonus'] = 3
            else:
                details['prefecture_bonus'] = 0

        # 3.3 Government Policy Alignment (5pts)
        # Cities with external CIO or strategy get bonus (shows national policy adoption)
        policy_score = 0
        if dx_status.get('ext_cio') == 'あり':
            policy_score += 3
        if dx_status.get('strategy'):
            policy_score += 2
        score += min(policy_score, 5)
        details['policy_alignment'] = policy_score

        return min(score, 20), details

    # --- 4. Feasibility (15pts) ---
    def _score_feasibility(self, city_code: str):
        """
        Calculate feasibility based on technical readiness and organizational capacity.
        Enhanced v2: Uses dx_status JSON and population data.
        """
        score = 0
        details = {}
        cur = self.conn.cursor()

        # Get city data
        cur.execute("""
            SELECT dx_status, population
            FROM municipalities
            WHERE city_code = %s
        """, (city_code,))
        row = cur.fetchone()
        if not row:
            return 0, {"error": "City not found"}

        dx_status, population = row
        dx_status = dx_status or {}
        population = population or 0

        # 4.1 Technical Readiness (8pts)
        tech_score = 0

        # Cloud migration status
        cloud_status = dx_status.get('cloud_migration', '')
        if cloud_status == '完了':
            tech_score += 4
        elif cloud_status == '進行中':
            tech_score += 2

        # LGWAN connection (almost universal, but verify)
        if dx_status.get('lgwan_connection', True):
            tech_score += 2

        # DX department exists
        if dx_status.get('dept'):
            tech_score += 2

        score += min(tech_score, 8)
        details['technical'] = tech_score

        # 4.2 Funding Capacity (4pts)
        # Use population as proxy for budget size
        fund_score = 0
        if population >= 500000:
            fund_score = 4  # Major cities
        elif population >= 100000:
            fund_score = 3  # Large cities
        elif population >= 30000:
            fund_score = 2  # Medium cities
        else:
            fund_score = 1  # Small municipalities

        score += min(fund_score, 4)
        details['funding'] = fund_score

        # 4.3 HR Capacity (3pts)
        hr_score = 0

        # CIO appointed
        if dx_status.get('cio') == 'あり':
            hr_score += 1

        # External CIO (shows ability to hire expertise)
        if dx_status.get('ext_cio') == 'あり':
            hr_score += 2
        elif population >= 100000:
            # Large cities likely have internal capacity
            hr_score += 1

        score += min(hr_score, 3)
        details['hr'] = hr_score

        return min(score, 15), details

    # --- 5. Accountability (10pts) ---
    def _score_accountability(self, city_code: str, texts: List[str]):
        combined_text = " ".join(texts)
        score = 0
        details = {}
        
        # 5.1 Case Studies (6pts)
        # Internal DB query
        case_score = 4 # Mock
        score += min(case_score, 6)
        details['cases'] = case_score
        
        # 5.2 KPI Clarity (4pts)
        kpi_score = 0
        if "%" in combined_text or "削減" in combined_text: kpi_score += 2
        if "EBPM" in combined_text: kpi_score += 2
        score += min(kpi_score, 4)
        details['kpi'] = kpi_score
        
        return min(score, 10), details

    def _determine_confidence(self, total: int, text_count: int) -> str:
        if total >= 80 and text_count >= 1: return 'high'
        if total >= 60: return 'medium'
        return 'low'
