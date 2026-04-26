# OnboardIQ — Funnel Analytics Dashboard

A funnel analytics dashboard that gives product and growth teams complete visibility into their user onboarding journey, from the moment a user starts, to every step they take, to whether they complete or abandon the process entirely.

**Demo Video:** 
## Demo Video: https://www.loom.com/share/32bacd5db13f40fd9e2103bc886cb358

---

## The Problem

Most organisations measure outcomes. They know their headline conversion rate. What many do not know — with any precision, is what happened in between.

Some teams rely on third-party tools that capture surface-level events but not granular, step-by-step behaviour. Others track only the users who complete onboarding and have little to no data on those who dropped off, where exactly they left, or why. In some organisations, the data exists across different systems and nobody has connected it into a single coherent view.

Without that visibility, optimisation becomes guesswork. OnboardIQ is built to close that gap.

---

## What It Does

### Step Analysis
Shows exactly where users drop off at each stage of the funnel, the number of users lost, the drop-off percentage, and the conversion rate between steps. Each step is classified as **Healthy**, **Watch**, or **High Risk** so teams know immediately where to focus.

### Time Analysis
Tracks how long users spend between steps. A step that takes users an average of 12 minutes to move through is telling you something, friction, confusion, or a missing document. Time data turns a drop-off number into a diagnosis.

### Channel Breakdown
Separates funnel performance by acquisition channel. A 61% conversion rate on web versus 33% on mobile is not a funnel problem, it is a mobile experience problem. The fix is completely different, and the distinction matters.

### User Drill-Down
Shows individual user journeys, when they entered, where they stopped, how long the process took, and what channel they came from. This is where pattern recognition happens and hypotheses are formed.

### Insights & Recommendations
The dashboard automatically generates insights based on the data, biggest drop-off point, slowest transition, best-performing channel, and surfaces strategic recommendations for the team.

---

## Why This Matters for Growth

Onboarding is the most important funnel in any product. It is the moment that decides whether a new user becomes an active one, and whether an active user sticks around. Every improvement here has a ripple effect: more users complete onboarding, more of them stay, more of them generate revenue, and fewer of them churn.

The data needed to make those improvements is almost always already there. It sits in event logs that nobody has pulled together into one clear view. What is usually missing is the skills to make that data readable and the analytical thinking to know what questions to ask of it.

That is what OnboardIQ is built around, not just displaying data, but making it easy for a team to see what is wrong, understand why, and know what to do next.

---

## Tech Stack

| Layer | Tool |
|---|---|
| Backend | FastAPI (Python) |
| Database | PostgreSQL via Neon |
| Frontend | Vanilla HTML, CSS, JavaScript |
| Charts | Chart.js |
| Hosting | Vercel |

---

## Project Structure

```
onboardiq/
├── api/
│   ├── index.py        # All API routes (FastAPI)
│   └── database.py     # Database connection
├── public/
│   └── index.html      # Dashboard frontend
├── sql/
│   └── schema.sql      # Database schema and seed data
├── vercel.json         # Vercel routing configuration
└── requirements.txt    # Python dependencies
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Health check |
| GET | `/api/funnels` | List all funnels |
| GET | `/api/funnels/{id}` | Get funnel and its steps |
| POST | `/api/funnels` | Create a new funnel |
| POST | `/api/events/start` | Log a funnel start event |
| POST | `/api/events/step` | Log a step event |
| POST | `/api/events/complete` | Log a completion event |
| POST | `/api/events/abandon` | Log an abandon event |
| GET | `/api/analytics/funnel/{id}/steps` | Step-by-step drop-off analysis |
| GET | `/api/analytics/funnel/{id}/summary` | Overall funnel summary |
| GET | `/api/analytics/funnel/{id}/time` | Time-between-steps analysis |
| GET | `/api/analytics/funnel/{id}/channel` | Channel breakdown |
| GET | `/api/analytics/funnel/{id}/users` | Individual user journeys |

All analytics endpoints support optional `start_date` and `end_date` query parameters for date filtering.

---

## Running Locally

**Prerequisites:** Python 3.10+, a PostgreSQL database (Neon free tier recommended)

```bash
# Clone the repo
git clone https://github.com/Okaks/onboardiq.git
cd onboardiq

# Install dependencies
pip install -r requirements.txt

# Set your database URL
export DATABASE_URL="your_neon_connection_string"

# Run the schema to set up tables and seed data
# Paste sql/schema.sql into your Neon SQL Editor and run it

# Start the server
uvicorn api.index:app --reload
```

Visit https://onboardiq-eight.vercel.app/ to view the dashboard.

---

## Environment Variables

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string (set in Vercel project settings) |

---

## Author

**Blessing Okakwu** — Growth & Product Analyst
[Portfolio](https://bokakwu.wixsite.com/okakwus-analytics) · [LinkedIn](https://www.linkedin.com/in/blessing-okakwu/) · [GitHub](https://github.com/Okaks/onboardiq)
