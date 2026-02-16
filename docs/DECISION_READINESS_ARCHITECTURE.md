# Decision Readiness Architecture: LocalGov DX Intelligence v3.0

## 🎯 Core Philosophy: CIO/CDO-Centric Evaluation
**From "Sales Push" (BANT) to "Decision Readiness" (Internal Logic)**

We do not measure "how easy it is to sell".
We measure **"how ready the municipality is to decide"**.

### The 5 Pillars of Decision (Total: 100 pts)

| Category | Points | Logic (CIO's Inner Monologue) | Data Source |
|----------|--------|-------------------------------|-------------|
| **1. Structural Pressure** | **30** | "We have no choice but to change." (Demographics, Fiscal) | e-Stat API |
| **2. Leadership Commitment** | **25** | " The Mayor said we must do this." (Policy Speech) | Official Site (PDF) + Ollama |
| **3. Peer Pressure** | **20** | "Everyone else is doing it." (Neighbor/Peer Adoption) | Internal DB + Digital Agency CSV |
| **4. Feasibility** | **15** | "We have the budget and tech to do it." (Cloud/Network) | Digital Agency CSV |
| **5. Accountability** | **10** | "I can explain this to the assembly/citizens." (KPI/Cases) | Google News RSS + Internal DB |

---

## 🏗️ Data Intelligence Architecture

```mermaid
graph TD
    subgraph Data_Layer [Free Data Sources]
        EStat[e-Stat API] -->|Population/Fiscal| DataLake
        Digi[Digital Agency CSV] -->|DX Structure/Online| DataLake
        Web[Official Sites] -->|Mayor Speech PDF| DataLake
        RSS[Google News] -->|Local News| DataLake
    end

    subgraph Intelligence_Layer [Lenovo Tiny AI Engine]
        DataLake --> Structural[1. Structural Scorer]
        DataLake --> Feasibility[4. Feasibility Scorer]
        
        Web --> Ollama[Ollama (Llama 3.2)]
        Web --> BERT[BERT Classifier (cl-tohoku)]
        
        Ollama --> Leadership[2. Leadership Scorer]
        BERT --> Leadership
        
        DataLake --> Peer[3. Peer Pressure Engine]
        DataLake --> Accountability[5. Accountability Scorer]
        
        Structural --> Calculator[Total Readiness Calculator]
        Leadership --> Calculator
        Peer --> Calculator
        Feasibility --> Calculator
        Accountability --> Calculator
    end

    subgraph Application_Layer [AWS Lightsail]
        Calculator --> DB[(PostgreSQL)]
        DB --> API[FastAPI]
        API --> UI[Next.js Dashboard]
        UI --> Heatmap[Deck.gl Map]
    end
```

---

## 🧠 Logic Details

### 1. Structural Pressure (30pts)
*Automatic calculation via e-Stat API*
- **Demographic (12pts)**: Depopulation rate > 20% (+6), Elderly ratio > 40% (+4).
- **Fiscal (12pts)**: Fiscal Strength Index < 0.3 (+6), Debt Ratio > 18% (+3).
- **Burnout (6pts)**: Staff reduction > 20% (+4).

### 2. Leadership Commitment (25pts)
*Hybrid AI Analysis (Ollama + BERT)*
- **Mayor's Voice (12pts)**: 
    - **BERT**: Classify "Commitment Level" (High/Medium/Low) -> Score 8/5/2.
    - **Ollama**: Extract specific quotes/context.
- **Org Structure (8pts)**: DX Department exists (+4), CIO appointed (+2).
- **Budget (5pts)**: "Supplementary Budget" mentioned (+3).

### 3. Peer Pressure (20pts)
*Comparative Analysis*
- **Peer Adoption (15pts)**: >50% of similar-size cities have Zoom (+10).
- **Gov Push (5pts)**: "Digital Garden City" selection (+3).

### 4. Feasibility (15pts)
*Readiness Check*
- **Tech (8pts)**: GovCloud Migrated (+4), LGWAN Connected (+2).
- **Funding (4pts)**: Budget secured (+3).
- **HR (3pts)**: IT Staff > 5 (+1).

### 5. Accountability (10pts)
*Explanation Logic*
- **Cases (6pts)**: 5+ similar successful cases (+4).
- **KPI (4pts)**: Clear numerical goals in policy (+2).

---

## 🛡️ Implementation Rules
1.  **No Tender Data**: We abandon costly/difficult tender data.
2.  **3-Node Rule**:
    *   **Mac**: Scrapers & Data Prep scripts.
    *   **Lenovo**: DB, Ollama, Scheduling.
    *   **AWS**: Read-Only UI.
3.  **Absolute Evaluation**: No ranking. A score of 80 means "Ready to Decide".

