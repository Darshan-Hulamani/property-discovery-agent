# Property Discovery Agent - Approach & Write-up

**Author:** [Darshan Hulamani](https://github.com/Darshan-Hulamani/)

**Assignment:** Digitomics Agentic AI Engineering - Autonomous Property-Discovery Agent

**Date:** July 2026

## 1. Project Analysis

The project is a full-stack AI property discovery product with a React/Vite frontend, FastAPI backend, Gemini tool-calling agent, curated Indian listings, neighbourhood profiles, live OSRM commute routing, and Leaflet maps.

What is good:
- Clear separation between UI, API, agent loop, tools, and data.
- Tool trace makes autonomous agent behaviour visible for evaluation.
- Curated listings include real property-like fields, coordinates, builders, possession status, price, tags, and neighbourhood context.
- Live commute routing adds one genuinely dynamic signal instead of relying entirely on mock data.
- The frontend now feels closer to a premium SaaS workspace, with map drawer, shortlist cards, loading states, dark mode, and mobile-first responsiveness.

What was weak:
- The original UI looked assignment-like and broke on smaller viewports.
- Search was mostly filtering, so the agent could not explain ranking in a deterministic way.
- Locality matching was too loose and could bury exact-area results under unrelated high-scoring alternatives.
- Static production serving did not expose `/images`, so built property images could break behind FastAPI.
- Documentation did not reflect the weighted ranking engine.

What should remain untouched:
- The overall FastAPI + React architecture is appropriate for a portfolio app.
- The tool registry pattern is simple and extensible.
- OSRM is a pragmatic live-data integration for a demo without paid map APIs.

What should be rewritten later:
- In-memory sessions should become persistent storage.
- Curated JSON should become a seed dataset loaded into PostgreSQL.
- Agent evals should be formalized instead of manually checking prompt scenarios.

## 2. Current Architecture

```text
React/Vite UI
  -> /api/chat
FastAPI app
  -> Gemini agent loop
  -> Tool registry
  -> search/ranking/details/neighbourhood/commute/compare/EMI tools
  -> curated JSON data + live OSRM routing
  -> markdown answer + structured property cards + tool trace
```

Session state is currently in memory per `session_id`. Buyer preferences are also tracked per session through the profile memory tool.

## 3. Agent Workflow

The system prompt now frames the agent as HomeScope AI, a premium Indian real estate consultant. For every turn it should detect intent, update buyer memory, clarify only when core information is missing, select relevant tools, reason from returned data, and produce a concise shortlist with trade-offs and one next question.

The agent is instructed to:
- Save city, budget, BHK, locality, commute destination, and must-have features immediately.
- Search first, then call details, neighbourhood, commute, compare, or EMI tools as needed.
- Never invent property IDs, coordinates, commute times, scores, builders, or amenities.
- Disclose that listings and neighbourhood profiles are curated demo data.

## 4. Ranking Methodology

Search results are now ranked by a deterministic weighted scoring engine:

| Signal | Weight |
|--------|--------|
| Budget match | 22% |
| BHK match | 10% |
| Locality match | 12% |
| School score | 12% |
| Safety score | 12% |
| Metro access | 10% |
| Preference tags | 12% |
| Possession | 4% |
| Investment potential | 6% |

Each result includes `score`, `score_breakdown`, and `score_reasons`. The LLM uses these outputs to explain why a property fits instead of inventing hidden reasoning.

Locality is treated as a primary search area. If the buyer asks for Whitefield, exact Whitefield results are shown first; fallback areas can appear only after the primary matches.

## 5. UI/UX Improvements

The interface has been redesigned as a premium advisor workspace:
- Sticky glass-style header with theme toggle.
- Product hero with key metrics.
- Advisor panel with chat, examples, loading skeletons, and tool trace.
- Modern property cards with images, scores, reasons, amenities, builder, possession, and map action.
- Responsive map drawer with Leaflet markers and score popups.
- Mobile layout with sticky input and full-screen map behaviour.

## 6. Data & Tools

| Tool | Purpose | Data source |
|------|---------|-------------|
| `search_properties` | Filter and rank listings | Curated dataset |
| `get_property_details` | Deep enriched property view | Curated dataset + ranking |
| `estimate_commute` | Driving commute to landmark/workplace | Live OSRM + Nominatim fallback |
| `get_neighbourhood_profile` | Safety, schools, metro, amenities | Curated profiles |
| `compare_properties` | Side-by-side finalist comparison | Curated dataset |
| `calculate_mortgage` | EMI and affordability estimate | Formula-based |
| `update_buyer_profile` | Session memory for buyer constraints | In-memory |

## 7. Model Recommendation

Gemini is acceptable for the current portfolio version because it has good function-calling support, low friction setup, and fast latency. For a production SaaS version, the best long-term approach would be provider abstraction with evaluation-based model selection.

Recommended path:
- Keep Gemini as the default demo model.
- Add a model adapter interface so OpenAI, Claude, or Gemini can be swapped without touching tools.
- Use automated evals to compare function-call accuracy, hallucination rate, latency, and cost.
- Consider OpenAI or Claude for stronger reasoning and tool reliability if the project becomes a production-grade product.

## 8. Additional Add-ons & Recommendations

- Add PostgreSQL with PostGIS for geospatial search and locality radius queries.
- Add Redis for session memory, cached commute results, and rate limiting.
- Add property favorites, compare board, shareable shortlist links, and PDF export.
- Add affordability, EMI, down-payment, stamp-duty, and maintenance-cost calculators.
- Add neighbourhood scorecards for walkability, schools, hospitals, safety, metro, traffic, and rental demand.
- Add market trends, price-per-sqft history, appreciation forecast, and rental yield estimates.
- Add structured JSON agent outputs to reduce markdown parsing and make UI cards fully reliable.
- Add automated agent evals for common buyer journeys and tool-selection correctness.
- Add Playwright visual tests for desktop and mobile layouts.
- Add error boundaries, retry states, API timeout handling, and empty-state guidance.
- Add authentication so users can save searches and shortlists.
- Add observability with request IDs, tool latency, model latency, failure rates, and prompt/version tracking.
- Add input moderation and guardrails around financial advice, legal claims, and unsupported live listing claims.
- Add deployment hardening: environment validation, health checks, CI builds, linting, and smoke tests.

## 9. Demo Scenarios

1. "3BHK under Rs 1.2 Cr in Whitefield with metro and good schools."
   The agent updates memory, calls `search_properties`, and returns a ranked shortlist with exact Whitefield results first.

2. "I work in Electronic City. Rank these by commute and family safety."
   The agent calls `estimate_commute` for relevant properties and explains commute trade-offs.

3. "Find affordable 2BHK homes for rental investment near an IT corridor."
   The agent maps the intent to budget-friendly, IT corridor, metro, and rental-demand signals.

4. "Show under-construction options only."
   The search tool filters by possession and returns only matching inventory.

---

Listings and neighbourhood data are curated demo data. Commute estimates use live OSRM routing when computed. Agent responses are generated through the configured Gemini model.
