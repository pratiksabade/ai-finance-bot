# Personal Finance Advisor Bot

A full-stack cash flow management and personal budgeting web application built with Python Flask, SQLAlchemy, SQLite, Chart.js, and Google Gemini API. Configured for the Indian Rupee (INR / ₹) standard.

---

## 1. Project Overview

Personal Finance Advisor Bot is a self-hosted personal finance platform. It enables individuals to track income streams, record categorized expenses, set monthly category spending caps, monitor capital savings goals, and generate data-driven cash flow diagnostics using Google Gemini.

The system is designed with an institutional, utility-first user interface: high-contrast typography, tabular financial figures, crisp rectangular geometry, and strict client-side data isolation.

---

## 2. Features

- **Income Stream Tracking:** Log multi-source earnings (salary, consulting, dividends, business revenue) with dates, tags, and amounts in INR (₹).
- **Categorized Expense Ledger:** Record and categorize expenses across 9 core domains (Food, Rent, Transport, Education, Healthcare, Entertainment, Shopping, Utilities, Other).
- **Budget Planning & Limit Enforcement:** Define monthly category caps. Real-time indicators flag safe spending, approaching limits (80%), and budget overruns.
- **Capital & Savings Goals:** Track target reserve funds (Emergency Fund, Hardware, Travel, Higher Education) with progress bars and quick-allocation deposits.
- **Backend-Computed Ratios:** Savings rates, category burn rates, and budget variances are computed server-side in Python to guarantee mathematical consistency.
- **Interactive Visualizations:** Chart.js charts for multi-month income vs. expense comparisons and category breakdown doughnuts.
- **Google Gemini AI Diagnostic:** Generates structured spending diagnostics, leakage evaluations, and actionable 30-day plans based on actual user transactions.
- **Statutory Financial Disclaimer:** Explicit disclaimers clarifying educational and planning use only; no automated trading or financial execution.
- **Privacy & Terms Pages:** Dedicated regulatory pages outlining local SQLite persistence, data confidentiality, and non-fiduciary status.

---

## 3. Technology Stack

- **Backend:** Python 3.9+ / 3.11+, Flask 3.x, Flask-SQLAlchemy 3.x, Flask-CORS, Werkzeug (PBKDF2 password hashing).
- **Database:** SQLite 3 (isolated relational storage via SQLAlchemy ORM).
- **AI Engine:** Google Gemini API (`google-generativeai` / `gemini-3.8-flash`).
- **Frontend:** Semantic HTML5, CSS3 (custom institutional fintech design system, no CSS frameworks required), Vanilla JavaScript (ES6+ modular controllers), Chart.js (v4.x).
- **Configuration:** Python-dotenv for environment variable isolation.

---

## 4. Project Structure

```
personal-finance-advisor/
├── app.py                      # Flask application factory, routes, and server entry point
├── config.py                   # Centralized configuration and environment loader
├── seed.py                     # Database seeder with realistic Indian Rupee demo records
├── test_app.py                 # Automated verification test suite
├── requirements.txt            # Python dependencies
├── .env.example                # Sample environment configuration template
├── .env                        # Local environment variables (ignored by Git)
├── .gitignore                  # Git ignore rules for virtualenvs, SQLite, and secrets
├── models/                     # SQLAlchemy database models
│   ├── __init__.py             # Database instance export
│   ├── user.py                 # User model with password hashing
│   ├── income.py               # Income stream model
│   ├── expense.py              # Categorized expense model
│   ├── budget.py               # Monthly category budget limits model
│   └── savings_goal.py         # Capital savings goal model
├── routes/                     # Modular Flask REST API Blueprints
│   ├── __init__.py             # Blueprints export
│   ├── auth.py                 # Registration, login, session validation
│   ├── dashboard.py            # Financial summary endpoint with demo data fallback
│   ├── income.py               # Income CRUD operations
│   ├── expenses.py             # Expense CRUD operations and category listing
│   ├── budgets.py              # Budget limits and spending variance
│   ├── goals.py                # Savings goals CRUD and fund allocation
│   └── ai.py                   # Gemini AI financial diagnostic endpoint
├── services/                   # Business logic and external API integrations
│   ├── __init__.py
│   ├── finance_service.py      # Server-side calculations and INR formatters
│   └── gemini_service.py       # Google Gemini SDK service with fallback handling
├── templates/                  # Jinja2 HTML templates
│   ├── index.html              # Public landing page
│   ├── login.html              # Account authentication page
│   ├── register.html           # New account registration page
│   ├── dashboard.html          # Core financial dashboard application shell
│   ├── privacy.html            # Privacy Policy legal page
│   └── terms.html              # Terms and Conditions legal page
├── static/                     # Static frontend assets
│   ├── favicon.svg             # Institutional SVG favicon
│   ├── css/
│   │   └── style.css           # Institutional fintech stylesheet
│   └── js/
│       ├── app.js              # Application state, router, modals, toasts, INR formatting
│       ├── dashboard.js        # Dashboard metrics and Chart.js visualizations
│       ├── income.js           # Income table and form controller
│       ├── expenses.js         # Expense table, category filter, and form controller
│       ├── budgets.js          # Budget variance and limit controller
│       ├── goals.js            # Savings goal progress and deposit controller
│       └── ai-advisor.js       # AI diagnostic execution and report renderer
└── instance/
    └── finance.db              # SQLite relational database (auto-created on first run)
```

