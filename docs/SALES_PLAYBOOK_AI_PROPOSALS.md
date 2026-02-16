# Sales Playbook: AI-Powered Municipality Proposals

**Version:** 1.0
**Last Updated:** 2026-02-14
**AI Engine:** Llama 3.2 3B (Ollama)

---

## Overview

The Decision Readiness v3.0 system now includes **AI-powered sales proposal generation** using local LLMs. This provides Zoom sales teams with customized, score-based proposals for each municipality without requiring external API calls or data sharing.

---

## How It Works

###  **1. Readiness Scoring (9-37/100)**

All 1,916 Japanese municipalities have been scored across 5 pillars:

| Pillar | Max Points | Description |
|--------|-----------|-------------|
| **Structural Pressure** | 30 | Demographics, fiscal stress, staff burnout |
| **Leadership Commitment** | 25 | DX department, CIO, strategy, budget |
| **Peer Pressure** | 20 | Regional adoption, prefecture leadership |
| **Feasibility** | 15 | Tech readiness, funding, HR capacity |
| **Accountability** | 10 | Case studies, KPI clarity |

### **2. Score Tiers**

| Tier | Score Range | Count | Strategy |
|------|-------------|-------|----------|
| 🏆 **Top Tier** | 33-37 | ~150 | Advanced innovation, model city |
| 🥇 **High** | 25-32 | ~400 | Proven ROI, peer success stories |
| 🥈 **Medium** | 18-24 | ~600 | Start small, quick wins |
| 🥉 **Low** | 10-17 | ~600 | Pain point solving, pilot projects |
| ⚠️ **Very Low** | <10 | ~166 | Long-term nurturing, education |

### **3. AI Proposal Generation**

**Endpoint:** `POST /api/proposals/generate`

**Request:**
```json
{
  "city_code": "401307",
  "focus_area": "general"  // or: structural, leadership, feasibility
}
```

**Response:**
```json
{
  "city_code": "401307",
  "proposal_text": "Subject: ...\n\nDear Mayor...",
  "generated_at": "2026-02-14T05:12:42"
}
```

---

## Sales Strategy by Tier

### 🏆 **Top Tier (33-37 points) - ~150 municipalities**

**Profile:**
- Advanced DX prefectures (Tokyo, Osaka, Fukuoka, etc.)
- Large populations (>500k)
- DX departments established
- Cloud migration in progress/complete

**Messaging:**
- Position as "model city" / "innovation leader"
- Showcase advanced features (Zoom Phone, Zoom Rooms, Workplace)
- Enterprise-scale deployment
- Global collaboration capabilities

**Sample Proposal Keywords:**
- "Global engagement"
- "Transforming business"
- "Advanced innovation"
- "Becoming a model city"

**Priority:** HIGH - Close rate ~40-50%

**Recommended Products:**
- Zoom Workplace (unified platform)
- Zoom Phone (full deployment)
- Zoom Rooms (hybrid work)

---

### 🥇 **High Tier (25-32 points) - ~400 municipalities**

**Profile:**
- Regional capitals / Core cities (中核市)
- Moderate DX investment
- Some leadership commitment
- Good fiscal health

**Messaging:**
- Peer success stories (show regional leaders)
- Proven ROI from similar-sized cities
- Phased implementation
- Cost-benefit analysis

**Sample Proposal Keywords:**
- "Join leading cities"
- "Proven results"
- "Regional collaboration"
- "Efficient government"

**Priority:** MEDIUM-HIGH - Close rate ~25-35%

**Recommended Products:**
- Zoom Meetings (department-level)
- Zoom Webinars (citizen engagement)
- Zoom Phone (pilot departments)

---

### 🥈 **Medium Tier (18-24 points) - ~600 municipalities**

**Profile:**
- Standard cities (一般市)
- Limited DX budget
- Starting digital transformation
- Structural pressures building

**Messaging:**
- "Start small" approach
- Quick wins & immediate pain points
- Low-risk pilot projects
- Minimal training required

**Sample Proposal Keywords:**
- "Starting Small approach"
- "Immediate pain relief"
- "Pilot project"
- "Quick implementation"

**Priority:** MEDIUM - Close rate ~15-20%

**Recommended Products:**
- Zoom Meetings (single department pilot)
- Zoom Team Chat (communication improvement)
- Training & support package

---

### 🥉 **Low Tier (10-17 points) - ~600 municipalities**

**Profile:**
- Small towns (町)
- Minimal DX activity
- Tight budgets
- Limited IT staff

**Messaging:**
- Solve specific pain points (e.g., remote meetings during COVID)
- Minimal setup, maximum benefit
- Free tier → paid migration path
- Education & handholding

**Sample Proposal Keywords:**
- "Small-town focus"
- "Initial steps"
- "Simple to use"
- "Affordable solution"

**Priority:** LOW - Close rate ~5-10%

**Recommended Products:**
- Zoom Meetings Basic (free) → Pro upgrade
- Consultation & training
- Simple use cases (council meetings, citizen townhalls)

---

### ⚠️ **Very Low (<10 points) - ~166 municipalities**

**Profile:**
- Very small villages (村)
- Aging populations
- No DX infrastructure
- Minimal digital literacy

**Strategy:**
- Long-term nurturing (12-24 months)
- Education-first approach
- Wait for government mandates
- Partner with prefecture

