# AI4MH — AI-Powered Mental Health Crisis Monitoring

**Google Summer of Code 2026 | ISSR, The University of Alabama**  
**Contributor:** Om Pradip Chougule  
**GitHub:** https://github.com/ironman1947

---

## Project Overview

AI4MH is a community-level mental health crisis monitoring system that analyzes publicly available social media conversations to detect early warning signs of mental health distress across geographic regions.

This system does **not** track individuals. It monitors aggregated public language patterns at the county or city level to help public health agencies identify emerging crises and allocate resources proactively.

---

## Core Components

### 1. Crisis Lexicon
A structured keyword and coded language database covering:
- Explicit mental health distress language
- Suicide and self-harm related terms
- Substance use related language
- Coded and slang terms used in online communities

### 2. Sentiment Analysis (VADER)
- Scores each post from -1 (most negative) to +1 (most positive)
- Compares current 72-hour window against 30-day regional baseline
- Detects significant drops in average sentiment per county

### 3. Crisis Signal Score (CSS) Engine
Combines three inputs into a single actionable score:
- **Sentiment Intensity (SI)** — how negative is the language?
- **Volume Spike Score (VS)** — how sudden is the increase in posts?
- **Geographic Clustering (GC)** — are affected counties neighbours?

```
CSS = (0.4 × SI) + (0.4 × VS) + (0.2 × GC)
```

### 4. Risk Controls
- Bot detection (posting time patterns + language similarity)
- Media spike detection (Google News API cross-check)
- Sparse data flagging (rural county handling)

### 5. Escalation Engine
Three-level decision system:
- **Level 1 (Monitor):** CSS 0.5–0.7 → logged, weekly review
- **Level 2 (Review):** CSS 0.7–0.85 → analyst alerted within 24 hours
- **Level 3 (Escalate):** CSS > 0.85 + confidence > 70% → immediate human review

### 6. Longitudinal Memory Store
- Stores daily CSS scores per county in SQLite
- Enables trend analysis over weeks and months
- Powers predictive escalation indicators

### 7. Public Health Dashboard
- Interactive heatmaps using Folium and GeoPandas
- Real-time and historical trend visualization using Plotly
- Built for public health agency use

---

## Tech Stack

| Component | Technology |
|---|---|
| NLP / Sentiment | VADER, spaCy, HuggingFace Transformers |
| Topic Modelling | LDA (gensim), BERT |
| Data Collection | PRAW (Reddit), Twitter API v2, Spotify API |
| Geospatial | GeoPandas, Folium, Leaflet.js |
| Dashboard | Plotly, Dash |
| Backend | FastAPI |
| Storage | SQLite (longitudinal memory store) |
| Analysis | Pandas, Seaborn, SciPy |

---

## Repository Structure

```
ai4mh-crisis-monitoring/
├── README.md
├── crisis_lexicon.py        # Crisis keyword and coded language database
├── sentiment_analysis.py   # VADER sentiment scoring pipeline
├── css_engine.py           # Crisis Signal Score calculation
├── bot_detection.py        # Bot amplification detection
├── geospatial_mapper.py    # County-level heatmap generation
├── dashboard.py            # Plotly dashboard scaffold
├── memory_store.py         # Longitudinal SQLite storage
└── sample_data/
    ├── mock_reddit_posts.json
    └── mock_county_baseline.json
```

---

## Ethical Considerations

- No personally identifiable information is collected or stored
- System operates on aggregated public data only
- All escalations require human review before real-world action
- Designed to comply with IRB-approved research workflows
- Audit log maintained for full transparency and accountability

---

## Status

This repository is the early prototype developed as part of the GSoC 2026 application process. Active development will begin during the GSoC coding period.
