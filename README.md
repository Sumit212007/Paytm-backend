# Paytm GrowthPilot Backend

> **AI Business Partner for Every Paytm Merchant**

Paytm GrowthPilot is an AI-powered business copilot designed for Paytm merchants. The backend analyzes merchant transaction patterns, detects anomalies and growth opportunities (such as revenue drops, underperforming hour windows, and customer churn), explains **WHY** it is happening, recommends the **NEXT BEST ACTION**, allows merchant approval, orchestrates automated campaign execution via **n8n**, and calculates campaign performance and return on investment (ROI).

---

## 1. Core Product Loop

```text
       DATA (Paytm Transactions & Customers)
                         ↓
                      OBSERVE
                         ↓
            IDENTIFY PROBLEM / OPPORTUNITY
                         ↓
               EXPLAIN WHY (Gemini AI)
                         ↓
            RECOMMEND ACTION (Pydantic Validated)
                         ↓
                MERCHANT APPROVAL
                         ↓
         CAMPAIGN EXECUTION (n8n Webhook & Paytm Push)
                         ↓
               CUSTOMER NOTIFICATION
                         ↓
                  MEASURE RESULTS
                         ↓
            AI ANALYZES RESULTS & ROI
                         ↓
                 NEXT OPPORTUNITY
```

---

## 2. Technology Stack

* **Backend Framework**: Python 3.11, FastAPI, Pydantic v2, Uvicorn
* **Database Layer**: PostgreSQL (Supabase) via SQLAlchemy ORM (with SQLite fallback for offline dev/testing)
* **AI Engine**: Google Gemini API (`google-generativeai` / `google-genai`)
* **Workflow Automation**: n8n Webhooks
* **Testing & Quality**: Pytest, TestClient, Httpx

---

## 3. Architecture & Responsibilities

```text
+------------------------------------------------------------------+
|                       FastAPI Application                        |
|                                                                  |
|  +-------------------+  +-------------------+  +--------------+  |
|  | Analytics Engine  |  | Anomaly Detector  |  | Segmentation |  |
|  +-------------------+  +-------------------+  +--------------+  |
|                                                                  |
|  +-------------------+  +-------------------+  +--------------+  |
|  | Recommendation    |  | Campaign Exec     |  | AI Assistant |  |
|  | Engine            |  | & Eligibility     |  | Engine       |  |
|  +-------------------+  +-------------------+  +--------------+  |
+------------------------------------------------------------------+
       |                  |                    |                |
       v                  v                    v                v
+--------------+  +---------------+  +-------------------+  +-------+
| PostgreSQL / |  | Google Gemini |  | n8n Automation    |  | Mock  |
| Supabase     |  | API           |  | Webhooks          |  | Notif |
+--------------+  +---------------+  +-------------------+  +-------+
```

* **FastAPI**: Main application backend, REST APIs, analytics calculation, business logic, recommendation validation, and campaign lifecycle management.
* **Supabase / PostgreSQL**: Persistent relational data store.
* **Google Gemini API**: Natural language reasoning, insight explanations, campaign generation, and multilingual conversational copilot (`english`, `hindi`, `hinglish`).
* **n8n**: External workflow automation layer triggered via FastAPI webhooks.
* **React (Future)**: Frontend client connecting to `/api/v1/` REST endpoints.

---

## 4. Directory Structure

```text
Paytm/
├── app/
│   ├── main.py                     # FastAPI application setup & lifespan
│   ├── core/
│   │   ├── config.py               # Pydantic environment configuration
│   │   ├── security.py             # CORS & security middleware
│   │   └── logging.py              # Structured logging
│   │
│   ├── database/
│   │   ├── connection.py           # SQLAlchemy engine & session factory
│   │   └── models.py               # Declarative ORM models (13 tables)
│   │
│   ├── schemas/                    # Pydantic v2 validation & response schemas
│   │   ├── merchant.py
│   │   ├── customer.py
│   │   ├── transaction.py
│   │   ├── analytics.py
│   │   ├── insight.py
│   │   ├── recommendation.py
│   │   ├── campaign.py
│   │   ├── notification.py
│   │   ├── assistant.py
│   │   └── dashboard.py
│   │
│   ├── services/                   # Core business domain logic
│   │   ├── analytics_service.py    # Revenue & hourly math calculations
│   │   ├── segmentation_service.py # Deterministic customer classifier
│   │   ├── anomaly_service.py      # Rule-based opportunity detector
│   │   ├── insight_service.py      # Insight synthesis & storage
│   │   ├── recommendation_service.py # AI action plans & approval flow
│   │   ├── campaign_service.py     # Campaign execution & measurement
│   │   ├── notification_service.py # Merchant & Mock Paytm Push dispatch
│   │   ├── ai_service.py           # Gemini reasoning & multilingual chat
│   │   ├── n8n_service.py          # n8n webhook dispatcher
│   │   ├── merchant_service.py
│   │   ├── customer_service.py
│   │   └── transaction_service.py
│   │
│   ├── integrations/
│   │   ├── gemini/
│   │   │   └── client.py           # Gemini API client wrapper
│   │   └── n8n/
│   │       └── client.py           # n8n HTTP webhook client
│   │
│   └── utils/
│       └── helpers.py              # Date ranges and math helpers
│
├── scripts/
│   └── seed_demo_data.py           # Realistic seed script for Sharma General Store
│
├── tests/
│   ├── conftest.py
│   ├── test_analytics.py
│   ├── test_segmentation.py
│   ├── test_recommendation_and_campaign.py
│   └── test_assistant_and_api.py
│
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── run.py                          # Application launcher
```

