# 🏠 Property Discovery Agent

An autonomous conversational AI agent that helps home buyers discover, analyze, compare, and rank residential properties based on natural language preferences. Developed as part of the **Digitomics Agentic AI Engineering Assignment**.

The system leverages **Google Gemini** as the reasoning engine, enabling the agent to autonomously determine which tools to invoke, gather information from multiple data sources, estimate live commute times, analyze neighbourhood characteristics, and generate explainable, ranked property recommendations.

---

## 🚀 Live Demo

**Application:** [Working Demo](https://property-discovery-agent.vercel.app/)

**Assignment deliverables:** [DELIVERABLES.md](DELIVERABLES.md)

---

## 🏗️ System Architecture

```
User (React Chat UI)
        │
        ▼
 FastAPI Backend
        │
        ▼
 Gemini Agent Loop
        │
 ┌──────┼───────────────┐
 ▼      ▼       ▼       ▼
Listings  Neighbourhood  Commute  Comparison
   │         │            │         │
   └─────────┴────────────┴─────────┘
                 │
                 ▼
      Ranked Property Recommendations
```

A detailed architecture diagram and workflow can be found in **docs/architecture.md**.

---

## 📊 Data Sources

| Component | Source |
|-----------|--------|
| Property Listings | Curated mock dataset (30 realistic Indian property listings) |
| Neighbourhood Information | Curated mock dataset (schools, metro, safety, amenities) |
| Commute Estimation | Live OSRM Routing API + OpenStreetMap Nominatim |
| Agent Reasoning | Google Gemini API |

> **Note:** Public APIs for platforms such as MagicBricks, Housing.com, and 99acres are not freely available. Therefore, realistic curated datasets are used for listings and neighbourhood information while keeping the reasoning engine fully autonomous.

---

# ✨ Features

- 🤖 Autonomous AI agent using Google Gemini
- 💬 Natural language conversation
- 🛠️ Dynamic tool selection (no hard-coded workflow)
- 🏘️ Property search and filtering
- 🚗 Live commute estimation
- 📍 Neighbourhood analysis
- ⚖️ Property comparison
- 📈 Explainable multi-factor property ranking
- 🔄 Multi-turn conversational support

---

# 📋 Prerequisites

- Python **3.11+**
- Node.js **18+**
- Google Gemini API Key

Generate a free API key from Google AI Studio:

[https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)

---

# ⚙️ Installation

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/Darshan-Hulamani/property-discovery-agent.git
cd property-discovery-agent
```

---

## 2️⃣ Backend Setup

```bash
cd backend

python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt

cp ../.env.example ../.env
```

Edit the `.env` file and add:

```env
GEMINI_API_KEY=your_api_key
```

---

## 3️⃣ Frontend Setup

```bash
cd frontend

npm install
npm run build
```

---

## ▶️ Run the Application

From the **backend** directory:

```bash
uvicorn app.main:app --reload --port 8000
```

Open:

```
http://localhost:8000
```

---

## 💻 Development Mode

Backend

```bash
cd backend

uvicorn app.main:app --reload --port 8000
```

Frontend

```bash
cd frontend

npm run dev
```

The React development server automatically proxies API requests to the FastAPI backend.

---

# 🔑 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| GEMINI_API_KEY | ✅ | Google Gemini API Key |
| GEMINI_MODEL | Optional | Gemini model (default: gemini-3.5-flash) |
| OSRM_BASE_URL | Optional | OSRM Routing Server URL |

---

# 🧰 Agent Tools

The agent autonomously selects and executes the appropriate tools based on the user's request.

| Tool | Purpose |
|------|---------|
| **search_properties** | Search listings using budget, city, BHK, locality and preferences |
| **get_property_details** | Retrieve detailed information for a selected property |
| **estimate_commute** | Calculate live driving time using OSRM |
| **get_neighbourhood_profile** | Retrieve neighbourhood insights including schools, safety and amenities |
| **compare_properties** | Compare shortlisted properties side-by-side |

Unlike traditional chatbots, the workflow is **agent-driven** rather than hard-coded.

---

# 💬 Example Prompts

```
Find a 3BHK apartment under ₹1.2 crore in Whitefield with good schools nearby.
```

```
My office is in Electronic City. Which shortlisted properties have the shortest commute?
```

```
Show me affordable 2BHK apartments in Marathahalli under ₹80 lakh.
```

```
Compare the top three recommended properties.
```

---

# ☁️ Deployment

The live application is deployed on **Vercel**.

For users who wish to self-host the project, deployment instructions for **Render** are provided below.

1. Push the repository to GitHub.
2. Create a new **Render Web Service**.
3. Configure:

**Build Command**

```bash
pip install -r backend/requirements.txt && cd frontend && npm install && npm run build
```

**Start Command**

```bash
cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Root Directory**

```
Repository Root
```

4. Add the environment variable:

```
GEMINI_API_KEY
```

5. Deploy the application.

Alternatively, use the included **render.yaml** blueprint.

---

# 📁 Project Structure

```
property-discovery-agent/
│
├── backend/
│   ├── app/
│   │   ├── agent/
│   │   ├── tools/
│   │   └── main.py
│   │
│   └── data/
│
├── frontend/
│
├── docs/
│
├── .env.example
├── render.yaml
└── README.md
```

---

# 🛠️ Technology Stack

- React
- Vite
- FastAPI
- Google Gemini API
- Python
- JavaScript
- OpenStreetMap Nominatim
- OSRM Routing API
- Render

---

# 📄 License

This project was developed as part of the **Digitomics Agentic AI Engineering Assignment** and is released under the **MIT License**.
