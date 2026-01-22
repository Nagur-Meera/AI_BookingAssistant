# 🏥 HealthCare Plus - AI Booking Assistant

An intelligent AI-powered booking assistant for medical clinics built with Streamlit and OpenAI.

## ✨ Features

- **🤖 AI Chat Interface**: Natural conversation with GPT-4o-mini
- **📄 RAG Support**: Upload PDFs and ask questions about your documents
- **📅 Smart Booking Flow**: Multi-turn conversation to collect booking details
- **✅ Confirmation System**: Summarizes and confirms before saving
- **💾 SQLite Database**: Persistent storage for bookings
- **📧 Email Notifications**: Automatic confirmation emails
- **📋 Admin Dashboard**: View, filter, and manage all bookings
- **🧠 Memory Management**: Maintains last 25 messages for context

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/Nagur-Meera/AI_BookingAssistant.git
cd AI_BookingAssistant
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Keys

Edit `.streamlit/secrets.toml`:
```toml
# Required
OPENAI_API_KEY = "your-openai-api-key"

# Optional (for email confirmations)
SMTP_EMAIL = "your-email@gmail.com"
SMTP_PASSWORD = "your-gmail-app-password"
```

### 4. Run the Application
```bash
streamlit run app/main.py
```

## 🔑 API Keys Setup

### OpenAI API Key (Required)
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a new API key
3. Add to `.streamlit/secrets.toml`

### Gmail App Password (Optional - for emails)
1. Enable 2-Factor Authentication on your Google Account
2. Go to [Google App Passwords](https://myaccount.google.com/apppasswords)
3. Generate a new App Password for "Mail"
4. Add to `.streamlit/secrets.toml`

## 📁 Project Structure

```
AI_UseCase/
├── app/
│   ├── main.py              # Main Streamlit application
│   ├── config.py            # Configuration and secrets
│   ├── chat_logic.py        # Intent detection & validation
│   ├── booking_flow.py      # Multi-turn booking conversation
│   ├── rag_pipeline.py      # PDF ingestion & RAG
│   ├── tools.py             # Database & email functions
│   └── admin_dashboard.py   # Admin UI
├── db/
│   ├── database.py          # SQLite connection
│   └── models.py            # Table definitions
├── docs/                    # Sample PDFs
├── .streamlit/
│   └── secrets.toml         # API keys (not in git)
├── requirements.txt
└── README.md
```

## 💬 How to Use

### Chat Interface
1. **General Questions**: Just type your question
2. **Start Booking**: Say "I want to book an appointment"
3. **With RAG**: Upload PDFs first, then ask questions about them

### Booking Flow
The assistant will collect:
- Full Name
- Email Address
- Phone Number
- Appointment Type
- Preferred Date (YYYY-MM-DD)
- Preferred Time (HH:MM)

After collecting all details, it will show a summary and ask for confirmation.

### Admin Dashboard
- View all bookings
- Filter by name, email, date, status
- Update booking status
- Delete bookings
- Export to CSV

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **AI/LLM**: OpenAI GPT-4o-mini
- **Embeddings**: text-embedding-3-small
- **Vector Store**: FAISS
- **Database**: SQLite
- **Email**: SMTP (Gmail)

## 📊 Database Schema

### customers
| Column | Type |
|--------|------|
| customer_id | INTEGER (PK) |
| name | TEXT |
| email | TEXT |
| phone | TEXT |

### bookings
| Column | Type |
|--------|------|
| id | INTEGER (PK) |
| customer_id | INTEGER (FK) |
| booking_type | TEXT |
| date | TEXT |
| time | TEXT |
| status | TEXT |
| created_at | TIMESTAMP |

## 🌐 Deployment on Streamlit Cloud

1. Push code to GitHub
2. Go to [Streamlit Cloud](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set main file path: `app/main.py`
5. Add secrets in the Streamlit Cloud dashboard:
   - `OPENAI_API_KEY`
   - `SMTP_EMAIL` (optional)
   - `SMTP_PASSWORD` (optional)

## ⚠️ Notes

- SQLite database resets on Streamlit Cloud restarts (acceptable for demo)
- For production, consider using Supabase or PostgreSQL
- Keep your API keys secure and never commit them to git

## 📝 License

MIT License
