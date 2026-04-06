# 🏏 IPL AI Analyst

> **Analyze. Predict. Win with Data.**
> A full-stack AI-powered cricket analytics platform built on 17 seasons of IPL data.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-Framework-red?style=flat-square&logo=streamlit)
![Power BI](https://img.shields.io/badge/Power%20BI-Embedded-yellow?style=flat-square&logo=powerbi)
![Groq](https://img.shields.io/badge/Groq-LLaMA%203-purple?style=flat-square)
![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-green?style=flat-square&logo=supabase)
![ML](https://img.shields.io/badge/ML-Random%20Forest-orange?style=flat-square&logo=scikit-learn)

---

## 📌 Table of Contents

- [About the Project](#about-the-project)
- [How This Project Works](#how-this-project-works)
- [Tech Stack](#tech-stack)
- [Database Schema](#database-schema)
- [Features](#features)
  - [1. IPL Dashboard](#1-ipl-dashboard)
  - [2. IPL Match Prediction](#2-ipl-match-prediction)
  - [3. AI Analytics Chat](#3-ai-analytics-chat)
  - [4. Project Architecture](#4-project-architecture)
- [How to Use Each Feature](#how-to-use-each-feature)
- [Local Setup Guide](#local-setup-guide)
- [Project Stats](#project-stats)
- [Author](#author)

---

## 📖 About the Project

**IPL AI Analyst** is a final-year MCA (Data Science) capstone project built at D.Y. Patil University, Pune. It is a multi-page Streamlit web application that combines **Business Intelligence**, **Machine Learning**, and **Generative AI** into a single platform to analyze, visualize, and predict IPL cricket match outcomes.

The platform is powered by a live **Supabase PostgreSQL** database containing 76,000+ records across 17 IPL seasons (2008–2025), with an embedded **Power BI** dashboard, a **Random Forest** ML model for match prediction, and an **AI chatbot** that converts plain English questions into live SQL queries and returns answers with interactive Plotly charts.

---

## ⚙️ How This Project Works

The overall architecture of IPL AI Analyst follows a 4-layer pipeline:

```
User (Browser)
     │
     ▼
Streamlit Web App  ──────────────────────────────────────────┐
     │                                                        │
     ├── IPL Dashboard     →  Power BI Embedded Report        │
     │                                                        │
     ├── Match Prediction  →  Random Forest ML Model (.pkl)   │
     │                        trained on 2008–2024 match data │
     │                                                        │
     ├── AI Analytics Chat →  Groq LLaMA 3 (NL → SQL)        │
     │                        → Supabase PostgreSQL (Live DB) │
     │                        → Plotly Chart (Result)         │
     │                                                        │
     └── Project Architecture → Static Info Page              │
                                                              │
Supabase PostgreSQL Database ─────────────────────────────────┘
     │
     ├── matches       (1,034+ rows)
     ├── innings       (2,068+ rows)
     ├── deliveries    (250K+ rows)
     ├── players       (600+ rows)
     └── player_teams  (3,500+ rows)
```

**Step-by-step flow:**

1. The user opens the Streamlit app in their browser.
2. They navigate to any of the 4 pages using the left sidebar.
3. Depending on the page, the app either loads an embedded Power BI report, runs an ML model, queries the live Supabase database via the AI chatbot, or displays the project architecture.
4. All data is served from a live Supabase PostgreSQL backend — no static CSV files for the main app.
5. The ML model (`ipl_model.pkl`) is loaded via Joblib and makes predictions in milliseconds using scikit-learn's Random Forest Classifier.
6. The AI chatbot uses Groq's LLaMA 3 API to generate SQL from the user's English question, runs it against Supabase, and returns both a text answer and a Plotly chart.

---

## 🛠️ Tech Stack

| Category | Tools Used |
|---|---|
| **Frontend & Framework** | Python 3.10+, Streamlit |
| **Analytics & BI** | Power BI (Embedded), Plotly |
| **AI & NLP** | Groq LLaMA 3 (NL to SQL) |
| **Machine Learning** | Scikit-learn (Random Forest), Joblib |
| **Database** | Supabase PostgreSQL, SQLite / CSV |
| **Data Processing** | Pandas, NumPy |
| **Deployment** | Streamlit Cloud |

---

## 🗄️ Database Schema

The Supabase PostgreSQL database has 5 normalized tables:

| Table | Key Columns | Rows |
|---|---|---|
| `matches` | match_id, season, winner, venue, toss_winner | 1,034+ |
| `innings` | innings_id, total_runs, run_rate | 2,068+ |
| `deliveries` | delivery_id, batter_id, runs_batter | 250K+ |
| `players` | player_id, player_name, registry_id | 600+ |
| `player_teams` | player_id, team_name, season | 3,500+ |

> **Note:** Table names in Supabase are **case-sensitive**. Always use exact lowercase names as shown above when writing SQL queries.

---

## ✨ Features

### 1. 📊 IPL Dashboard

**What it is:** An interactive Power BI report embedded directly inside the Streamlit app. It provides deep analytics across 17 seasons of IPL data with filters, drill-downs, and visual charts.

**Why it is used:** Power BI provides enterprise-grade business intelligence capabilities — interactive slicers, cross-filtering, and multi-page report navigation — that go far beyond basic Plotly charts. Embedding it inside Streamlit allows users to experience BI-grade analytics without leaving the app.

**What it shows:**
- Total matches, total runs, total sixes, average run rate per match
- Highest team score, chasing success percentage, toss win impact
- Total runs by season (area chart)
- Total matches by season (bar chart)
- Win type distribution — Runs vs Wickets (donut chart)
- The report has **5 pages** navigable via the Power BI pagination bar

---

### 2. 🎯 IPL Match Prediction

**What it is:** A machine learning-powered match winner predictor. The user selects two teams, a venue, a toss winner, and a toss decision — and the model returns win probabilities for both teams in under a second.

**Why it is used:** The Random Forest Classifier was chosen because it handles categorical features well, is robust against overfitting, and provides probability scores (not just win/loss) which makes the prediction output more meaningful and informative.

**Model Details:**
- **Algorithm:** Random Forest Classifier
- **Estimators:** 200 decision trees
- **Training Data:** IPL seasons 2008–2024
- **Test Accuracy:** ~72% (cross-validated)
- **Features used:** Team 1, Team 2, Venue, Toss Winner, Toss Decision
- **Encoding:** Label Encoding for all categorical columns
- **Serialization:** Saved and loaded via Joblib (`.pkl` file)

**Output:** Two side-by-side cards showing the predicted winner and runner-up with their win probability percentages (e.g., Delhi Capitals — 53.6%, Lucknow Super Giants — 46.4%).

---

### 3. 🤖 AI Analytics Chat

**What it is:** A conversational AI chatbot that accepts any IPL-related question in plain English, converts it to SQL using Groq's LLaMA 3 model, queries the live Supabase PostgreSQL database, and returns both a natural language answer and an interactive Plotly chart.

**Why it is used:** This feature removes the need for users to know SQL. Any cricket fan, analyst, or recruiter can simply type a question and get a data-backed answer instantly. It demonstrates real-world integration of Large Language Models (LLMs) with structured databases — a highly relevant skill in modern data engineering.

**How it works internally:**
1. User types a question in the chat input box.
2. The question is sent to the **Groq LLaMA 3** API with a system prompt that describes the database schema.
3. LLaMA 3 generates a valid PostgreSQL SQL query.
4. The SQL is executed against the **Supabase PostgreSQL** database.
5. The result is returned to LLaMA 3, which writes a natural language answer.
6. A **Plotly chart** is automatically generated from the query result.
7. Both the text answer and the chart are displayed in the chat window.

**Quick Questions (FAQ Buttons):**
The chatbot sidebar includes 15 pre-built clickable questions across 3 difficulty levels:

- 🟢 **Easy** — How many total matches were played in IPL history? | Which team played the most matches? | How many seasons are there in the dataset? | Which match venue is most popular? | How many total wickets fell in IPL 2023?
- 🟡 **Medium** — Which team won the most matches when batting first? | What is the average first innings score? | Which venue has the highest average score? | Who are the top 5 wicket-takers? | Which team has the best win percentage?
- 🔴 **Hard** — Which batsman has the most sixes in IPL history? | What is the win percentage for teams winning the toss? | Which season had the highest average match score? | Who scored the most runs in a single season? | What is the best bowling economy in IPL history?

---

### 4. 🏗️ Project Architecture

**What it is:** A detailed information page that documents the entire technical architecture of the IPL AI Analyst platform. It is designed to help developers, recruiters, and professors understand how the system was built.

**Why it is used:** Transparency in project architecture demonstrates professional software engineering practices. It shows that the project is not just a UI — it has a structured backend, a trained ML pipeline, and a documented data engineering workflow.

**What it contains:**
- **Technology Stack Grid** — All tools with logos and descriptions (Python, Streamlit, Scikit-learn, Pandas, Power BI, Joblib, SQLite/CSV, Streamlit Cloud)
- **Database Schema Table** — All 5 tables with key columns and row counts
- **ML Feature Engineering Table** — All features used for model training with encoding descriptions
- **Model Architecture Panel** — Algorithm (Random Forest), estimators (200), test accuracy (~72%), holdout year (2025)
- **Local Setup Guide** — 5-step setup instructions with terminal commands

---

## 🖥️ How to Use Each Feature

### Using the IPL Dashboard
1. Click **IPL Dashboard** in the left sidebar.
2. The Power BI report loads automatically inside the app.
3. Use the **Season**, **Team**, and **Venue** slicers at the top to filter data.
4. Click the **arrow buttons** at the bottom of the Power BI panel to navigate between the 5 report pages.
5. Use the **expand icon** (top-right of the Power BI panel) to view the report in full screen.

### Using Match Prediction
1. Click **IPL Match Prediction** in the left sidebar.
2. Select **Team 1** from the first dropdown.
3. Select **Team 2** from the second dropdown.
4. Select the **Venue / Stadium** from the third dropdown.
5. Select the **Toss Winner** and **Toss Decision** (Bat or Field).
6. Click the **"Engage Prediction Engine"** button.
7. The prediction output shows both teams with their win probability percentages.

### Using the AI Analytics Chat
1. Click **AI Analytics Chat** in the left sidebar.
2. Either type your own question in the chat input box at the bottom, or click any of the **15 Quick Question buttons** on the left panel.
3. Press the **ASK** button or hit Enter.
4. Wait 2–5 seconds for the AI to generate SQL, query the database, and return the answer.
5. The response appears as a text answer followed by an interactive Plotly chart.
6. You can ask follow-up questions in the same session.

### Using Project Architecture
1. Click **Project Architecture** in the left sidebar.
2. Scroll down to explore the tech stack, database schema, ML feature table, model details, and local setup guide.
3. Expand the **requirements.txt** section at the bottom to see all Python dependencies.

---

## 🚀 Local Setup Guide

Follow these steps to run IPL AI Analyst on your local machine:

**Step 1 — Clone the repository**
```bash
git clone https://github.com/your-username/ipl-ai-analyst.git
cd ipl-ai-analyst
```

**Step 2 — Install Python dependencies**
```bash
pip install -r requirements.txt
```

**Step 3 — Copy your trained ML model to the app root**
```bash
cp /path/to/ipl_model.pkl .
```
> The `ipl_model.pkl` file must be placed alongside `Home.py` in the root directory.

**Step 4 — Set up your environment variables**

Create a `.env` file in the root directory and add the following:
```
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
GROQ_API_KEY=your_groq_api_key
POWERBI_URL=your_power_bi_embed_url
```

**Step 5 — Launch the Streamlit app**
```bash
streamlit run Home.py
```

**Step 6 — Open in browser**

The app will automatically open at `http://localhost:8501`

---

## 📊 Project Stats

| Metric | Value |
|---|---|
| IPL Seasons Covered | 17 (2008–2025) |
| Total Matches | 1,034+ |
| Total Deliveries | 250,000+ |
| Total Players | 600+ |
| ML Model Accuracy | ~72% |
| ML Algorithm | Random Forest (200 estimators) |
| AI Engine | Groq LLaMA 3 |
| Database | Supabase PostgreSQL |
| Deployment | Streamlit Cloud |

---

## 👨‍💻 Author

**Maan** — Final Year MCA (Data Science) Student

- 🎓 D.Y. Patil University, Pune | CGPA: 8.11 / 10
- 🔗 [LinkedIn](http://www.linkedin.com/in/maan-vaishnani)
- 💻 [GitHub](https://github.com/1079maan/IPL_AI_ANALYST.git)
- 🌐 [Live Demo](https://ipl-ai-analytics-platform.streamlit.app/)

---

> *Built with passion for cricket, data science, and AI. This project is the capstone of my MCA journey — combining everything I learned about data engineering, machine learning, and generative AI into one real-world platform.*