**Priority:** VERY LOW - Defer to prefecture/regional initiatives

---

## Using the AI Proposal System

### **Step 1: Identify Target Municipality**

Query the scores API:
```bash
GET /api/scores/map/all  # Get all scores
GET /api/scores/401307   # Get Fukuoka City details
```

### **Step 2: Generate Customized Proposal**

```bash
curl -X POST http://localhost:8000/api/proposals/generate \
  -H "Content-Type: application/json" \
  -d '{
    "city_code": "401307",
    "focus_area": "general"
  }'
```

### **Step 3: Review & Customize**

- AI generates ~400-1000 character proposal in Japanese
- Review for accuracy (AI is good but not perfect)
- Add specific contact info, pricing, next steps
- Personalize with mayor's name, recent news

### **Step 4: Send & Track**

- Email to municipality contact
- Log in CRM
- Follow up in 1 week
- Track response rate by score tier

---

## AI Proposal Examples

### **Example 1: Fukuoka City (Score: 37/100 - Top Tier)**

```
Subject: 福岡市にZoomを導入 - Pain Point解決と革新を起源とするグローバルエンゲージメント

Dear Mayor [Last Name],

福岡市の主要要因は、ビジネスや教育、医療分野で構造的圧力が高く感じられているようです。
Zoomを導入することで、市民との間でより深いつながりを作成し、グローバルなエンゲージメントを促進できます。

みなさんと Zoom で即座に会いましょう。

Best regards,
[Your Name]
```

**Translation:** "Introducing Zoom to Fukuoka City - Solving Pain Points and Empowering Innovation. The city faces structural pressure in business, education, and medical fields. Zoom can create deeper connections with citizens and promote global engagement."

---

### **Example 2: Sapporo City (Score: 22/100 - Medium Tier)**

```
Subject: Zoom for 札幌市 - Transforming Communication with Innovation

Dear Mayor,

札幌市の citizens の間でビジネスや教育、健康など、さまざまな分野でのコミュニケーションを改善するための
Zoom を取り入れてみませんか。

私たちの分析によると、札幌市では Structural Pressure は高くなっていますが、
Budget/Feasibility が良いです。Zoom の Starting Small アプローチを検討してみましょう。
```

**Translation:** "Zoom for Sapporo - Let's improve communication across business, education, health. Our analysis shows high structural pressure but good budget/feasibility. Let's consider Zoom's Starting Small approach."

---

### **Example 3: Small Town (Score: 15/100 - Low Tier)**

```
Subject: Zoom for 小-town Japan: Enhancing Local Communication

Dear Mayor [Last Name],

小規模な自治体には、強力なネットワークは非常に重要です。
Zoom は、遠隔のコミュニケーションを容易にする利便性があり、地域経済発展に貢献する可能性があります。

私たちの提案では、小規模自治体の初期ステップとして Zoom を採用し、
日常業務やコミュニティとの関わりを改善します。
```

**Translation:** "Zoom for small-town Japan. Strong networks are critical for small municipalities. Zoom can facilitate remote communication and contribute to local economic development. We propose adopting Zoom as an initial step to improve daily operations."

---

## Best Practices

### **DO:**
✅ Use AI as a **starting point**, not final output
✅ Verify city details (mayor name, recent news)
✅ Add specific pricing, timeline, next steps
✅ A/B test proposals across similar-scored cities
✅ Track which score tiers convert best
✅ Adjust prompts based on learnings

### **DON'T:**
❌ Send AI proposals verbatim without review
❌ Ignore cultural context or recent events
❌ Over-promise features not yet available
❌ Use English translations in Japanese proposals
❌ Target very low-scoring villages aggressively

---

## Performance Metrics (Expected)

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Proposals Generated | 100/month | 0 (new) | 🟡 Ramp-up |
| Response Rate | 15% | TBD | 🟡 Track |
| Top Tier Close Rate | 40% | TBD | 🟡 Track |
| Medium Tier Close Rate | 20% | TBD | 🟡 Track |
| Avg Time to Generate | <2 min | ~30 sec | ✅ Good |

---

## Next Steps

### **Week 1-2: Pilot Program**
1. Generate proposals for top 50 municipalities (scores >30)
2. Manual review & customization
3. Send to verified contacts
4. Track open/response rates

### **Week 3-4: Scale & Optimize**
1. Refine prompts based on feedback
2. A/B test messaging variations
3. Expand to high-tier (25-32) municipalities
4. Integrate with CRM

### **Month 2: Automation**
1. Automated proposal generation nightly
2. Email integration
3. Response tracking dashboard
4. ML-based prompt optimization

---

## Technical Details

**Model:** Llama 3.2 3B
**Hosting:** Local Ollama (Docker container)
**Latency:** ~30-60 seconds per proposal
**Cost:** $0 (self-hosted)
**Privacy:** All data stays local, no external API calls

**API Endpoint:** `http://localhost:8000/api/proposals/generate`
**Swagger Docs:** `http://localhost:8000/docs#/Proposals`

---

## Support & Questions

**Technical Issues:** Check API logs: `docker logs zoom-dx-api`
**Prompt Updates:** Edit `backend/routers/proposals.py` (line 58-77)
**Model Swap:** Change `OLLAMA_MODEL` in `backend/config.py`

---

**🎯 Ready to generate your first AI proposal? Start with the top 10 scoring cities!**