---

## 5. Setup & Installation

### Step 1: Clone & Setup Environment

```bash
# Clone the repository
cd Paytm

# Create python virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

Create `.env` file by copying `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` file values:

```env
PROJECT_NAME="Paytm GrowthPilot Backend"
VERSION="1.0.0"
API_V1_STR="/api/v1"
ENVIRONMENT="development"
DEBUG=true

# Supabase PostgreSQL (or fallback to sqlite for local offline dev)
DATABASE_URL="postgresql://postgres:your_password@db.xxxx.supabase.co:5432/postgres"
SUPABASE_URL="https://your-project.supabase.co"
SUPABASE_KEY="your-anon-key"

# Google Gemini API
GEMINI_API_KEY="your_gemini_api_key"

# n8n Orchestration Layer
N8N_BASE_URL="http://localhost:5678"
N8N_CAMPAIGN_WEBHOOK_URL="http://localhost:5678/webhook/growthpilot-campaign"
N8N_ANALYSIS_WEBHOOK_URL="http://localhost:5678/webhook/growthpilot-analysis"
```

---

## 6. Database Seeding & Running Server

### Seed Demo Data for Hackathon Demo

Run the seed script to populate realistic data for **Sharma General Store**:

```bash
python scripts/seed_demo_data.py
```

*What the seed script creates:*
* Merchant: **Sharma General Store** (`mer_sharma_001`)
* 200 Customers (137 inactive regular customers, 40 regulars, 23 new)
* 14 days of transactions intentionally featuring a **~16% revenue drop** and **4 PM – 7 PM slow hours**
* Initial active insight (`ins_sales_drop_001`)
* Initial pending recommendation (`rec_winback_001` - ₹50 OFF above ₹300)

### Start FastAPI Backend Server

```bash
python run.py
```

Or using Uvicorn directly:

```bash
uvicorn app.main:app --reload --port 8000
```

Access Swagger API Documentation at: **`http://127.0.0.1:8000/docs`**

---

## 7. Complete Step-by-Step Hackathon Demo Flow

1. **Open Merchant Dashboard**:
   ```http
   GET http://127.0.0.1:8000/api/v1/dashboard/mer_sharma_001
   ```
   *Response*: Returns today's sales, active sales drop insight, pending recommendation, and recent campaign history.

2. **Trigger Periodic Analysis (n8n entrypoint)**:
   ```http
   POST http://127.0.0.1:8000/api/v1/automation/analyze/mer_sharma_001
   ```
   *Response*: Detects revenue drop & underperforming 4 PM - 7 PM window, invokes Gemini for Hinglish explanation, and drafts recommendation.

3. **Merchant Approves Recommendation**:
   ```http
   POST http://127.0.0.1:8000/api/v1/recommendations/rec_winback_001/approve
   ```
   *Response*: Approves recommendation, creates active campaign, filters 137 eligible inactive regular customers, dispatches mock Paytm customer push notifications, and triggers n8n campaign webhook.

4. **Measure Campaign Performance**:
   ```http
   POST http://127.0.0.1:8000/api/v1/automation/measure-campaign/<campaign_id>
   ```
   *Response*: Calculates redemptions, generated revenue (e.g. ₹15,120), revenue lift (+18.5%), and ROI (+620%). Sends merchant result notification.

5. **Ask AI Copilot Assistant**:
   ```http
   POST http://127.0.0.1:8000/api/v1/assistant/chat
   Content-Type: application/json

   {
     "merchant_id": "mer_sharma_001",
     "message": "Aaj sales kam kyu hui?",
     "language": "hinglish"
   }
   ```
   *Response*:
   ```json
   {
     "message": "Aaj aapki sales main 4 PM–7 PM ke beech kam hui hain (15.9% decline). GrowthPilot has an active win-back offer for 137 inactive customers.",
     "language": "hinglish",
     "audio_ready": true,
     "suggested_action": {
       "type": "view_recommendation",
       "id": "rec_winback_001"
     }
   }
   ```

---

## 8. Running Automated Tests

Run the full Pytest suite:

```bash
python -m pytest -v
```

Tests cover:
* Math analytics & percentage change calculations
* Rule-based customer segmentation (new, regular, loyal, inactive, high value)
* Recommendation generation & merchant approval flow
* Campaign measurement & ROI calculation
* AI Assistant context passing and endpoint integration
