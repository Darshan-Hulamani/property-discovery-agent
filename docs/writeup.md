# Property Discovery Agent – Approach & Write-up

**Author:** Darshan Hulamani  
**Assignment:** Digitomics Agentic AI Engineering – Autonomous Property Discovery Agent  
**Date:** July 2026

---

# 1. Project Overview

Property Discovery Agent is an autonomous conversational AI application that helps home buyers discover, analyze, compare, and rank residential properties based on natural language preferences.

The system uses a Large Language Model (Google Gemini) as the reasoning engine to understand user intent, decide which tools to invoke, retrieve relevant information, and generate explainable property recommendations. Instead of following a fixed workflow, the agent dynamically selects tools depending on the user's request, making the interaction more natural and flexible.

---

# 2. System Architecture

```text
React/Vite Frontend
        │
        ▼
 FastAPI Backend
        │
        ▼
 Gemini Agent
        │
 ┌──────┼───────────────┐
 ▼      ▼       ▼       ▼
Property  Neighbourhood  Commute  Comparison
 Search      Data         API       Tools
        │
        ▼
 Ranked Property Recommendations
```

The frontend provides a conversational interface, while the FastAPI backend manages agent execution, tool invocation, property ranking, and response generation.

---

# 3. Agent Workflow

The agent follows an autonomous reasoning workflow instead of a hard-coded pipeline.

For every user request, it:

- Understands the user's intent and preferences.
- Determines which tools are required.
- Retrieves relevant property and neighbourhood information.
- Computes additional signals such as commute time when required.
- Evaluates candidate properties using a weighted ranking model.
- Generates an explainable shortlist with clear reasoning.

The agent is instructed to avoid fabricating property details and uses only information returned by the available tools.

---

# 4. Ranking Methodology

Properties are ranked using a deterministic weighted scoring model based on multiple factors.

| Ranking Signal | Weight |
|---------------|--------|
| Budget Match | 22% |
| BHK Match | 10% |
| Locality Match | 12% |
| School Score | 12% |
| Safety Score | 12% |
| Metro Accessibility | 10% |
| User Preference Tags | 12% |
| Possession Status | 4% |
| Investment Potential | 6% |

The final recommendation includes both the overall score and a concise explanation describing why each property matches the buyer's preferences.

---

# 5. Agent Tools

| Tool | Purpose |
|------|---------|
| **search_properties** | Search and rank properties based on user preferences |
| **get_property_details** | Retrieve complete information about a selected property |
| **estimate_commute** | Calculate live driving commute using OSRM |
| **get_neighbourhood_profile** | Retrieve neighbourhood information including schools, safety, metro, and amenities |
| **compare_properties** | Compare shortlisted properties side-by-side |
| **calculate_mortgage** | Estimate EMI and affordability |
| **update_buyer_profile** | Maintain user preferences throughout the conversation |

---

# 6. Data Sources

The application combines curated datasets with live services.

- Property listings are provided through a curated dataset containing realistic Indian residential properties.
- Neighbourhood profiles include schools, safety, metro connectivity, and nearby amenities.
- Driving commute estimates are calculated using the live OSRM Routing API with OpenStreetMap geocoding.
- Conversational reasoning and tool orchestration are performed using Google Gemini.

---

# 7. Trade-offs

Due to the lack of freely available APIs from major real estate platforms such as MagicBricks, Housing.com, and 99acres, curated datasets were used for property listings and neighbourhood information.

However, live routing services were integrated to provide realistic commute estimates, ensuring that the application demonstrates genuine tool usage alongside autonomous reasoning.

The project prioritizes transparency by clearly distinguishing curated data from live services.

---

# 8. Future Improvements

Future enhancements could include:

- Integration with real estate listing APIs.
- Persistent user accounts and saved searches.
- Database-backed property storage using PostgreSQL.
- Advanced investment analytics and market trend prediction.
- Support for multiple LLM providers through a model abstraction layer.

---

The project demonstrates an autonomous AI agent capable of understanding natural language preferences, selecting appropriate tools, reasoning over multiple information sources, and producing explainable property recommendations through an interactive conversational interface.