---

## 5. Prerequisites

- Python 3.9, 3.10, 3.11, or 3.12 installed on your system.
- Pip package manager installed.
- Git (optional, for repository management).
- Google Gemini API key (obtainable from Google AI Studio).

---

## 6. Installation & Local Setup

### Step 1: Clone or Navigate to the Project Folder

```bash
cd personal-finance-advisor
```

### Step 2: Create and Activate Virtual Environment

**On Windows (Command Prompt or PowerShell):**

```powershell
python -m venv venv
venv\Scripts\activate
```

**On Linux / macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies

```bash
pip install -r requirements.txt
```

---

## 7. Environment Configuration (.env)

Copy `.env.example` to create your local `.env` file:

**On Windows:**

```cmd
copy .env.example .env
```

**On Linux / macOS:**

```bash
cp .env.example .env
```

Open `.env` in your text editor and configure your variables:

```ini
# Google Gemini API Key from Google AI Studio
GEMINI_API_KEY=your_actual_gemini_api_key_here

# Flask Secret Key for session cookie signing
SECRET_KEY=generate-a-secure-random-secret-key-for-sessions

# Server settings
PORT=5000
FLASK_DEBUG=1
```

> **Security Note:** The `.env` file contains sensitive credentials and is strictly excluded from version control via `.gitignore`. Never commit API keys to GitHub.

---

## 8. Database Initialization & Demo Data

You can start with a fresh database or populate it with realistic Indian Rupee demo records.

### Option A: Initialize Empty Database

The SQLite database file (`instance/finance.db`) is automatically created when you start the Flask application.

### Option B: Seed Realistic Demo Data (Recommended for Evaluation)

Run the seeding script to populate an example user with income records, categorized expenses, monthly budgets, and savings goals:

```bash
python seed.py
```

To wipe and re-seed from scratch at any time:

```bash
python seed.py --reset
```

**Demo Account Credentials:**
- **Email:** `demo@financeadvisor.in`
- **Password:** `Password@123`
- **Currency:** Indian Rupee (INR / ₹)

---

## 9. Running the Application

Start the Flask development server:

```bash
python app.py
```

The application will start on:

```
http://127.0.0.1:5000
```

Open this URL in any modern web browser (Chrome, Firefox, Edge, Safari).

---

## 10. Automated Testing & Verification

Run the comprehensive test suite to verify health endpoints, user authentication, session security, CRUD operations, backend financial calculations, and Google Gemini integration:

```bash
python test_app.py
```

The test runner will validate:
1. Health check endpoint status and currency format.
2. User login, password verification, and session persistence.
3. Financial summary math (Income, Expenses, Net Savings, Savings Ratio).
4. CRUD functionality for Income, Expenses, Budgets, and Goals.
5. Savings goal allocation and fund deposits.
6. Google Gemini AI diagnostic generation with legal disclaimer enforcement.
7. Public landing, authentication, privacy policy, and terms route accessibility.

---

## 11. Git & GitHub Deployment Instructions

Follow these steps to push the project to your GitHub repository:

### Step 1: Initialize Git Repository

```bash
git init
```

### Step 2: Verify Ignored Files

Ensure `.env` and `instance/` are ignored:

```bash
git status
```

Verify that `.env` and `instance/finance.db` are **NOT** listed in the untracked files.

### Step 3: Stage and Commit Files

```bash
git add .
git commit -m "Initial commit: Personal Finance Advisor Bot full-stack application"
```

### Step 4: Link Remote Repository and Push

```bash
git branch -M main
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
```

---

## 12. Production Deployment Notes

For deployment to Linux servers (Ubuntu/Debian) or PaaS platforms (Render, Railway, AWS EC2, DigitalOcean):

1. **WSGI Server:** Use Gunicorn instead of the built-in Flask development server:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```
2. **Environment Variables:** Set `SECRET_KEY`, `GEMINI_API_KEY`, and `FLASK_DEBUG=0` in your production environment settings.
3. **Database Migration:** For multi-instance scaling, point `DATABASE_URL` in `.env` to a PostgreSQL instance (e.g., `postgresql://user:password@host:5432/dbname`). SQLAlchemy ORM handles the schema seamlessly.
4. **HTTPS / SSL:** Enforce HTTPS when serving over custom domains to ensure session cookie encryption (`SESSION_COOKIE_SECURE=True`).

---

## 13. Security & Compliance Architecture

- **Password Storage:** Uses Werkzeug's modern cryptographic password hashing with unique salt per user. Plaintext passwords are never stored.
- **Session Protection:** Session cookies are configured with `HTTPOnly=True` and `SameSite=Lax` to mitigate XSS and CSRF attack vectors.
- **SQL Injection Prevention:** All database operations utilize SQLAlchemy parameterized ORM queries; no raw string concatenation is used in SQL statements.
- **User Record Isolation:** All queries filter explicitly by `user_id = session['user_id']`. Users cannot view or modify transactions belonging to other accounts.
- **API Key Confidentiality:** Google Gemini API keys are loaded strictly on the backend and are never sent or exposed to client-side browsers.
- **Non-Fiduciary Disclaimer:** Statutory disclaimers are embedded within the AI Advisor interface and public legal terms, clearly establishing educational scope and prohibiting automated trades.

---

## 14. License

This project is licensed under the MIT License. Open source and suitable for academic evaluation, personal cash flow management, and portfolio demonstration.
