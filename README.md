# AI Powered College & University Learning Management System

A production-ready LMS with AI-powered student assistance, built for **Government Graduate College Jhang**.

## Features

- **AI Chatbot** — Context-aware student assistance with streaming responses, multiple AI providers (Gemini, Groq, OpenRouter, HuggingFace, DeepSeek)
- **Knowledge Base** — Admin uploads training data organized by department/program/class/subject
- **Quiz Generator** — AI generates MCQs, True/False, Fill-in-the-Blank from knowledge base
- **Flashcards** — AI-powered study flashcards
- **CMS** — Full public website with editable pages, news, events, gallery
- **Admin Panel** — Dashboard with analytics, charts, student management, CRUD for everything
- **Role-Based Auth** — Super Admin, Admin, Student with session management
- **Downloads** — Books, notes, past papers, assignments
- **Notifications** — Targeted to departments, classes, or all students
- **Dark Mode** — Toggle between light and dark themes
- **Responsive** — Mobile-friendly design

## Tech Stack

- **Backend:** Python, Flask, SQLAlchemy
- **Frontend:** HTML5, CSS3, Bootstrap 5, JavaScript, AJAX
- **Database:** Supabase PostgreSQL
- **AI:** Google Gemini, Groq, OpenRouter, HuggingFace, DeepSeek (switchable from admin panel)

## Login Credentials

| Role | Email | Password |
|------|-------|----------|
| Super Admin | admin@ggcjhang.edu.pk | Admin@123 |
| Student | ahmed.khan@student.ggcjhang.edu.pk | Student@123 |

## Local Setup

```bash
# Clone the repo
git clone <your-repo-url>
cd Ahmad

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment file and fill in your values
cp .env.example .env

# Run the app
python run.py
```

Visit http://localhost:5000

## Environment Variables

| Variable | Description |
|----------|-------------|
| SECRET_KEY | Flask secret key |
| SUPABASE_URL | Your Supabase project URL |
| SUPABASE_KEY | Supabase publishable key |
| SUPABASE_DB_HOST | PostgreSQL host (pooler) |
| SUPABASE_DB_PORT | 5432 |
| SUPABASE_DB_NAME | postgres |
| SUPABASE_DB_USER | postgres.your-project-ref |
| SUPABASE_DB_PASSWORD | Your database password |
| ENCRYPTION_KEY | Fernet key for API key encryption |

---

## Deploy to Render

### Step 1: Push to GitHub

```bash
cd Ahmad
git init
git add .
git commit -m "Initial commit - AI Powered LMS"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### Step 2: Create Render Web Service

1. Go to [render.com](https://render.com) and sign up/login
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:

| Setting | Value |
|---------|-------|
| **Name** | `ggc-jhang-lms` |
| **Region** | Singapore (closest to Pakistan) |
| **Branch** | `main` |
| **Runtime** | Python |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn run:app --bind 0.0.0.0:$PORT --workers 4 --timeout 120` |
| **Plan** | Free (or Starter $7/mo for always-on) |

### Step 3: Add Environment Variables

In the Render dashboard, go to **Environment** tab and add:

| Key | Value |
|-----|-------|
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | (click "Generate" to create a random key) |
| `SUPABASE_URL` | `https://vbiqkqfphkhkvqzhqyra.supabase.co` |
| `SUPABASE_KEY` | `sb_publishable_ARJYhl4SC4WMj2nFOJ0FSw_V_IJrpy2` |
| `SUPABASE_DB_HOST` | `aws-1-ap-southeast-1.pooler.supabase.com` |
| `SUPABASE_DB_PORT` | `5432` |
| `SUPABASE_DB_NAME` | `postgres` |
| `SUPABASE_DB_USER` | `postgres.vbiqkqfphkhkvqzhqyra` |
| `SUPABASE_DB_PASSWORD` | Your database password |
| `ENCRYPTION_KEY` | `kSjHkWvCj7ogYwUZY74Mm2ExGQvSk0K3zpNXCGI4Amw=` |
| `PYTHON_VERSION` | `3.12.4` |

### Step 4: Deploy

Click **"Create Web Service"** — Render will:
1. Clone your repo
2. Install dependencies
3. Start the gunicorn server
4. Give you a URL like `https://ggc-jhang-lms.onrender.com`

### Important Notes

- **Free tier** spins down after 15 minutes of inactivity (first request after sleep takes ~30 seconds)
- **Starter plan** ($7/mo) keeps it always running
- Database is on **Supabase** (separate), so no extra DB cost on Render
- SSL/HTTPS is automatic on Render

### Step 5: Verify

1. Open your Render URL
2. Login with `admin@ggcjhang.edu.pk` / `Admin@123`
3. Go to **AI Settings** → Configure at least one AI provider with an API key
4. Test the chatbot

---

## Project Structure

```
Ahmad/
├── app/
│   ├── ai/                 # AI provider integrations
│   ├── controllers/        # Request handlers
│   ├── models/             # 18 SQLAlchemy models (26 tables)
│   ├── routes/             # 5 Flask blueprints (84 routes)
│   ├── services/           # 15 business logic services
│   ├── static/             # CSS, JS, uploads
│   ├── templates/          # 66 Jinja2 templates
│   └── utils/              # Helpers, decorators, encryption
├── migrations/             # SQL schema
├── config.py               # Multi-environment config
├── run.py                  # Entry point
├── requirements.txt        # Dependencies
├── render.yaml             # Render deployment config
├── Procfile                # Process file for Render/Heroku
└── runtime.txt             # Python version
```
