# Property Discovery Agent — Approach & Write-up

**Author:** [Darshan Hulamani](https://github.com/Darshan-Hulamani/).
**Assignment:** Digitomics Agentic AI Engineering — Autonomous Property-Discovery Agent  
**Date:** July 2026

## 1. Problem & approach

Home buyers in India spend months manually comparing listings across MagicBricks, 99acres, Housing.com, plus school ratings, commute times, and neighbourhood safety. This agent automates that multi-source reasoning in a single conversational interface.

**Approach:** A Gemini-powered autonomous agent with five function-calling tools. The LLM decides which tools to invoke based on the user's natural-language preferences — not a fixed pipeline. After gathering evidence, it ranks candidates and explains each pick against the buyer's stated priorities.

## 2. Tools & data sources

| Tool | Purpose | Live or mock |
|------|---------|--------------|
| `search_properties` | Filter listings by city, budget, BHK, locality, tags | Mock (30 curated Indian listings) |
| `get_property_details` | Deep dive on one property | Mock |
| `estimate_commute` | Driving time to workplace/landmark | **Live OSRM** + Nominatim geocoding |
| `get_neighbourhood_profile` | Schools, safety, metro, amenities | Mock (curated per-locality profiles) |
| `compare_properties` | Side-by-side finalist comparison | Derived from mock data |

**Why mock listings?** No reliable free public API exists for Indian property portals. Scraping would be fragile and likely violate terms of service. The assignment explicitly values honesty: a smaller, real, well-reasoned agent beats an over-scoped demo that doesn't run.

**Why OSRM for commute?** It's free, requires no API key, and provides real routing geometry. When a buyer mentions "office in Electronic City," the agent calls `estimate_commute` with live coordinates.

## 3. Ranking methodology

Ranking is **LLM reasoning over tool outputs**, not a hidden Python scorer. The system prompt instructs Gemini to:

1. Weight budget fit, locality match, commute (when computed), school/safety scores, and property attributes
2. Produce a top 3–5 shortlist with bullet justifications tied to user priorities
3. Include a "Trade-offs" section for honest compromise analysis
4. Disclose data sources in "Data notes"

On follow-ups ("what about commute to Electronic City?" or "cheaper options in Marathahalli?"), the agent calls only the relevant tools and updates its recommendations.

## 4. Architecture

React chat UI → FastAPI `/api/chat` → Gemini agent loop → tool registry → data sources → ranked markdown response.

Session state is in-memory (per `session_id`). Tool trace is optionally exposed in the UI to demonstrate autonomous tool use during evaluation.

## 5. Trade-offs

| Decision | Trade-off |
|----------|-----------|
| Mock listings | Fast, reliable demo; not real marketplace data |
| Gemini Flash | Free tier, fast; rate limits on heavy use |
| In-memory sessions | Simple deploy; no persistence across restarts |
| Single Render service | One deploy artifact; frontend rebuilt on each deploy |
| OSRM public instance | Free but shared; may rate-limit under load |

## 6. What I'd improve with more time

1. **Real listing ingestion** — Partner API or scheduled ETL from licensed data providers
2. **Persistent sessions** — Redis or PostgreSQL for conversation history
3. **Google Maps Distance Matrix** — More accurate Bangalore traffic-aware commute
4. **Structured output** — JSON schema for shortlist cards in the React UI (not just markdown)
5. **Evaluation suite** — Automated tests for tool selection patterns and ranking consistency
6. **Multi-city expansion** — More listings and neighbourhood profiles for tier-2 cities

## 7. Demo scenarios

1. *Initial search:* "3BHK under ₹1.2 Cr in Whitefield, good schools, metro nearby"  
   → Agent calls `search_properties`, `get_neighbourhood_profile`, returns ranked shortlist.

2. *Commute follow-up:* "Office is in Electronic City"  
   → Agent calls `estimate_commute` for top candidates, re-ranks with commute context.

3. *Refinement:* "Cheaper 2BHK in Marathahalli under ₹80 lakh"  
   → Agent calls `search_properties` with updated filters, compares with prior picks.

---

*Listings and neighbourhood data: curated demo dataset. Commute: live OSRM routing. Agent: live Google Gemini API.*
