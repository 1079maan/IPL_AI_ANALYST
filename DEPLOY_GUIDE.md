# IPL NEXUS — Complete Deployment Guide
# Deploy to Streamlit Cloud in 7 steps

---

## STEP 1 — Create Supabase Account (Free Online PostgreSQL)

1. Go to → https://supabase.com
2. Click "Start your project" → Sign up free
3. Click "New Project" → fill in:
   - Project name: `ipl-nexus`
   - Database password: create a strong password (save it!)
   - Region: pick closest to India (Singapore or Mumbai)
4. Wait 2 minutes for project to be ready
5. Go to: Settings → Database → find your credentials:
   - Host: `db.xxxxxxxxxxxx.supabase.co`
   - Port: `5432`
   - Database: `postgres`
   - User: `postgres`
   - Password: (the one you created)

---

## STEP 2 — Import IPL Data to Supabase

Option A — Using pgAdmin (easiest):
1. Open pgAdmin on your PC
2. Right-click your local IPL_Data → Backup → save as .sql file
3. Open Supabase → SQL Editor
4. Paste and run the .sql file

Option B — Using CSV import:
1. Supabase → Table Editor → Import CSV
2. Upload each CSV file:
   - matches.csv
   - innings.csv
   - deliveries.csv
   - players.csv
   - player_teams.csv

---

## STEP 3 — Update secrets.toml for Supabase

Open .streamlit/secrets.toml and update:

```toml
GROQ_API_KEY = "gsk_your_actual_groq_key"

[postgres]
host     = "db.xxxxxxxxxxxx.supabase.co"
port     = 5432
dbname   = "postgres"
user     = "postgres"
password = "your_supabase_password"
```

Test locally first:
```bash
streamlit run Home.py
```
Click "Test DB Connection" → should show PostgreSQL Connected ✅

---

## STEP 4 — Push to GitHub

```bash
# In your project folder (ipl_nexus_deploy)

# Initialize git
git init

# Add all files
git add .

# First commit
git commit -m "IPL NEXUS AI Chatbot - initial deployment"

# Create repo on github.com first, then:
git remote add origin https://github.com/YOUR_USERNAME/ipl-nexus.git
git branch -M main
git push -u origin main
```
<!-- https://github.com/1079maan/Final_Project.git -->

IMPORTANT: Check that .streamlit/secrets.toml is NOT uploaded.
The .gitignore file already excludes it.

---

## STEP 5 — Deploy on Streamlit Cloud

1. Go to → https://share.streamlit.io
2. Sign in with GitHub
3. Click "New app"
4. Fill in:
   - Repository: your-username/ipl-nexus
   - Branch: main
   - Main file path: Home.py
5. Click "Deploy!"
6. Wait 3-5 minutes for deployment

---

## STEP 6 — Add Secrets in Streamlit Cloud

1. Go to your deployed app
2. Click ⋮ (three dots) → Settings → Secrets
3. Paste EXACTLY this (with your real values):

```toml
GROQ_API_KEY = "gsk_your_real_groq_key_here"

[postgres]
host     = "db.xxxxxxxxxxxx.supabase.co"
port     = 5432
dbname   = "postgres"
user     = "postgres"
password = "your_supabase_password"
```

4. Click Save → App will restart automatically

---

## STEP 7 — Test Your Live App

1. Open your app URL:
   https://your-username-ipl-nexus.streamlit.app

2. Go to AI Chat page
3. Click "Test DB Connection" → should show ✅ Connected
4. Ask: "Top 10 batsmen all time" → should show results

DONE! Share the URL with anyone in the world! 🎉

---

## How to Make Changes After Deployment

```bash
# 1. Edit any file on your PC
# 2. Push to GitHub
git add .
git commit -m "describe your change"
git push

# 3. Streamlit Cloud auto-updates in 1-2 minutes
# No manual action needed!
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| DB not connecting | Check secrets.toml host/password are correct |
| App crashes on start | Check requirements.txt has all packages |
| Groq not working | Check GROQ_API_KEY in Streamlit secrets |
| Slow loading | Normal first time — Supabase free tier sleeps |
| Model file missing | Upload ipl_model.pkl to GitHub or use demo mode |
