"""
db.py — PostgreSQL connection for IPL NEXUS

Credential priority:
  1. st.secrets  → Streamlit Cloud (production)
  2. os.getenv() → local environment variables
"""

import os
import psycopg2
import psycopg2.pool
import pandas as pd
import streamlit as st
from typing import Optional, Tuple


def _get_db_config() -> dict:
    """
    Load DB credentials from st.secrets (Streamlit Cloud)
    or fall back to environment variables.
    Uses Session Pooler for Streamlit Cloud compatibility.
    """
    # ── Priority 1: st.secrets (Streamlit Cloud) ──────────────────────────────
    try:
        secrets = st.secrets["postgres"]
        return {
            "host":     secrets["host"],
            "port":     int(secrets.get("port", 5432)),
            "dbname":   secrets["dbname"],
            "user":     secrets["user"],
            "password": secrets["password"],
            "sslmode":  "require",
        }
    except (KeyError, FileNotFoundError):
        pass

    # ── Priority 2: Session Pooler fallback ───────────────────────────────────
    return {
        "host":     os.getenv("PG_HOST",     "aws-1-ap-south-1.pooler.supabase.com"),
        "port":     int(os.getenv("PG_PORT", "5432")),
        "dbname":   os.getenv("PG_DB",       "postgres"),
        "user":     os.getenv("PG_USER",     "postgres.qxgxodpethnqmwheyepq"),
        "password": os.getenv("PG_PASSWORD", "Vaishnani@2728"),
        "sslmode":  "require",
    }


# ── Connection pool ────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_pool():
    """
    Thread-safe PostgreSQL connection pool.
    Cached once per session — no reconnect overhead.
    """
    try:
        pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=5,
            connect_timeout=10,
            **_get_db_config(),       # ✅ uses correct function
        )
        return pool
    except psycopg2.OperationalError:
        return None


def run_query(sql: str) -> tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Execute a SQL SELECT query and return (DataFrame, error_string).
    Exactly one of the two will always be None.
    """
    pool = get_pool()
    if pool is None:
        return None, (
            "Cannot connect to PostgreSQL. "
            "Check your credentials in Streamlit Secrets."
        )

    conn = None
    try:
        conn = pool.getconn()
        with conn.cursor() as cur:
            cur.execute(sql)
            if cur.description is None:
                return pd.DataFrame(), None
            cols = [desc[0] for desc in cur.description]
            rows = cur.fetchmany(10_000)
            df   = pd.DataFrame(rows, columns=cols)
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="ignore")
            return df, None
    except psycopg2.Error as e:
        return None, f"SQL Error: {e.pgerror or str(e)}"
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"
    finally:
        if conn:
            pool.putconn(conn)


def test_connection() -> bool:
    """Quick ping — used by Test DB Connection button."""
    df, err = run_query("SELECT 1 AS ok")
    return err is None


# ── Schema context sent to Groq LLM ───────────────────────────────────────────
SCHEMA_CONTEXT = """
PostgreSQL database: postgres (Supabase)
Tables and columns:

matches(
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

players(player_id, player_name, registry_id)

player_teams(player_id, team_name, season)

Key relationships:
- deliveries.batter_id     → players.player_id
- deliveries.bowler_id     → players.player_id
- deliveries.player_out_id → players.player_id
- deliveries.match_id      → matches.match_id
- innings.match_id         → matches.match_id
- player_teams.player_id   → players.player_id

CRITICAL DATA FACTS:
- is_wicket stores 't' or 'f' (STRING) — use WHERE is_wicket = 't'
- over_number range is 1 to 20 (NOT 0 to 19)
- player_of_match format is {"Name"} — clean with REPLACE()
"""