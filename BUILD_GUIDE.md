# Property Discovery Agent - Build Guide

This guide explains how to run, verify, and deploy the current full-stack Property Discovery Agent.

## Tech Stack

- Frontend: React 19, TypeScript, Vite, React Markdown, Leaflet, React Leaflet
- Backend: FastAPI, Pydantic, Google GenAI SDK, HTTPX, Python dotenv
- Agent: Gemini function calling with a tool registry and session memory
- Data: curated JSON listings and neighbourhood profiles
- Live integration: OSRM routing and Nominatim geocoding fallback

## Project Structure

```text
property-discovery-agent/
  api/index.py                       # Vercel Python entrypoint
  backend/
    app/main.py                      # FastAPI app
    app/models.py                    # Pydantic request/response schemas
    app/agent/prompts.py             # Agent system prompt
    app/agent/loop.py                # Gemini tool-calling loop
    app/tools/registry.py            # Tool declarations and dispatcher
    app/tools/search_listings.py     # Search and ranked shortlist tool
    app/tools/ranking.py             # Weighted scoring engine
    app/tools/property_details.py    # Enriched property details
    app/tools/neighbourhood.py       # Curated locality profile
    app/tools/commute.py             # Live commute estimation
    app/tools/compare.py             # Side-by-side comparison
    app/tools/mortgage_calculator.py # EMI calculator
    app/tools/profile_memory.py      # Session buyer memory
    data/listings.json
    data/neighbourhoods.json
  frontend/
    public/images/                  # Property imagery copied into dist/images
    src/App.tsx
    src/components/Chat.tsx
    src/components/PropertyCard.tsx
    src/components/MapComponent.tsx
  docs/writeup.md
```

## Environment

Create a root `.env` file:

```env
GEMINI_API_KEY=your_google_ai_studio_key
GEMINI_MODEL=gemini-2.5-flash
OSRM_BASE_URL=https://router.project-osrm.org
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

`GEMINI_MODEL` is optional; the app defaults to `gemini-2.5-flash` if it is not set.

## Install Dependencies

Backend:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Frontend:

```powershell
cd frontend
npm install
```

On Windows, if PowerShell blocks `npm`, run `npm.cmd` instead.

## Run Locally

Terminal 1:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Terminal 2:

```powershell
cd frontend
npm.cmd run dev
```

Open `http://localhost:5173`.

## Verify

Frontend production build:

```powershell
cd frontend
npm.cmd run build
```

Backend compile check:

```powershell
.\backend\.venv\Scripts\python.exe -m compileall backend\app
```

Targeted ranking check:

```powershell
.\backend\.venv\Scripts\python.exe -c "import sys,json; sys.path.insert(0,'backend'); from app.tools.search_listings import search_properties; print(json.dumps(search_properties(city='Bangalore', locality='Whitefield', max_budget_inr=12000000, min_bhk=3, must_have_tags=['metro_nearby','schools_nearby'], limit=5), indent=2))"
```

Static image serving after a frontend build:

```powershell
.\backend\.venv\Scripts\python.exe -c "import sys; sys.path.insert(0,'backend'); from fastapi.testclient import TestClient; from app.main import app; c=TestClient(app); r=c.get('/images/luxury_apartment_1_1783011988895.png'); print(r.status_code, r.headers.get('content-type'), len(r.content))"
```

Expected result: status `200`, content type `image/png`.

## Deployment Notes

- Vercel uses `api/index.py` for the backend entrypoint and Vite for the frontend static build.
- Render or a single FastAPI service can serve the built SPA from `frontend/dist`.
- FastAPI mounts `/assets` for bundled JS/CSS and `/images` for copied public images when `frontend/dist` exists.
- Configure production `CORS_ALLOWED_ORIGINS` to the deployed frontend domain.

## Demo Prompts

- `3BHK under Rs 1.2 Cr in Whitefield with metro and good schools.`
- `I work in Electronic City. Rank options by commute and family safety.`
- `Find affordable 2BHK homes for rental investment near an IT corridor.`
- `Compare ready-to-move gated communities with strong schools.`
