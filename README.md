# 🔮 DataWhisperer
### Natural Language Database Intelligence Agent
*Built with Google ADK + SQLite MCP Server*

---

DataWhisperer is an AI agent that lets you query a live SQLite e-commerce database in plain English. It uses the **Model Context Protocol (MCP)** to connect to an `mcp-server-sqlite` instance, translates your questions into SQL, executes them, and returns sharp business insights — all through a beautiful dark terminal-style UI.

## Architecture

```
User (Browser)
    │
    ▼
FastAPI Server (main.py)
    │
    ▼
Google ADK Agent (LlmAgent with Gemini 2.0 Flash)
    │
    ▼ MCP Protocol (stdio)
mcp-server-sqlite
    │
    ▼
SQLite Database (ecommerce.db)
    └── categories, products, customers, orders, order_items
```

**MCP Tool Used:** `mcp-server-sqlite` from `modelcontextprotocol/servers`  
**Tools exposed:** `list_tables`, `describe_table`, `read_query`, `write_query`, `create_table`

---

## Dataset

The database is pre-seeded with realistic Indian e-commerce data:

| Table | Rows | Description |
|-------|------|-------------|
| `categories` | 8 | Electronics, Apparel, Books, etc. |
| `products` | 37 | With price, cost, stock, rating |
| `customers` | 800 | 12 Indian cities, 4 loyalty tiers |
| `orders` | 3,500 | 18 months of transactions |
| `order_items` | ~7,000 | Line items with discounts |

---

## Local Setup

### Prerequisites
- Python 3.12+
- `uv` (for running MCP server): `pip install uv`
- Google API Key (Gemini): https://aistudio.google.com/app/apikey

### Step 1 — Clone & Install

```bash
git clone <your-repo-url>
cd datawhisperer

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### Step 2 — Configure Environment

```bash
cp .env.example .env
# Edit .env and set your GOOGLE_API_KEY
```

### Step 3 — Seed the Database

```bash
python setup/seed_db.py
```

You should see:
```
✅ Database seeded at: ./data/ecommerce.db
   → 37 products across 8 categories
   → 800 customers across 12 cities
   → 3,500 orders with line items
```

### Step 4 — Run Locally

```bash
python main.py
```

Open: **http://localhost:8080**

---

## Cloud Run Deployment (Public URL)

### Prerequisites
- Google Cloud project with billing enabled
- `gcloud` CLI installed and authenticated
- `GOOGLE_API_KEY` exported in your shell

### Deploy in 3 Commands

```bash
# 1. Authenticate
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# 2. Set your API key
export GOOGLE_API_KEY=your_gemini_api_key_here

# 3. Deploy
chmod +x deploy.sh
./deploy.sh
```

The script will:
1. Enable required GCP APIs
2. Build the Docker image with Cloud Build
3. Push to Google Container Registry
4. Deploy to Cloud Run (publicly accessible, no auth required)
5. Print your **public URL**

### Manual Deploy (Alternative)

```bash
# Build image
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/datawhisperer .

# Deploy
gcloud run deploy datawhisperer \
  --image gcr.io/YOUR_PROJECT_ID/datawhisperer \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 1Gi \
  --set-env-vars "GOOGLE_API_KEY=YOUR_KEY,DB_PATH=/app/data/ecommerce.db"
```

---

## Sample Queries to Demo

| Question | What it demonstrates |
|----------|---------------------|
| "Which city generates the most revenue?" | GROUP BY + SUM, JOIN across tables |
| "Top 5 products by profit margin" | Computed columns, multi-table JOIN |
| "Customers inactive for 90 days" | Date arithmetic, subqueries |
| "Monthly revenue trend last 6 months" | Time-series aggregation |
| "Return rate by product category" | Percentage calculation, CASE statements |
| "Average order value by payment method" | Simple GROUP BY with AVG |
| "Which products are low on stock?" | WHERE filter on inventory |
| "Revenue breakdown by customer tier" | JOIN customers → orders |

---

## Project Structure

```
datawhisperer/
├── main.py                        # FastAPI server + SSE streaming
├── requirements.txt
├── Dockerfile
├── deploy.sh                      # One-command Cloud Run deploy
├── .env.example
├── setup/
│   └── seed_db.py                 # Database seeder (run once)
├── data/
│   └── ecommerce.db               # Generated SQLite database
├── static/
│   └── index.html                 # Full frontend UI
└── adk_agent/
    └── datawhisperer_app/
        ├── __init__.py
        └── agent.py               # ADK LlmAgent with MCP toolset
```

---

## How MCP Works Here

The agent uses `MCPToolset` with `StdioServerParameters` to spawn `mcp-server-sqlite` as a child process:

```python
mcp_toolset = MCPToolset(
    connection_params=StdioServerParameters(
        command="uvx",
        args=["mcp-server-sqlite", "--db-path", DB_PATH],
    )
)
```

The MCP server exposes these tools to the agent:
- **`list_tables`** — discover what tables exist
- **`describe_table`** — inspect columns and types
- **`read_query`** — execute SELECT statements
- **`write_query`** — INSERT/UPDATE/DELETE (not used in this demo)

The agent autonomously decides which tools to call, constructs the SQL, executes it via MCP, and synthesizes the result into a natural language response.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| AI Agent | Google ADK (LlmAgent) |
| LLM | Gemini 2.0 Flash |
| MCP Server | `mcp-server-sqlite` (official MCP) |
| Backend | FastAPI + SSE streaming |
| Database | SQLite |
| Frontend | Vanilla JS + CSS (no framework) |
| Deploy | Google Cloud Run |

---

*Built for the MCP Agent Project Submission*
