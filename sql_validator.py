"""
sql_validator.py — SQL Validator using Groq LLM

This is Step 2 in the chatbot pipeline:

  User Question
       ↓
  Step 1: sql_generator.py  → Generate SQL
       ↓
  Step 2: sql_validator.py  → Validate / Correct SQL   ← THIS FILE
       ↓
  Step 3: db.py             → Run validated SQL on PostgreSQL
       ↓
  Step 4: charts.py         → Draw Plotly chart
       ↓
  Streamlit UI

Uses your exact validator prompt.
Returns { validated_sql, status, explanation }
"""

import os
import re
import json
import streamlit as st
from groq import Groq


def _get_groq_key() -> str:
    """Load Groq API key from st.secrets or environment variable."""
    try:
        return st.secrets["GROQ_API_KEY"]
    except (KeyError, FileNotFoundError):
        pass
    return os.getenv("GROQ_API_KEY", "")


GROQ_MODEL = "llama3-70b-8192"

_client = None

def _get_client():
    global _client
    if _client is not None:
        return _client
    key = _get_groq_key().strip()
    if not key:
        return None
    try:
        _client = Groq(api_key=key)
        return _client
    except Exception:
        return None


# ══════════════════════════════════════════════════════════════════════════════
#  YOUR EXACT VALIDATOR PROMPT
# ══════════════════════════════════════════════════════════════════════════════
VALIDATOR_PROMPT_TEMPLATE = """You are a senior PostgreSQL query validator for an IPL analytics chatbot.

Your job is to verify whether a generated SQL query correctly answers the user's question.

USER QUESTION:
{user_question}

GENERATED SQL:
{generated_sql}

TASK:
1. Check if the SQL query correctly answers the question.
2. Check if the SQL uses correct tables and columns.
3. Check for logical errors in aggregations or joins.

If the SQL query is correct:
Return the same SQL.

If the SQL query is incorrect:
Return a corrected SQL query.

DATABASE SCHEMA (for reference):

"Matches"(
    match_id, season, match_date, match_city, match_venue,
    toss_winner, toss_decision, match_type,
    team1, team2, player_of_match, balls_per_over, overs,
    winner, win_by_runs, win_by_wickets,
    result, eliminator, match_key
)

innings(
    innings_id, match_id, innings_number,
    batting_team, bowling_team,
    total_runs, total_wickets, total_balls, total_overs,
    run_rate, target_runs, target_overs
)

deliveries(
    delivery_id, match_id, inning_number,
    over_number, ball_number,
    batter_id, bowler_id, non_striker_id,
    runs_batter, runs_extras, runs_total,
    is_wicket, dismissal_type, player_out_id
)

"Players"(player_id, player_name, registry_id)

player_teams(player_id, team_name, season)

Relationships:
- deliveries.batter_id     → players.player_id
- deliveries.bowler_id     → players.player_id
- deliveries.player_out_id → players.player_id
- deliveries.match_id      → matches.match_id
- innings.match_id         → matches.match_id
- player_teams.player_id   → players.player_id

RULES:
- Only allow SELECT queries.
- Do not generate INSERT, UPDATE, DELETE, or DROP.
- Ensure LIMIT is used for ranking queries.
- Ensure player names come from the players table.

CRITICAL DATA RULES — always check these in every query:
1. is_wicket is STRING: use is_wicket = 't' for wickets, NEVER is_wicket = TRUE or = 1
2. over_number range is 1-20: powerplay = over_number <= 6, death = over_number >= 16
3. player_of_match has format {"Name"}: always clean with REPLACE(REPLACE(player_of_match,'{"',''),'"}','')
4. Use COUNT(*) FILTER (WHERE condition) for conditional counts in PostgreSQL

OUTPUT FORMAT:
Return ONLY valid JSON — no markdown, no code fences, no extra text:
{{
  "validated_sql": "corrected_or_original_sql",
  "status": "valid | corrected",
  "explanation": "short explanation of validation"
}}"""


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN FUNCTION
# ══════════════════════════════════════════════════════════════════════════════
def validate_sql(user_question: str, generated_sql: str) -> dict:
    """
    Validate and optionally correct a Groq-generated SQL query.

    Args:
        user_question : original user question (e.g. "top 10 batsmen")
        generated_sql : SQL string from sql_generator.generate_sql()

    Returns dict:
        {
          validated_sql : str  — corrected or original SQL
          status        : str  — 'valid' | 'corrected' | 'skipped'
          explanation   : str  — short explanation
          source        : str  — 'validator' | 'passthrough'
        }
    """
    client = _get_client()

    # ── No API key → pass SQL through unchanged ───────────────────────────────
    if not client:
        return {
            "validated_sql": generated_sql,
            "status":        "skipped",
            "explanation":   "Validator skipped — no API key set.",
            "source":        "passthrough",
        }

    # ── Basic safety check before even calling the API ────────────────────────
    sql_upper = generated_sql.upper().strip()
    dangerous = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE", "CREATE"]
    for keyword in dangerous:
        if keyword in sql_upper:
            return {
                "validated_sql": generated_sql,
                "status":        "blocked",
                "explanation":   f"Query blocked — contains forbidden keyword: {keyword}",
                "source":        "validator",
            }

    if not sql_upper.startswith("SELECT"):
        return {
            "validated_sql": generated_sql,
            "status":        "blocked",
            "explanation":   "Query blocked — only SELECT queries are allowed.",
            "source":        "validator",
        }

    # ── Call Groq validator ───────────────────────────────────────────────────
    try:
        prompt = VALIDATOR_PROMPT_TEMPLATE.format(
            user_question=user_question,
            generated_sql=generated_sql,
        )

        response = _get_client().chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,    # zero temp = most deterministic validation
            max_tokens=600,
            stream=False,
        )

        raw = response.choices[0].message.content.strip()

        # Strip markdown fences if present
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$",           "", raw)

        result         = json.loads(raw)
        result["source"] = "validator"

        # Ensure validated_sql is never empty
        if not result.get("validated_sql", "").strip():
            result["validated_sql"] = generated_sql
            result["status"]        = "valid"

        return result

    except json.JSONDecodeError:
        # Validator returned non-JSON → use original SQL safely
        return {
            "validated_sql": generated_sql,
            "status":        "passthrough",
            "explanation":   "Validator returned unexpected format — using original SQL.",
            "source":        "passthrough",
        }
    except Exception as e:
        # API error → use original SQL safely
        return {
            "validated_sql": generated_sql,
            "status":        "passthrough",
            "explanation":   f"Validator error — using original SQL. ({str(e)[:60]})",
            "source":        "passthrough",
        }