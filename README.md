# Pulse Backend

FastAPI backend for scoring pipeline risk and generating AI-powered re-engagement emails.


**Api Documentation** = [pulse_api_docs.pdf](https://github.com/user-attachments/files/27939049/pulse_api_docs.pdf)


## Tech Stack

- **FastAPI** for REST API
- **Python 3.10+**
- **Groq API** (Llama 3.3 70B) for email generation
- Deployed on **Railway**

## Local Development

### Prerequisites

- Python 3.10+
- pip

### Setup

1. Clone the repository
```bash
git clone https://github.com/yourusername/pulse-backend.git
cd pulse-backend
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory
   GROQ_KEY=your_groq_api_key_here

4. 4. Generate synthetic deal data
```bash
python data_generator.py
```

This creates `deals.json` with 200 realistic CRM deals.

5. Start the development server
```bash
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

API docs: `http://localhost:8000/docs`

## Environment Variables
| `GROQ_API_KEY` | Groq API key for LLM email generation | `gsk_...` |
| `PORT` | Port to run the server (set by Railway in prod) | `8000` |

## Project Structure
```
.
├── main.py              # FastAPI app and routes
├── scoring.py           # Risk scoring engine
├── email_draft.py       # AI email generation
├── data_generator.py    # Synthetic CRM data generator
├── deals.json           # Generated deal data
├── requirements.txt     # Python dependencies
└── .env                 # Environment variables (not committed)
```
## API Endpoints

### `GET /api/deals`
Returns all deals with risk scores, sorted by risk (descending).

**Response:**
```json
[
  {
    "id": "DEAL-0001",
    "account_name": "Acme Corp",
    "amount": 95000,
    "score": 84,
    "bucket": "red",
    "breakdown": [...],
    ...
  }
]
```

### `GET /api/deals/{id}`
Returns a single deal with full detail.

### `GET /api/summary`
Returns KPI metrics and rep leaderboard.

**Response:**
```json
{
  "total_pipeline": 8865000,
  "pipeline_at_risk": 3160000,
  "red_count": 21,
  "yellow_count": 34,
  "rep_leaderboard": [...]
}
```

### `POST /api/deals/{id}/draft-email`
Generates an AI-powered re-engagement email for a deal.

**Response:**
```json
{
  "subject": "Quick check-in on our proposal",
  "body": "Hi [name], I wanted to follow up..."
}
```

## Scoring Engine

Deals are scored 0-100 based on five transparent rules:

1. **Customer Silence** (0-30 pts): Days since last customer reply
2. **Stage Stagnation** (0-25 pts): Time in stage vs team median
3. **Stale Next Step** (0-15 pts): Overdue or missing next steps
4. **Single Threading** (0-15 pts): Limited stakeholder engagement
5. **Close Date Slipped** (0-15 pts): Past-due expected close dates

Each rule returns a point value and a human-readable explanation.

**Buckets:**
- **0-35**: Green (healthy)
- **36-65**: Yellow (watch closely)
- **66+**: Red (needs action)

## Deployment

### Railway

1. Push to GitHub
2. Connect repository to Railway
3. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variable: `GROQ_API_KEY`
5. Deploy

Railway auto-detects Python and installs from `requirements.txt`.

## Data Generation

The `data_generator.py` script creates 200 synthetic deals with realistic patterns:

- 70% green (healthy deals)
- 20% yellow (warning signs)
- 10% red (high risk)

High-risk deals are modeled with specific behavioral signatures (long customer silence, overdue next steps, single-threaded relationships).

Run it anytime to regenerate data:
```bash
python data_generator.py
```
