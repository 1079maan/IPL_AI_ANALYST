"""
db.py — PostgreSQL connection + query execution for IPL NEXUS
Uses psycopg2 ThreadedConnectionPool for performance on large ball-by-ball datasets.

⚠️  Credentials are embedded below. After changing your DB password,
    update line 21 (password field) with your new password.
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
    or fall back to environment variables / hardcoded values.
    """
    # ── Priority 1: st.secrets (Streamlit Cloud) ──────────────────────────────
    try:
        secrets = st.secrets["postgres"]
        return {
            "host":     secrets["db.qxgxodpethnqmwheyepq.supabase.co"],
            "port":     int(secrets.get("port", 5432)),
            "dbname":   secrets["postgres"],
            "user":     secrets["postgres"],
            "password": secrets["Vaishnani@2728"],
        }
    except (KeyError, FileNotFoundError):
        pass

    # ── Priority 2: Environment variables ─────────────────────────────────────
    return {
        "host":     os.getenv("PG_HOST",     "localhost"),
        "port":     int(os.getenv("PG_PORT", "5432")),
        "dbname":   os.getenv("PG_DB",       "IPL_Data"),
        "user":     os.getenv("PG_USER",     "postgres"),
        "password": os.getenv("PG_PASSWORD", "Maan@2004"),
    }


# ── Database credentials ───────────────────────────────────────────────────────
# ⚠️  Update password below if you change it in pgAdmin
DB_CONFIG = {
    "host":     os.getenv("PG_HOST",     "localhost"),
    "port":     int(os.getenv("PG_PORT", "5432")),
    "dbname":   os.getenv("PG_DB",       "IPL_Data"),
    "user":     os.getenv("PG_USER",     "postgres"),
    "password": os.getenv("PG_PASSWORD", "Maan@2004"),
}

# ── Connection pool (cached once per Streamlit session) ───────────────────────
@st.cache_resource(show_spinner=False)
def get_pool():
    """
    Create a thread-safe PostgreSQL connection pool.
    min 1 connection, max 5 connections — suitable for Streamlit's threading model.
    """
    try:
        pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=5,
            connect_timeout=10,
            **DB_CONFIG,
        )
        return pool
    except psycopg2.OperationalError as e:
        return None   # handled gracefully in run_query()


def run_query(sql: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Execute a SQL SELECT query and return (DataFrame, error_string).
    Exactly one of the two return values will be None.

    Performance optimisations for 250K+ ball-by-ball rows:
      • Reuses pooled connections — no reconnect overhead per query
      • fetchmany(10_000) caps memory usage — SQL should always use LIMIT
      • pd.to_numeric(errors='ignore') keeps number columns numeric for charting
    """
    pool = get_pool()
    if pool is None:
        return None, (
            "❌ Cannot connect to PostgreSQL. "
            "Check your credentials in db.py (host / dbname / user / password)."
        )

    conn = None
    try:
        conn = pool.getconn()
        with conn.cursor() as cur:
            cur.execute(sql)
            if cur.description is None:
                return pd.DataFrame(), None         # query returned no rows
            cols = [desc[0] for desc in cur.description]
            rows = cur.fetchmany(10_000)             # safety cap
            df   = pd.DataFrame(rows, columns=cols)
            # Coerce numeric-looking columns so charts work correctly
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
    """Quick ping — used by the 'Test DB Connection' button in the sidebar."""
    df, err = run_query("SELECT 1 AS ok")
    return err is None


# ── Schema context (sent to Groq LLM so it understands the DB structure) ──────
SCHEMA_CONTEXT = """
PostgreSQL database: IPL_Data
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
"""
