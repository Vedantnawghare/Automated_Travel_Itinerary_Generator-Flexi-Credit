# n8n Travel Automation Workflow

This directory provides the automated integration between the **Automated Travel Itinerary Generator** and external services (**Google Calendar** and **Gmail**) via an **n8n** automation workflow.

---

## 🏗️ Architecture

```
Streamlit Application
       │
       │ HTTP POST (Structured Itinerary JSON)
       ▼
┌──────────────────────────────────────────────┐
│                  n8n Server                  │
│                                              │
│  Webhook Node (POST /travel-itinerary)       │
│                      │                       │
│                      ▼                       │
│           Parse & Format JSON                │
│                      │                       │
│          ┌───────────┴───────────┐           │
│          ▼                       ▼           │
│    Google Calendar             Gmail         │
│  (Create Trip Event)    (Send Email Summary) │
│          │                       │           │
│          └───────────┬───────────┘           │
│                      ▼                       │
│             Respond to Webhook               │
└──────────────────────────────────────────────┘
```

---

## 🚀 Setup & Import Instructions

### 1. Requirements
- An active instance of **n8n** (Cloud or self-hosted via Docker `n8nio/n8n`).
- A Google account with access to Google Calendar and Gmail.

### 2. Import Workflow into n8n
1. Open your n8n web dashboard.
2. In the top-right corner, click **"Add Workflow"** or **"+"**.
3. Click the **"..."** menu icon in the top-right and choose **"Import from File"**.
4. Select `n8n/workflow.json` from this repository.
5. The full visual workflow will appear on your canvas.

### 3. Connect Google Credentials
> [!IMPORTANT]
> Google credentials must never be committed into GitHub. Connect your accounts securely via OAuth2 inside n8n:

1. Double-click the **Google Calendar** node.
2. Under **Credential to connect with**, click **"Create New Credential"** and complete the standard Google OAuth2 flow.
3. Select your primary calendar.
4. Double-click the **Gmail** node.
5. Under **Credential to connect with**, click **"Create New Credential"** and authorize Gmail OAuth2 to send messages.

### 4. Activate the Webhook
1. Open the **Webhook** node.
2. Copy the **Production URL** (e.g. `https://your-n8n.com/webhook/travel-itinerary`).
3. Click **"Save"** and toggle the workflow switch to **Active**.

### 5. Configure Streamlit
Add the webhook URL to your `.env` file (for local development) or **Streamlit Secrets** (for cloud deployment):

```ini
N8N_WEBHOOK_URL=https://your-n8n.com/webhook/travel-itinerary
```

---

## 📦 Expected Webhook Payload Schema

When a user clicks **"⚡ Dispatch to n8n Webhook"** in the Streamlit UI, the application POSTs the following JSON payload:

```json
{
  "destination": "Goa",
  "origin": "Mumbai",
  "start_date": "2026-10-15",
  "end_date": "2026-10-18",
  "duration": 4,
  "travellers": 2,
  "budget": 32000,
  "total_estimated_cost": 28400,
  "currency": "INR",
  "preferences": {
    "travel_style": "relaxed",
    "interests": ["Beaches", "Cafes", "Nightlife"],
    "avoid": ["rushed schedules"]
  },
  "itinerary": [
    {
      "day": 1,
      "date": "2026-10-15",
      "theme": "Arrival & Heritage Exploration",
      "morning": ["Land at airport and check in", "Breakfast at heritage bakery"],
      "afternoon": ["Walk through historical quarter", "Lunch at local bistro"],
      "evening": ["Sunset stroll along beachfront promenade", "Seafood dinner"],
      "estimated_cost": 2800,
      "notes": "Paced comfortably with minimal transit."
    }
  ],
  "email": "traveler@example.com",
  "create_calendar_events": true,
  "send_email": true
}
```

---

## 🧪 Testing the Integration
1. In n8n, click **"Listen for Test Event"** inside the Webhook node.
2. In your Streamlit app, click **"Dispatch to n8n Webhook"**.
3. Observe the live execution in n8n and verify:
   - Event creation on your Google Calendar.
   - Formatted itinerary email delivered to your inbox.
