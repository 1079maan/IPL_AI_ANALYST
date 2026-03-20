# """
# sql_generator.py — Natural Language → SQL using Groq LLM

# 3 Critical bugs fixed based on actual CSV data analysis:

# BUG 1 FIXED: is_wicket is STRING 't'/'f' — NOT boolean
#   WRONG:  WHERE is_wicket = TRUE  or  WHERE is_wicket = 1
#   FIXED:  WHERE is_wicket = 't'

# BUG 2 FIXED: over_number is 1–20 — NOT 0–19
#   WRONG:  WHERE over_number < 2   (returns only 1 over)
#   FIXED:  WHERE over_number <= 2  (returns overs 1 and 2)
#   Powerplay  = over_number <= 6
#   Death overs = over_number >= 16

# BUG 3 FIXED: player_of_match has format {"Name"} with curly braces
#   WRONG:  SELECT player_of_match
#   FIXED:  SELECT REPLACE(REPLACE(player_of_match,'{"',''),'"}','')
# """

# import os
# import re
# import json
# from groq import Groq
# from db import SCHEMA_CONTEXT

# # ═══════════════════════════════════════════════════════════════════════════════
# #  ⚠️  PASTE YOUR GROQ API KEY HERE
# #  Get a key → https://console.groq.com → API Keys → Create Key
# # ═══════════════════════════════════════════════════════════════════════════════
# GROQ_API_KEY = os.getenv("GROQ_API_KEY", "GrOQ_API_KEY")
# # ═══════════════════════════════════════════════════════════════════════════════

# GROQ_MODEL = "llama3-70b-8192"

# _client = None

# def _get_client():
#     global _client
#     if _client is not None:
#         return _client
#     key = GROQ_API_KEY.strip()
#     if not key or key == "GrOQ_API_KEY":
#         return None
#     try:
#         _client = Groq(api_key=key)
#         return _client
#     except Exception:
#         return None


# # ══════════════════════════════════════════════════════════════════════════════
# #  SYSTEM PROMPT — with all 3 data bugs documented for Groq
# # ══════════════════════════════════════════════════════════════════════════════
# SYSTEM_PROMPT = f"""You are an expert PostgreSQL data analyst for an IPL cricket database.

# {SCHEMA_CONTEXT}

# CRITICAL DATA FACTS — memorise these, never break these rules:

# 1. is_wicket column stores STRING values:
#    - 't' means wicket fell
#    - 'f' means no wicket
#    ALWAYS use: WHERE is_wicket = 't'
#    NEVER use:  WHERE is_wicket = TRUE  or  WHERE is_wicket = 1

# 2. over_number column range is 1 to 20 (NOT 0 to 19):
#    - First 2 overs   → WHERE over_number <= 2
#    - Powerplay       → WHERE over_number <= 6
#    - Middle overs    → WHERE over_number BETWEEN 7 AND 15
#    - Death overs     → WHERE over_number >= 16
#    NEVER use < 2 or < 6 or < 16 for over filters

# 3. player_of_match column stores values like {{"SR Tendulkar"}} with curly braces.
#    ALWAYS clean it using:
#    REPLACE(REPLACE(player_of_match, '{{\"', ''), '\"}}', '')  AS player_of_match
#    NEVER use raw player_of_match column directly.

# 4. runs_batter is the runs scored by batter (0-6).
#    Use SUM(runs_batter) for total batting runs.
#    Use COUNT(*) FILTER (WHERE runs_batter = 6) for sixes.
#    Use COUNT(*) FILTER (WHERE runs_batter = 4) for fours.

# 5. For probability calculations:
#    probability = ROUND(100.0 * COUNT(*) FILTER (WHERE condition) / NULLIF(COUNT(*),0), 2)

# OUTPUT FORMAT — strict JSON only, no markdown, no code fences:
# {{
#   "sql": "your SQL here",
#   "explanation": "1-2 sentence plain English explanation",
#   "chart_type": "bar or line or pie or scatter or none",
#   "chart_x": "column name for x-axis",
#   "chart_y": "column name for y-axis"
# }}

# RULES:
# - Only SELECT queries. Never INSERT/UPDATE/DELETE/DROP/ALTER.
# - Always LIMIT 10 for ranking queries.
# - Always JOIN players table for player names.
# - Always alias computed columns clearly."""


# # ══════════════════════════════════════════════════════════════════════════════
# #  KEYWORD MAP
# # ══════════════════════════════════════════════════════════════════════════════
# KEYWORD_MAP = {
#     # ── Probability / powerplay / over-based (HIGHEST PRIORITY) ──────────────
#     "probability of hitting six":   "six_probability_powerplay",
#     "probability of six":           "six_probability_powerplay",
#     "chance of six":                "six_probability_powerplay",
#     "chance of hitting":            "six_probability_powerplay",
#     "chance of a six":              "six_probability_powerplay",
#     "six in first":                 "six_probability_powerplay",
#     "six in powerplay":             "six_probability_powerplay",
#     "six probability":              "six_probability_powerplay",
#     "hitting six":                  "six_probability_powerplay",
#     "six in over":                  "six_probability_powerplay",
#     "six per over":                 "six_probability_powerplay",
#     "powerplay six":                "six_probability_powerplay",
#     "first two over":               "six_probability_powerplay",
#     "first 2 over":                 "six_probability_powerplay",
#     "percentage of sixes":          "six_probability_powerplay",  # ← FIX Q29
#     "sixes are hit":                "six_probability_powerplay",  # ← FIX Q29

#     # ── Wicket probability ────────────────────────────────────────────────────
#     "probability of a wicket":      "wicket_probability",         # ← FIX Q6
#     "probability of wicket":        "wicket_probability",
#     "wicket probability":           "wicket_probability",
#     "chance of wicket":             "wicket_probability",
#     "wicket falling":               "wicket_probability",         # ← FIX Q6
#     "wicket in powerplay":          "wicket_probability",
#     "powerplay wicket":             "wicket_probability",

#     # ── Win rate batting first/second ─────────────────────────────────────────
#     "win rate of teams":            "win_rate_batting",           # ← FIX Q2
#     "win rate batting":             "win_rate_batting",
#     "batting first vs":             "win_rate_batting",           # ← FIX Q2
#     "batting first win":            "win_rate_batting",
#     "batting second win":           "win_rate_batting",
#     "win batting first":            "win_rate_batting",
#     "win batting second":           "win_rate_batting",
#     "chasing win":                  "win_rate_batting",
#     "defending win":                "win_rate_batting",

#     # ── Win after score ───────────────────────────────────────────────────────
#     "percentage of matches are won": "win_after_score",           # ← FIX Q13
#     "matches are won by":            "win_after_score",           # ← FIX Q13
#     "teams scoring 180":             "win_after_score",
#     "win after scoring":             "win_after_score",
#     "probability of winning":        "win_after_score",
#     "win percentage scoring":        "win_after_score",
#     "score 160":                     "win_after_score",
#     "scoring 180":                   "win_after_score",           # ← FIX Q13

#     # ── Run rate difference powerplay vs death ────────────────────────────────
#     "run rate difference":          "over_run_rate",              # ← FIX Q11
#     "difference between powerplay": "over_run_rate",              # ← FIX Q11
#     "powerplay and death":          "over_run_rate",              # ← FIX Q11
#     "run rate per over":            "over_run_rate",
#     "over wise run":                "over_run_rate",
#     "six hitting rate":             "over_run_rate",
#     "run rate each over":           "over_run_rate",

#     # ── Batsmen / runs ────────────────────────────────────────────────────────
#     "top batsmen":      "top batsmen",
#     "top 10 batsmen":   "top batsmen",
#     "top batsman":      "top batsmen",
#     "best batsmen":     "top batsmen",
#     "best batsman":     "top batsmen",
#     "most runs":        "top batsmen",
#     "run scorer":       "top batsmen",
#     "highest run":      "top batsmen",
#     "all time bat":     "top batsmen",
#     "batsmen all":      "top batsmen",
#     "batsman":          "top batsmen",
#     "batting":          "top batsmen",
#     "who scored":       "top batsmen",
#     "scored most":      "top batsmen",

#     # ── Wickets / bowlers ─────────────────────────────────────────────────────
#     "top wicket":       "top wicket",
#     "most wicket":      "top wicket",
#     "best bowler":      "top wicket",
#     "highest wicket":   "top wicket",
#     "wicket taker":     "top wicket",
#     "wicket-taker":     "top wicket",
#     "bowling":          "top wicket",
#     "bowler":           "top wicket",
#     "took most":        "top wicket",

#     # ── Team wins ─────────────────────────────────────────────────────────────
#     "team win":         "team win",
#     "most win":         "team win",
#     "most wins":        "team win",
#     "best team":        "team win",
#     "win count":        "team win",
#     "which team":       "team win",
#     "team has most":    "team win",
#     "team standing":    "team win",
#     "team ranking":     "team win",
#     "ipl winner":       "team win",
#     "most title":       "team win",
#     "championship":     "team win",

#     # ── Season trends ─────────────────────────────────────────────────────────
#     "runs per season":  "runs per season",
#     "season trend":     "runs per season",
#     "runs over":        "runs per season",
#     "season run":       "runs per season",
#     "year wise run":    "runs per season",
#     "runs each season": "runs per season",

#     # ── Sixes ─────────────────────────────────────────────────────────────────
#     "most six":         "six",
#     "most sixes":       "six",
#     "maximum six":      "six",
#     "sixes hit":        "six",
#     "six hitter":       "six",
#     "hit most six":     "six",

#     # ── Fours ─────────────────────────────────────────────────────────────────
#     "most four":        "four",
#     "most fours":       "four",
#     "maximum four":     "four",
#     "fours hit":        "four",

#     # ── Toss ──────────────────────────────────────────────────────────────────
#     "toss impact":      "toss",
#     "toss effect":      "toss",
#     "toss result":      "toss",
#     "toss on result":   "toss",
#     "impact of toss":   "toss",
#     "toss win":         "toss",
#     "toss":             "toss",

#     # ── Player of match ───────────────────────────────────────────────────────
#     "player of match":  "player of match",
#     "man of match":     "player of match",
#     "best player":      "player of match",
#     "award":            "player of match",
#     "most award":       "player of match",
#     "most mom":         "player of match",

#     # ── Season matches ────────────────────────────────────────────────────────
#     "matches per season":  "season",
#     "season match":        "season",
#     "matches in season":   "season",
#     "matches each season": "season",

#     # ── Economy ───────────────────────────────────────────────────────────────
#     "economy":          "economy",
#     "best economy":     "economy",
#     "lowest economy":   "economy",
#     "economy rate":     "economy",

#     # ── Strike rate ───────────────────────────────────────────────────────────
#     "strike rate":      "strike rate",
#     "highest strike":   "strike rate",
#     "best strike":      "strike rate",

#     # ── Highest score ─────────────────────────────────────────────────────────
#     "highest score":        "highest score",
#     "highest team score":   "highest score",
#     "biggest score":        "highest score",
#     "highest total":        "highest score",
#     "highest innings":      "highest score",
# }


# # ══════════════════════════════════════════════════════════════════════════════
# #  FALLBACK QUERIES — all fixed for actual DB data format
# # ══════════════════════════════════════════════════════════════════════════════
# FALLBACK_QUERIES = {

#     # ── BUG FIXED: is_wicket='t', over_number 1-20 ───────────────────────────
#     "six_probability_powerplay": {
#         "sql": """
#             SELECT
#                 over_number,
#                 COUNT(*)                                                        AS total_balls,
#                 COUNT(*) FILTER (WHERE runs_batter = 6)                        AS total_sixes,
#                 ROUND(100.0 * COUNT(*) FILTER (WHERE runs_batter = 6)
#                       / NULLIF(COUNT(*), 0), 2)                                AS six_probability_pct
#             FROM deliveries
#             WHERE over_number <= 2
#             GROUP BY over_number
#             ORDER BY over_number
#         """,
#         "explanation": "Probability of hitting a six in overs 1 and 2. Calculated as (sixes ÷ total balls) × 100 per over.",
#         "chart_type": "bar", "chart_x": "over_number", "chart_y": "six_probability_pct",
#     },

#     "wicket_probability": {
#         "sql": """
#             SELECT
#                 over_number,
#                 COUNT(*)                                              AS total_balls,
#                 COUNT(*) FILTER (WHERE is_wicket = 't')              AS wickets,
#                 ROUND(100.0 * COUNT(*) FILTER (WHERE is_wicket = 't')
#                       / NULLIF(COUNT(*), 0), 2)                      AS wicket_probability_pct
#             FROM deliveries
#             WHERE over_number <= 6
#             GROUP BY over_number
#             ORDER BY over_number
#         """,
#         "explanation": "Probability of a wicket falling in each powerplay over (1-6).",
#         "chart_type": "bar", "chart_x": "over_number", "chart_y": "wicket_probability_pct",
#     },

#     "win_rate_batting": {
#         "sql": """
#             SELECT
#                 i.innings_number,
#                 CASE WHEN i.innings_number = 1 THEN 'Batting First'
#                      ELSE 'Batting Second' END                        AS strategy,
#                 COUNT(*)                                              AS total_matches,
#                 COUNT(*) FILTER (WHERE i.batting_team = m.winner)    AS wins,
#                 ROUND(100.0 * COUNT(*) FILTER (WHERE i.batting_team = m.winner)
#                       / NULLIF(COUNT(*), 0), 1)                      AS win_pct
#             FROM innings i
#             JOIN matches m ON i.match_id = m.match_id
#             WHERE m.winner IS NOT NULL
#               AND m.result != 'no result'
#             GROUP BY i.innings_number
#             ORDER BY i.innings_number
#         """,
#         "explanation": "Win rate for teams batting first vs batting second across all IPL matches.",
#         "chart_type": "bar", "chart_x": "strategy", "chart_y": "win_pct",
#     },

#     "venue_avg_score": {
#         "sql": """
#             SELECT
#                 m.match_venue                         AS venue,
#                 ROUND(AVG(i.total_runs), 1)           AS avg_score,
#                 COUNT(*)                              AS matches,
#                 MAX(i.total_runs)                     AS highest_score
#             FROM innings i
#             JOIN matches m ON i.match_id = m.match_id
#             WHERE i.innings_number = 1
#             GROUP BY m.match_venue
#             HAVING COUNT(*) >= 5
#             ORDER BY avg_score DESC
#             LIMIT 10
#         """,
#         "explanation": "IPL venues ranked by average first innings score — minimum 5 matches played.",
#         "chart_type": "bar", "chart_x": "venue", "chart_y": "avg_score",
#     },

#     "death_over_stats": {
#         "sql": """
#             SELECT
#                 over_number,
#                 COUNT(*)                                              AS total_balls,
#                 SUM(runs_total)                                       AS total_runs,
#                 COUNT(*) FILTER (WHERE runs_batter = 6)              AS sixes,
#                 COUNT(*) FILTER (WHERE runs_batter = 4)              AS fours,
#                 COUNT(*) FILTER (WHERE is_wicket = 't')              AS wickets,
#                 ROUND(SUM(runs_total) * 6.0 / NULLIF(COUNT(*),0), 2) AS run_rate
#             FROM deliveries
#             WHERE over_number >= 16
#             GROUP BY over_number
#             ORDER BY over_number
#         """,
#         "explanation": "Death overs (16-20) statistics — runs, sixes, fours, wickets and run rate per over.",
#         "chart_type": "bar", "chart_x": "over_number", "chart_y": "run_rate",
#     },

#     "powerplay_stats": {
#         "sql": """
#             SELECT
#                 over_number,
#                 COUNT(*)                                               AS total_balls,
#                 SUM(runs_total)                                        AS total_runs,
#                 COUNT(*) FILTER (WHERE runs_batter = 6)               AS sixes,
#                 COUNT(*) FILTER (WHERE runs_batter = 4)               AS fours,
#                 COUNT(*) FILTER (WHERE is_wicket = 't')               AS wickets,
#                 ROUND(SUM(runs_total) * 6.0 / NULLIF(COUNT(*), 0), 2) AS run_rate
#             FROM deliveries
#             WHERE over_number <= 6
#             GROUP BY over_number
#             ORDER BY over_number
#         """,
#         "explanation": "Powerplay (overs 1-6) statistics — runs, sixes, fours, wickets and run rate per over.",
#         "chart_type": "bar", "chart_x": "over_number", "chart_y": "run_rate",
#     },

#     "over_run_rate": {
#         "sql": """
#             SELECT
#                 over_number,
#                 ROUND(SUM(runs_total) * 6.0 / NULLIF(COUNT(*), 0), 2)  AS run_rate,
#                 COUNT(*) FILTER (WHERE runs_batter = 6)                 AS sixes,
#                 ROUND(100.0 * COUNT(*) FILTER (WHERE runs_batter = 6)
#                       / NULLIF(COUNT(*), 0), 2)                         AS six_pct
#             FROM deliveries
#             GROUP BY over_number
#             ORDER BY over_number
#         """,
#         "explanation": "Run rate and six-hitting percentage across all 20 overs in IPL history.",
#         "chart_type": "line", "chart_x": "over_number", "chart_y": "run_rate",
#     },

#     "super_over": {
#         "sql": """
#             SELECT
#                 COUNT(*)          AS super_over_matches,
#                 MIN(season)       AS first_season,
#                 MAX(season)       AS last_season
#             FROM matches
#             WHERE eliminator IS NOT NULL
#               AND eliminator != ''
#         """,
#         "explanation": "Total number of IPL matches that were decided by a Super Over.",
#         "chart_type": "none", "chart_x": "", "chart_y": "",
#     },

#     "win_after_score": {
#         "sql": """
#             SELECT
#                 CASE
#                     WHEN i.total_runs >= 200 THEN '200+'
#                     WHEN i.total_runs >= 180 THEN '180-199'
#                     WHEN i.total_runs >= 160 THEN '160-179'
#                     WHEN i.total_runs >= 140 THEN '140-159'
#                     ELSE 'Under 140'
#                 END                                                    AS score_bracket,
#                 COUNT(*)                                               AS matches,
#                 COUNT(*) FILTER (WHERE i.batting_team = m.winner)     AS wins,
#                 ROUND(100.0 * COUNT(*) FILTER (WHERE i.batting_team = m.winner)
#                       / NULLIF(COUNT(*), 0), 1)                        AS win_pct
#             FROM innings i
#             JOIN matches m ON i.match_id = m.match_id
#             WHERE i.innings_number = 1
#               AND m.winner IS NOT NULL
#               AND m.result != 'no result'
#             GROUP BY score_bracket
#             ORDER BY MIN(i.total_runs) DESC
#         """,
#         "explanation": "Win percentage for teams batting first based on their total score bracket.",
#         "chart_type": "bar", "chart_x": "score_bracket", "chart_y": "win_pct",
#     },

#     "avg_first_innings": {
#         "sql": """
#             SELECT
#                 m.season,
#                 ROUND(AVG(i.total_runs), 1)   AS avg_first_innings_score,
#                 MAX(i.total_runs)              AS highest_score,
#                 MIN(i.total_runs)              AS lowest_score,
#                 COUNT(*)                       AS matches
#             FROM innings i
#             JOIN matches m ON i.match_id = m.match_id
#             WHERE i.innings_number = 1
#             GROUP BY m.season
#             ORDER BY m.season
#         """,
#         "explanation": "Average first innings score per IPL season — shows how totals have grown over the years.",
#         "chart_type": "line", "chart_x": "season", "chart_y": "avg_first_innings_score",
#     },

#     "dot_ball": {
#         "sql": """
#             SELECT
#                 p.player_name,
#                 COUNT(*)                                               AS total_balls,
#                 COUNT(*) FILTER (WHERE d.runs_total = 0)              AS dot_balls,
#                 ROUND(100.0 * COUNT(*) FILTER (WHERE d.runs_total = 0)
#                       / NULLIF(COUNT(*), 0), 1)                        AS dot_ball_pct
#             FROM deliveries d
#             JOIN players p ON d.bowler_id = p.player_id
#             GROUP BY p.player_name
#             HAVING COUNT(*) >= 300
#             ORDER BY dot_ball_pct DESC
#             LIMIT 10
#         """,
#         "explanation": "Bowlers with the highest dot ball percentage — minimum 300 balls bowled.",
#         "chart_type": "bar", "chart_x": "player_name", "chart_y": "dot_ball_pct",
#     },

#     # ── BUG FIXED: is_wicket = 't' not TRUE ──────────────────────────────────
#     "top batsmen": {
#         "sql": """
#             SELECT
#                 p.player_name,
#                 SUM(d.runs_batter)            AS total_runs,
#                 COUNT(DISTINCT d.match_id)    AS matches,
#                 ROUND(SUM(d.runs_batter) * 100.0
#                       / NULLIF(COUNT(*), 0), 2) AS strike_rate
#             FROM deliveries d
#             JOIN players p ON d.batter_id = p.player_id
#             GROUP BY p.player_name
#             ORDER BY total_runs DESC
#             LIMIT 10
#         """,
#         "explanation": "Top 10 run-scorers in IPL history with strike rate.",
#         "chart_type": "bar", "chart_x": "player_name", "chart_y": "total_runs",
#     },

#     "top wicket": {
#         "sql": """
#             SELECT
#                 p.player_name,
#                 COUNT(*) FILTER (WHERE d.is_wicket = 't'
#                     AND d.dismissal_type NOT IN
#                     ('run out','retired hurt','obstructing the field')) AS wickets,
#                 COUNT(DISTINCT d.match_id)                             AS matches
#             FROM deliveries d
#             JOIN players p ON d.bowler_id = p.player_id
#             GROUP BY p.player_name
#             ORDER BY wickets DESC
#             LIMIT 10
#         """,
#         "explanation": "Top 10 wicket-takers in IPL history (excludes run-outs).",
#         "chart_type": "bar", "chart_x": "player_name", "chart_y": "wickets",
#     },

#     "team win": {
#         "sql": """
#             SELECT winner AS team,
#                    COUNT(*) AS wins
#             FROM matches
#             WHERE winner IS NOT NULL
#               AND result != 'no result'
#             GROUP BY winner
#             ORDER BY wins DESC
#             LIMIT 10
#         """,
#         "explanation": "IPL teams ranked by total wins across all seasons.",
#         "chart_type": "bar", "chart_x": "team", "chart_y": "wins",
#     },

#     "runs per season": {
#         "sql": """
#             SELECT m.season,
#                    SUM(d.runs_total)          AS total_runs,
#                    COUNT(DISTINCT d.match_id) AS matches
#             FROM deliveries d
#             JOIN matches m ON d.match_id = m.match_id
#             GROUP BY m.season
#             ORDER BY m.season
#         """,
#         "explanation": "Total runs scored in each IPL season showing growth over the years.",
#         "chart_type": "line", "chart_x": "season", "chart_y": "total_runs",
#     },

#     "highest score": {
#         "sql": """
#             SELECT m.season, i.batting_team,
#                    i.total_runs, i.total_wickets, m.match_venue
#             FROM innings i
#             JOIN matches m ON i.match_id = m.match_id
#             ORDER BY i.total_runs DESC
#             LIMIT 10
#         """,
#         "explanation": "Highest team innings totals ever recorded in IPL history.",
#         "chart_type": "bar", "chart_x": "batting_team", "chart_y": "total_runs",
#     },

#     "six": {
#         "sql": """
#             SELECT p.player_name,
#                    COUNT(*) FILTER (WHERE d.runs_batter = 6) AS sixes
#             FROM deliveries d
#             JOIN players p ON d.batter_id = p.player_id
#             GROUP BY p.player_name
#             ORDER BY sixes DESC
#             LIMIT 10
#         """,
#         "explanation": "Players with the most sixes hit in IPL history.",
#         "chart_type": "bar", "chart_x": "player_name", "chart_y": "sixes",
#     },

#     "four": {
#         "sql": """
#             SELECT p.player_name,
#                    COUNT(*) FILTER (WHERE d.runs_batter = 4) AS fours
#             FROM deliveries d
#             JOIN players p ON d.batter_id = p.player_id
#             GROUP BY p.player_name
#             ORDER BY fours DESC
#             LIMIT 10
#         """,
#         "explanation": "Players with the most fours hit in IPL history.",
#         "chart_type": "bar", "chart_x": "player_name", "chart_y": "fours",
#     },

#     "toss": {
#         "sql": """
#             SELECT
#                 toss_decision,
#                 COUNT(*)                                                     AS times_chosen,
#                 COUNT(*) FILTER (WHERE toss_winner = winner)                 AS wins_after_toss,
#                 ROUND(100.0 * COUNT(*) FILTER (WHERE toss_winner = winner)
#                       / NULLIF(COUNT(*), 0), 1)                              AS win_pct
#             FROM matches
#             WHERE result != 'no result'
#               AND winner IS NOT NULL
#             GROUP BY toss_decision
#         """,
#         "explanation": "Win percentage after winning the toss — bat vs field decision.",
#         "chart_type": "pie", "chart_x": "toss_decision", "chart_y": "wins_after_toss",
#     },

#     # ── BUG FIXED: player_of_match curly brace cleaned ───────────────────────
#     "player of match": {
#         "sql": """
#             SELECT
#                 REPLACE(REPLACE(player_of_match, '{"', ''), '"}', '')
#                                   AS player,
#                 COUNT(*)          AS awards
#             FROM matches
#             WHERE player_of_match IS NOT NULL
#             GROUP BY player_of_match
#             ORDER BY awards DESC
#             LIMIT 10
#         """,
#         "explanation": "Players with the most Player of the Match awards in IPL history.",
#         "chart_type": "bar", "chart_x": "player", "chart_y": "awards",
#     },

#     "season": {
#         "sql": """
#             SELECT season, COUNT(*) AS matches
#             FROM matches
#             GROUP BY season
#             ORDER BY season
#         """,
#         "explanation": "Total matches played in each IPL season from 2008 to 2025.",
#         "chart_type": "bar", "chart_x": "season", "chart_y": "matches",
#     },

#     "economy": {
#         "sql": """
#             SELECT
#                 p.player_name,
#                 ROUND(SUM(d.runs_total) * 6.0 / NULLIF(COUNT(*), 0), 2) AS economy_rate,
#                 COUNT(DISTINCT d.match_id)                                AS matches
#             FROM deliveries d
#             JOIN players p ON d.bowler_id = p.player_id
#             GROUP BY p.player_name
#             HAVING COUNT(DISTINCT d.match_id) >= 10
#             ORDER BY economy_rate ASC
#             LIMIT 10
#         """,
#         "explanation": "Bowlers with the best economy rates in IPL — minimum 10 matches.",
#         "chart_type": "bar", "chart_x": "player_name", "chart_y": "economy_rate",
#     },

#     "strike rate": {
#         "sql": """
#             SELECT
#                 p.player_name,
#                 ROUND(SUM(d.runs_batter) * 100.0 / NULLIF(COUNT(*), 0), 2) AS strike_rate,
#                 SUM(d.runs_batter)                                           AS total_runs
#             FROM deliveries d
#             JOIN players p ON d.batter_id = p.player_id
#             GROUP BY p.player_name
#             HAVING SUM(d.runs_batter) >= 500
#             ORDER BY strike_rate DESC
#             LIMIT 10
#         """,
#         "explanation": "Batsmen with the highest strike rates — minimum 500 runs scored.",
#         "chart_type": "bar", "chart_x": "player_name", "chart_y": "strike_rate",
#     },
# }


# # ══════════════════════════════════════════════════════════════════════════════
# #  SMART FALLBACK
# # ══════════════════════════════════════════════════════════════════════════════
# # ══════════════════════════════════════════════════════════════════════════════
# #  DATA LIMITATION HANDLER
# #  Detects questions that need data NOT available in the IPL dataset.
# #  Instead of showing wrong answer or error — shows friendly message
# #  AND suggests the closest available answer.
# # ══════════════════════════════════════════════════════════════════════════════

# # Each entry:
# #   "trigger keywords" → {
# #       missing  : what data is missing
# #       suggest  : closest available answer key from FALLBACK_QUERIES
# #       message  : friendly explanation shown to user
# #   }
# DATA_LIMITATIONS = [
#     {
#         "triggers": ["bouncy", "flat pitch", "pitch type", "pitch condition",
#                      "hard pitch", "slow pitch", "turning pitch", "spin friendly",
#                      "pace friendly", "green pitch", "dry pitch"],
#         "missing": "pitch type / pitch condition",
#         "suggest": "top wicket",
#         "message": (
#             "⚠️ Your question asks about **pitch type** (bouncy / flat / turning), "
#             "but this information is **not recorded** in the IPL dataset. "
#             "The dataset does not have a pitch condition column.\n\n"
#             "📊 **Closest available answer:** I can show you the "
#             "**top wicket-takers overall**, or wickets by venue "
#             "(different venues have different pitch characteristics).\n\n"
#             "💡 Try asking: *'Which bowler has most wickets at Wankhede Stadium?'* "
#             "or *'Top wicket takers in IPL'*"
#         ),
#     },
#     {
#         "triggers": ["salary", "auction price", "contract value", "ipl auction",
#                      "how much paid", "earning", "wage", "fee"],
#         "missing": "player salary / auction price",
#         "suggest": "top batsmen",
#         "message": (
#             "⚠️ Your question asks about **player salary or auction price**, "
#             "but this information is **not available** in the IPL dataset. "
#             "The dataset only contains match and ball-by-ball performance data.\n\n"
#             "📊 **Closest available answer:** I can show you the "
#             "**top run-scorers** or **Player of Match award winners** "
#             "which reflect player value through performance.\n\n"
#             "💡 Try asking: *'Top 10 batsmen all time'* "
#             "or *'Player of match awards'*"
#         ),
#     },
#     {
#         "triggers": ["injury", "fitness", "medical", "physio", "rehabilitation",
#                      "injured", "health", "recovery", "concussion"],
#         "missing": "player injury / fitness records",
#         "suggest": None,
#         "message": (
#             "⚠️ Your question asks about **player injuries or fitness**, "
#             "but this information is **not available** in the IPL dataset. "
#             "The dataset only contains on-field performance data.\n\n"
#             "❌ There is no similar data available to suggest as an alternative.\n\n"
#             "💡 Try asking performance questions like: "
#             "*'Top 10 batsmen'*, *'Best economy bowlers'*, "
#             "or *'Most sixes in IPL'*"
#         ),
#     },
#     {
#         "triggers": ["crowd", "attendance", "spectator", "audience",
#                      "stadium capacity", "ticket", "viewership"],
#         "missing": "crowd attendance / stadium capacity",
#         "suggest": "venue_avg_score",
#         "message": (
#             "⚠️ Your question asks about **crowd attendance**, "
#             "but this information is **not recorded** in the IPL dataset.\n\n"
#             "📊 **Closest available answer:** I can show you "
#             "**average scores per venue**, which shows the most active stadiums.\n\n"
#             "💡 Try asking: *'Which venue has the highest average score?'*"
#         ),
#     },
#     {
#         "triggers": ["weather", "rain", "dew", "humidity", "temperature",
#                      "wind", "cloudy", "overcast", "climate"],
#         "missing": "weather conditions",
#         "suggest": "toss",
#         "message": (
#             "⚠️ Your question asks about **weather conditions**, "
#             "but weather data is **not recorded** in the IPL dataset.\n\n"
#             "📊 **Closest available answer:** I can show you "
#             "**toss decisions and win rates**, as teams often choose to "
#             "field first due to dew factor in evening matches.\n\n"
#             "💡 Try asking: *'Toss impact on results'*"
#         ),
#     },
#     {
#         "triggers": ["age", "date of birth", "born", "nationality",
#                      "country", "international", "height", "weight"],
#         "missing": "player personal details (age, nationality, height)",
#         "suggest": "top batsmen",
#         "message": (
#             "⚠️ Your question asks about **player personal details** "
#             "(age / nationality / physical attributes), "
#             "but this information is **not in the IPL dataset**. "
#             "Only player names and team information are available.\n\n"
#             "📊 **Closest available answer:** I can show you "
#             "**player performance stats** instead.\n\n"
#             "💡 Try asking: *'Top 10 batsmen'* or *'Top wicket takers'*"
#         ),
#     },
#     {
#         "triggers": ["social media", "twitter", "instagram", "follower",
#                      "fan following", "popular", "celebrity"],
#         "missing": "social media / popularity data",
#         "suggest": "player of match",
#         "message": (
#             "⚠️ Your question asks about **social media or popularity**, "
#             "but this data is **not available** in the IPL dataset.\n\n"
#             "📊 **Closest available answer:** I can show you "
#             "**Player of Match award winners** as a measure of on-field popularity.\n\n"
#             "💡 Try asking: *'Player of match awards'*"
#         ),
#     },
#     {
#         "triggers": ["coach", "captain history", "management", "support staff",
#                      "trainer", "analyst", "selector"],
#         "missing": "team management / coaching staff data",
#         "suggest": "team win",
#         "message": (
#             "⚠️ Your question asks about **coaching staff or team management**, "
#             "but this information is **not recorded** in the IPL dataset.\n\n"
#             "📊 **Closest available answer:** I can show you "
#             "**team win records** which reflect overall team performance.\n\n"
#             "💡 Try asking: *'Which team has most wins?'*"
#         ),
#     },
#     {
#         "triggers": ["net run rate", "nrr", "points table", "qualification",
#                      "playoff", "standing point"],
#         "missing": "points table / net run rate",
#         "suggest": "team win",
#         "message": (
#             "⚠️ Your question asks about the **points table or net run rate**, "
#             "but this is **not stored** in the IPL dataset. "
#             "Only individual match results are available.\n\n"
#             "📊 **Closest available answer:** I can show you "
#             "**total wins per team** across all seasons.\n\n"
#             "💡 Try asking: *'Which team has most wins?'*"
#         ),
#     },
#     {
#         "triggers": ["broadcast", "tv rights", "sponsorship", "revenue",
#                      "prize money", "commercial"],
#         "missing": "financial / commercial data",
#         "suggest": None,
#         "message": (
#             "⚠️ Your question asks about **IPL finances or commercial data**, "
#             "but this information is **not in the dataset**. "
#             "The dataset only contains on-field cricket data.\n\n"
#             "❌ No similar data is available as an alternative.\n\n"
#             "💡 Try asking performance questions like: "
#             "*'Top 10 batsmen'*, *'Most sixes in IPL'*"
#         ),
#     },
# ]


# def _check_data_limitation(question: str) -> dict | None:
#     """
#     Check if the question asks for data that is NOT in the IPL dataset.
#     Returns a limitation response dict if found, else None.
#     """
#     q = question.lower()
#     for limitation in DATA_LIMITATIONS:
#         for trigger in limitation["triggers"]:
#             if trigger in q:
#                 # Build response
#                 suggest_key = limitation.get("suggest")
#                 suggest_sql = None
#                 if suggest_key and suggest_key in FALLBACK_QUERIES:
#                     suggest_sql = FALLBACK_QUERIES[suggest_key]

#                 return {
#                     "sql":         suggest_sql["sql"] if suggest_sql else "",
#                     "explanation": limitation["message"],
#                     "chart_type":  suggest_sql["chart_type"] if suggest_sql else "none",
#                     "chart_x":     suggest_sql.get("chart_x", "") if suggest_sql else "",
#                     "chart_y":     suggest_sql.get("chart_y", "") if suggest_sql else "",
#                     "source":      "limitation",
#                     "limited":     True,
#                 }
#     return None


# # ══════════════════════════════════════════════════════════════════════════════
# #  SMART FALLBACK
# # ══════════════════════════════════════════════════════════════════════════════
# def _fallback(question: str) -> dict:
#     q = question.lower().strip()

#     # ── Step 1: Greetings → friendly reply ───────────────────────────────────
#     greetings = ["hello", "hi", "hey", "how are you", "what's up",
#                  "good morning", "good evening", "thanks", "thank you",
#                  "bye", "ok", "okay", "test", "testing"]
#     if any(g == q or q.startswith(g) for g in greetings):
#         return {
#             "sql": "",
#             "explanation": (
#                 "👋 Hello! I am IPL NEXUS AI. "
#                 "Ask me any IPL cricket question! Try: "
#                 "'Top 10 batsmen', 'Top wicket takers', "
#                 "'Probability of six in first two overs', "
#                 "'Win rate batting first', 'Death over stats'."
#             ),
#             "chart_type": "none", "chart_x": "", "chart_y": "",
#             "source": "fallback",
#         }

#     # ── Step 2: KEYWORD_MAP (longest match wins) ──────────────────────────────
#     sorted_kws = sorted(KEYWORD_MAP.keys(), key=len, reverse=True)
#     for kw in sorted_kws:
#         if kw in q:
#             key = KEYWORD_MAP[kw]
#             if key in FALLBACK_QUERIES:
#                 return {**FALLBACK_QUERIES[key], "source": "fallback"}

#     # ── Step 3: direct FALLBACK_QUERIES keys ──────────────────────────────────
#     for key in FALLBACK_QUERIES:
#         if key in q:
#             return {**FALLBACK_QUERIES[key], "source": "fallback"}

#     # ── Step 4: no match → helpful message ────────────────────────────────────
#     return {
#         "sql": "",
#         "explanation": (
#             "❓ I could not find data for that question. "
#             "The IPL dataset contains: match results, ball-by-ball deliveries, "
#             "player stats, team info, and venue data.\n\n"
#             "Try asking:\n"
#             "• *Top 10 batsmen all time*\n"
#             "• *Top wicket takers*\n"
#             "• *Which team has most wins*\n"
#             "• *Runs per season trend*\n"
#             "• *Probability of six in first two overs*\n"
#             "• *Win rate batting first vs second*\n"
#             "• *Death over statistics*\n"
#             "• *Toss impact on results*\n"
#             "• *Player of match awards*\n"
#             "• *Best economy bowlers*"
#         ),
#         "chart_type": "none", "chart_x": "", "chart_y": "",
#         "source": "fallback",
#     }


# # ══════════════════════════════════════════════════════════════════════════════
# #  MAIN FUNCTION
# # ══════════════════════════════════════════════════════════════════════════════
# def generate_sql(question: str) -> dict:
#     """
#     Full pipeline:
#       1. Check DATA_LIMITATIONS  → if question needs missing data, explain + suggest
#       2. Try Groq LLM            → generate SQL from question
#       3. Fallback                → pre-built templates or helpful message
#     """

#     # ── Step 1: Check data limitations FIRST ─────────────────────────────────
#     limitation = _check_data_limitation(question)
#     if limitation:
#         return limitation

#     # ── Step 2: Try Groq LLM ─────────────────────────────────────────────────
#     client = _get_client()

#     if client:
#         for attempt in range(2):
#             try:
#                 response = client.chat.completions.create(
#                     model=GROQ_MODEL,
#                     messages=[
#                         {"role": "system", "content": SYSTEM_PROMPT},
#                         {"role": "user",   "content": question},
#                     ],
#                     temperature=0.0 if attempt == 0 else 0.1,
#                     max_tokens=800,
#                     stream=False,
#                 )

#                 raw = response.choices[0].message.content.strip()
#                 raw = re.sub(r"^```(?:json)?\s*", "", raw)
#                 raw = re.sub(r"\s*```$",           "", raw)

#                 json_match = re.search(r'\{.*\}', raw, re.DOTALL)
#                 if json_match:
#                     raw = json_match.group(0)

#                 result           = json.loads(raw)
#                 result["source"] = "groq"

#                 sql = result.get("sql", "").strip().upper()
#                 if not sql or not sql.startswith("SELECT"):
#                     continue

#                 return result

#             except json.JSONDecodeError:
#                 continue
#             except Exception:
#                 break

#     # ── Step 3: Smart fallback ────────────────────────────────────────────────
#     return _fallback(question)




"""
sql_generator.py — Natural Language → SQL using Groq LLM

HOW TO SET YOUR GROQ API KEY:

  ── Streamlit Cloud (production) ──────────────────────────────
  Go to: share.streamlit.io → Your App → Settings → Secrets
  Add this line:

    GROQ_API_KEY = "gsk_your_key_here"

  ── Local development ──────────────────────────────────────────
  Create .streamlit/secrets.toml in your project:

    GROQ_API_KEY = "gsk_your_key_here"
"""

"""
sql_generator.py — Natural Language → SQL using Groq LLM

HOW TO SET YOUR GROQ API KEY:

  ── Streamlit Cloud (production) ──────────────────────────────
  Go to: share.streamlit.io → Your App → Settings → Secrets
  Add this line:

    GROQ_API_KEY = "gsk_your_key_here"

  ── Local development ──────────────────────────────────────────
  Create .streamlit/secrets.toml in your project:

    GROQ_API_KEY = "gsk_your_key_here"
"""

import os
import re
import json
import streamlit as st
from groq import Groq
from db import SCHEMA_CONTEXT


def _get_groq_key() -> str:
    """Load Groq API key from st.secrets or environment variable."""
    # Priority 1: st.secrets (Streamlit Cloud)
    try:
        return st.secrets["GROQ_API_KEY"]
    except (KeyError, FileNotFoundError):
        pass
    # Priority 2: environment variable
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
#  SYSTEM PROMPT — with all 3 data bugs documented for Groq
# ══════════════════════════════════════════════════════════════════════════════
SYSTEM_PROMPT = f"""You are an expert PostgreSQL data analyst for an IPL cricket database.

{SCHEMA_CONTEXT}

CRITICAL DATA FACTS — memorise these, never break these rules:

1. is_wicket column stores STRING values:
   - 't' means wicket fell
   - 'f' means no wicket
   ALWAYS use: WHERE is_wicket = 't'
   NEVER use:  WHERE is_wicket = TRUE  or  WHERE is_wicket = 1

2. over_number column range is 1 to 20 (NOT 0 to 19):
   - First 2 overs   → WHERE over_number <= 2
   - Powerplay       → WHERE over_number <= 6
   - Middle overs    → WHERE over_number BETWEEN 7 AND 15
   - Death overs     → WHERE over_number >= 16
   NEVER use < 2 or < 6 or < 16 for over filters

3. player_of_match column stores values like {{"SR Tendulkar"}} with curly braces.
   ALWAYS clean it using:
   REPLACE(REPLACE(player_of_match, '{{\"', ''), '\"}}', '')  AS player_of_match
   NEVER use raw player_of_match column directly.

4. runs_batter is the runs scored by batter (0-6).
   Use SUM(runs_batter) for total batting runs.
   Use COUNT(*) FILTER (WHERE runs_batter = 6) for sixes.
   Use COUNT(*) FILTER (WHERE runs_batter = 4) for fours.

5. For probability calculations:
   probability = ROUND(100.0 * COUNT(*) FILTER (WHERE condition) / NULLIF(COUNT(*),0), 2)

OUTPUT FORMAT — strict JSON only, no markdown, no code fences:
{{
  "sql": "your SQL here",
  "explanation": "1-2 sentence plain English explanation",
  "chart_type": "bar or line or pie or scatter or none",
  "chart_x": "column name for x-axis",
  "chart_y": "column name for y-axis"
}}

RULES:
- Only SELECT queries. Never INSERT/UPDATE/DELETE/DROP/ALTER.
- Always LIMIT 10 for ranking queries.
- Always JOIN players table for player names.
- Always alias computed columns clearly.
- CRITICAL: Table names are case-sensitive. Use exactly: "Matches" (capital M), "Players" (capital P), deliveries, innings, player_teams (lowercase)"""


# ══════════════════════════════════════════════════════════════════════════════
#  KEYWORD MAP
# ══════════════════════════════════════════════════════════════════════════════
KEYWORD_MAP = {
    # ── Probability / powerplay / over-based (HIGHEST PRIORITY) ──────────────
    "probability of hitting six":   "six_probability_powerplay",
    "probability of six":           "six_probability_powerplay",
    "chance of six":                "six_probability_powerplay",
    "chance of hitting":            "six_probability_powerplay",
    "chance of a six":              "six_probability_powerplay",
    "six in first":                 "six_probability_powerplay",
    "six in powerplay":             "six_probability_powerplay",
    "six probability":              "six_probability_powerplay",
    "hitting six":                  "six_probability_powerplay",
    "six in over":                  "six_probability_powerplay",
    "six per over":                 "six_probability_powerplay",
    "powerplay six":                "six_probability_powerplay",
    "first two over":               "six_probability_powerplay",
    "first 2 over":                 "six_probability_powerplay",
    "percentage of sixes":          "six_probability_powerplay",  # ← FIX Q29
    "sixes are hit":                "six_probability_powerplay",  # ← FIX Q29

    # ── Wicket probability ────────────────────────────────────────────────────
    "probability of a wicket":      "wicket_probability",         # ← FIX Q6
    "probability of wicket":        "wicket_probability",
    "wicket probability":           "wicket_probability",
    "chance of wicket":             "wicket_probability",
    "wicket falling":               "wicket_probability",         # ← FIX Q6
    "wicket in powerplay":          "wicket_probability",
    "powerplay wicket":             "wicket_probability",

    # ── Win rate batting first/second ─────────────────────────────────────────
    "win rate of teams":            "win_rate_batting",           # ← FIX Q2
    "win rate batting":             "win_rate_batting",
    "batting first vs":             "win_rate_batting",           # ← FIX Q2
    "batting first win":            "win_rate_batting",
    "batting second win":           "win_rate_batting",
    "win batting first":            "win_rate_batting",
    "win batting second":           "win_rate_batting",
    "chasing win":                  "win_rate_batting",
    "defending win":                "win_rate_batting",

    # ── Win after score ───────────────────────────────────────────────────────
    "percentage of matches are won": "win_after_score",           # ← FIX Q13
    "matches are won by":            "win_after_score",           # ← FIX Q13
    "teams scoring 180":             "win_after_score",
    "win after scoring":             "win_after_score",
    "probability of winning":        "win_after_score",
    "win percentage scoring":        "win_after_score",
    "score 160":                     "win_after_score",
    "scoring 180":                   "win_after_score",           # ← FIX Q13

    # ── Run rate difference powerplay vs death ────────────────────────────────
    "run rate difference":          "over_run_rate",              # ← FIX Q11
    "difference between powerplay": "over_run_rate",              # ← FIX Q11
    "powerplay and death":          "over_run_rate",              # ← FIX Q11
    "run rate per over":            "over_run_rate",
    "over wise run":                "over_run_rate",
    "six hitting rate":             "over_run_rate",
    "run rate each over":           "over_run_rate",

    # ── Batsmen / runs ────────────────────────────────────────────────────────
    "top batsmen":      "top batsmen",
    "top 10 batsmen":   "top batsmen",
    "top batsman":      "top batsmen",
    "best batsmen":     "top batsmen",
    "best batsman":     "top batsmen",
    "most runs":        "top batsmen",
    "run scorer":       "top batsmen",
    "highest run":      "top batsmen",
    "all time bat":     "top batsmen",
    "batsmen all":      "top batsmen",
    "batsman":          "top batsmen",
    "batting":          "top batsmen",
    "who scored":       "top batsmen",
    "scored most":      "top batsmen",

    # ── Wickets / bowlers ─────────────────────────────────────────────────────
    "top wicket":       "top wicket",
    "most wicket":      "top wicket",
    "best bowler":      "top wicket",
    "highest wicket":   "top wicket",
    "wicket taker":     "top wicket",
    "wicket-taker":     "top wicket",
    "bowling":          "top wicket",
    "bowler":           "top wicket",
    "took most":        "top wicket",

    # ── Team wins ─────────────────────────────────────────────────────────────
    "team win":         "team win",
    "most win":         "team win",
    "most wins":        "team win",
    "best team":        "team win",
    "win count":        "team win",
    "which team":       "team win",
    "team has most":    "team win",
    "team standing":    "team win",
    "team ranking":     "team win",
    "ipl winner":       "team win",
    "most title":       "team win",
    "championship":     "team win",

    # ── Season trends ─────────────────────────────────────────────────────────
    "runs per season":  "runs per season",
    "season trend":     "runs per season",
    "runs over":        "runs per season",
    "season run":       "runs per season",
    "year wise run":    "runs per season",
    "runs each season": "runs per season",

    # ── Sixes ─────────────────────────────────────────────────────────────────
    "most six":         "six",
    "most sixes":       "six",
    "maximum six":      "six",
    "sixes hit":        "six",
    "six hitter":       "six",
    "hit most six":     "six",

    # ── Fours ─────────────────────────────────────────────────────────────────
    "most four":        "four",
    "most fours":       "four",
    "maximum four":     "four",
    "fours hit":        "four",

    # ── Toss ──────────────────────────────────────────────────────────────────
    "toss impact":      "toss",
    "toss effect":      "toss",
    "toss result":      "toss",
    "toss on result":   "toss",
    "impact of toss":   "toss",
    "toss win":         "toss",
    "toss":             "toss",

    # ── Player of match ───────────────────────────────────────────────────────
    "player of match":  "player of match",
    "man of match":     "player of match",
    "best player":      "player of match",
    "award":            "player of match",
    "most award":       "player of match",
    "most mom":         "player of match",

    # ── Season matches ────────────────────────────────────────────────────────
    "matches per season":  "season",
    "season match":        "season",
    "matches in season":   "season",
    "matches each season": "season",

    # ── Economy ───────────────────────────────────────────────────────────────
    "economy":          "economy",
    "best economy":     "economy",
    "lowest economy":   "economy",
    "economy rate":     "economy",

    # ── Strike rate ───────────────────────────────────────────────────────────
    "strike rate":      "strike rate",
    "highest strike":   "strike rate",
    "best strike":      "strike rate",

    # ── Highest score ─────────────────────────────────────────────────────────
    "highest score":        "highest score",
    "highest team score":   "highest score",
    "biggest score":        "highest score",
    "highest total":        "highest score",
    "highest innings":      "highest score",
}


# ══════════════════════════════════════════════════════════════════════════════
#  FALLBACK QUERIES — all fixed for actual DB data format
# ══════════════════════════════════════════════════════════════════════════════
FALLBACK_QUERIES = {

    # ── BUG FIXED: is_wicket='t', over_number 1-20 ───────────────────────────
    "six_probability_powerplay": {
        "sql": """
            SELECT
                over_number,
                COUNT(*)                                                        AS total_balls,
                COUNT(*) FILTER (WHERE runs_batter = 6)                        AS total_sixes,
                ROUND(100.0 * COUNT(*) FILTER (WHERE runs_batter = 6)
                      / NULLIF(COUNT(*), 0), 2)                                AS six_probability_pct
            FROM deliveries
            WHERE over_number <= 2
            GROUP BY over_number
            ORDER BY over_number
        """,
        "explanation": "Probability of hitting a six in overs 1 and 2. Calculated as (sixes ÷ total balls) × 100 per over.",
        "chart_type": "bar", "chart_x": "over_number", "chart_y": "six_probability_pct",
    },

    "wicket_probability": {
        "sql": """
            SELECT
                over_number,
                COUNT(*)                                              AS total_balls,
                COUNT(*) FILTER (WHERE is_wicket = 't')              AS wickets,
                ROUND(100.0 * COUNT(*) FILTER (WHERE is_wicket = 't')
                      / NULLIF(COUNT(*), 0), 2)                      AS wicket_probability_pct
            FROM deliveries
            WHERE over_number <= 6
            GROUP BY over_number
            ORDER BY over_number
        """,
        "explanation": "Probability of a wicket falling in each powerplay over (1-6).",
        "chart_type": "bar", "chart_x": "over_number", "chart_y": "wicket_probability_pct",
    },

    "win_rate_batting": {
        "sql": """
            SELECT
                i.innings_number,
                CASE WHEN i.innings_number = 1 THEN 'Batting First'
                     ELSE 'Batting Second' END                        AS strategy,
                COUNT(*)                                              AS total_matches,
                COUNT(*) FILTER (WHERE i.batting_team = m.winner)    AS wins,
                ROUND(100.0 * COUNT(*) FILTER (WHERE i.batting_team = m.winner)
                      / NULLIF(COUNT(*), 0), 1)                      AS win_pct
            FROM innings i
            JOIN "Matches" m ON i.match_id = m.match_id
            WHERE m.winner IS NOT NULL
              AND m.result != 'no result'
            GROUP BY i.innings_number
            ORDER BY i.innings_number
        """,
        "explanation": "Win rate for teams batting first vs batting second across all IPL matches.",
        "chart_type": "bar", "chart_x": "strategy", "chart_y": "win_pct",
    },

    "venue_avg_score": {
        "sql": """
            SELECT
                m.match_venue                         AS venue,
                ROUND(AVG(i.total_runs), 1)           AS avg_score,
                COUNT(*)                              AS matches,
                MAX(i.total_runs)                     AS highest_score
            FROM innings i
            JOIN "Matches" m ON i.match_id = m.match_id
            WHERE i.innings_number = 1
            GROUP BY m.match_venue
            HAVING COUNT(*) >= 5
            ORDER BY avg_score DESC
            LIMIT 10
        """,
        "explanation": "IPL venues ranked by average first innings score — minimum 5 matches played.",
        "chart_type": "bar", "chart_x": "venue", "chart_y": "avg_score",
    },

    "death_over_stats": {
        "sql": """
            SELECT
                over_number,
                COUNT(*)                                              AS total_balls,
                SUM(runs_total)                                       AS total_runs,
                COUNT(*) FILTER (WHERE runs_batter = 6)              AS sixes,
                COUNT(*) FILTER (WHERE runs_batter = 4)              AS fours,
                COUNT(*) FILTER (WHERE is_wicket = 't')              AS wickets,
                ROUND(SUM(runs_total) * 6.0 / NULLIF(COUNT(*),0), 2) AS run_rate
            FROM deliveries
            WHERE over_number >= 16
            GROUP BY over_number
            ORDER BY over_number
        """,
        "explanation": "Death overs (16-20) statistics — runs, sixes, fours, wickets and run rate per over.",
        "chart_type": "bar", "chart_x": "over_number", "chart_y": "run_rate",
    },

    "powerplay_stats": {
        "sql": """
            SELECT
                over_number,
                COUNT(*)                                               AS total_balls,
                SUM(runs_total)                                        AS total_runs,
                COUNT(*) FILTER (WHERE runs_batter = 6)               AS sixes,
                COUNT(*) FILTER (WHERE runs_batter = 4)               AS fours,
                COUNT(*) FILTER (WHERE is_wicket = 't')               AS wickets,
                ROUND(SUM(runs_total) * 6.0 / NULLIF(COUNT(*), 0), 2) AS run_rate
            FROM deliveries
            WHERE over_number <= 6
            GROUP BY over_number
            ORDER BY over_number
        """,
        "explanation": "Powerplay (overs 1-6) statistics — runs, sixes, fours, wickets and run rate per over.",
        "chart_type": "bar", "chart_x": "over_number", "chart_y": "run_rate",
    },

    "over_run_rate": {
        "sql": """
            SELECT
                over_number,
                ROUND(SUM(runs_total) * 6.0 / NULLIF(COUNT(*), 0), 2)  AS run_rate,
                COUNT(*) FILTER (WHERE runs_batter = 6)                 AS sixes,
                ROUND(100.0 * COUNT(*) FILTER (WHERE runs_batter = 6)
                      / NULLIF(COUNT(*), 0), 2)                         AS six_pct
            FROM deliveries
            GROUP BY over_number
            ORDER BY over_number
        """,
        "explanation": "Run rate and six-hitting percentage across all 20 overs in IPL history.",
        "chart_type": "line", "chart_x": "over_number", "chart_y": "run_rate",
    },

    "super_over": {
        "sql": """
            SELECT
                COUNT(*)          AS super_over_matches,
                MIN(season)       AS first_season,
                MAX(season)       AS last_season
            FROM "Matches"
            WHERE eliminator IS NOT NULL
              AND eliminator != ''
        """,
        "explanation": "Total number of IPL matches that were decided by a Super Over.",
        "chart_type": "none", "chart_x": "", "chart_y": "",
    },

    "win_after_score": {
        "sql": """
            SELECT
                CASE
                    WHEN i.total_runs >= 200 THEN '200+'
                    WHEN i.total_runs >= 180 THEN '180-199'
                    WHEN i.total_runs >= 160 THEN '160-179'
                    WHEN i.total_runs >= 140 THEN '140-159'
                    ELSE 'Under 140'
                END                                                    AS score_bracket,
                COUNT(*)                                               AS matches,
                COUNT(*) FILTER (WHERE i.batting_team = m.winner)     AS wins,
                ROUND(100.0 * COUNT(*) FILTER (WHERE i.batting_team = m.winner)
                      / NULLIF(COUNT(*), 0), 1)                        AS win_pct
            FROM innings i
            JOIN "Matches" m ON i.match_id = m.match_id
            WHERE i.innings_number = 1
              AND m.winner IS NOT NULL
              AND m.result != 'no result'
            GROUP BY score_bracket
            ORDER BY MIN(i.total_runs) DESC
        """,
        "explanation": "Win percentage for teams batting first based on their total score bracket.",
        "chart_type": "bar", "chart_x": "score_bracket", "chart_y": "win_pct",
    },

    "avg_first_innings": {
        "sql": """
            SELECT
                m.season,
                ROUND(AVG(i.total_runs), 1)   AS avg_first_innings_score,
                MAX(i.total_runs)              AS highest_score,
                MIN(i.total_runs)              AS lowest_score,
                COUNT(*)                       AS matches
            FROM innings i
            JOIN "Matches" m ON i.match_id = m.match_id
            WHERE i.innings_number = 1
            GROUP BY m.season
            ORDER BY m.season
        """,
        "explanation": "Average first innings score per IPL season — shows how totals have grown over the years.",
        "chart_type": "line", "chart_x": "season", "chart_y": "avg_first_innings_score",
    },

    "dot_ball": {
        "sql": """
            SELECT
                p.player_name,
                COUNT(*)                                               AS total_balls,
                COUNT(*) FILTER (WHERE d.runs_total = 0)              AS dot_balls,
                ROUND(100.0 * COUNT(*) FILTER (WHERE d.runs_total = 0)
                      / NULLIF(COUNT(*), 0), 1)                        AS dot_ball_pct
            FROM deliveries d
            JOIN "Players" p ON d.bowler_id = p.player_id
            GROUP BY p.player_name
            HAVING COUNT(*) >= 300
            ORDER BY dot_ball_pct DESC
            LIMIT 10
        """,
        "explanation": "Bowlers with the highest dot ball percentage — minimum 300 balls bowled.",
        "chart_type": "bar", "chart_x": "player_name", "chart_y": "dot_ball_pct",
    },

    # ── BUG FIXED: is_wicket = 't' not TRUE ──────────────────────────────────
    "top batsmen": {
        "sql": """
            SELECT
                p.player_name,
                SUM(d.runs_batter)            AS total_runs,
                COUNT(DISTINCT d.match_id)    AS matches,
                ROUND(SUM(d.runs_batter) * 100.0
                      / NULLIF(COUNT(*), 0), 2) AS strike_rate
            FROM deliveries d
            JOIN "Players" p ON d.batter_id = p.player_id
            GROUP BY p.player_name
            ORDER BY total_runs DESC
            LIMIT 10
        """,
        "explanation": "Top 10 run-scorers in IPL history with strike rate.",
        "chart_type": "bar", "chart_x": "player_name", "chart_y": "total_runs",
    },

    "top wicket": {
        "sql": """
            SELECT
                p.player_name,
                COUNT(*) FILTER (WHERE d.is_wicket = 't'
                    AND d.dismissal_type NOT IN
                    ('run out','retired hurt','obstructing the field')) AS wickets,
                COUNT(DISTINCT d.match_id)                             AS matches
            FROM deliveries d
            JOIN "Players" p ON d.bowler_id = p.player_id
            GROUP BY p.player_name
            ORDER BY wickets DESC
            LIMIT 10
        """,
        "explanation": "Top 10 wicket-takers in IPL history (excludes run-outs).",
        "chart_type": "bar", "chart_x": "player_name", "chart_y": "wickets",
    },

    "team win": {
        "sql": """
            SELECT winner AS team,
                   COUNT(*) AS wins
            FROM "Matches"
            WHERE winner IS NOT NULL
              AND result != 'no result'
            GROUP BY winner
            ORDER BY wins DESC
            LIMIT 10
        """,
        "explanation": "IPL teams ranked by total wins across all seasons.",
        "chart_type": "bar", "chart_x": "team", "chart_y": "wins",
    },

    "runs per season": {
        "sql": """
            SELECT m.season,
                   SUM(d.runs_total)          AS total_runs,
                   COUNT(DISTINCT d.match_id) AS matches
            FROM deliveries d
            JOIN "Matches" m ON d.match_id = m.match_id
            GROUP BY m.season
            ORDER BY m.season
        """,
        "explanation": "Total runs scored in each IPL season showing growth over the years.",
        "chart_type": "line", "chart_x": "season", "chart_y": "total_runs",
    },

    "highest score": {
        "sql": """
            SELECT m.season, i.batting_team,
                   i.total_runs, i.total_wickets, m.match_venue
            FROM innings i
            JOIN "Matches" m ON i.match_id = m.match_id
            ORDER BY i.total_runs DESC
            LIMIT 10
        """,
        "explanation": "Highest team innings totals ever recorded in IPL history.",
        "chart_type": "bar", "chart_x": "batting_team", "chart_y": "total_runs",
    },

    "six": {
        "sql": """
            SELECT p.player_name,
                   COUNT(*) FILTER (WHERE d.runs_batter = 6) AS sixes
            FROM deliveries d
            JOIN "Players" p ON d.batter_id = p.player_id
            GROUP BY p.player_name
            ORDER BY sixes DESC
            LIMIT 10
        """,
        "explanation": "Players with the most sixes hit in IPL history.",
        "chart_type": "bar", "chart_x": "player_name", "chart_y": "sixes",
    },

    "four": {
        "sql": """
            SELECT p.player_name,
                   COUNT(*) FILTER (WHERE d.runs_batter = 4) AS fours
            FROM deliveries d
            JOIN "Players" p ON d.batter_id = p.player_id
            GROUP BY p.player_name
            ORDER BY fours DESC
            LIMIT 10
        """,
        "explanation": "Players with the most fours hit in IPL history.",
        "chart_type": "bar", "chart_x": "player_name", "chart_y": "fours",
    },

    "toss": {
        "sql": """
            SELECT
                toss_decision,
                COUNT(*)                                                     AS times_chosen,
                COUNT(*) FILTER (WHERE toss_winner = winner)                 AS wins_after_toss,
                ROUND(100.0 * COUNT(*) FILTER (WHERE toss_winner = winner)
                      / NULLIF(COUNT(*), 0), 1)                              AS win_pct
            FROM "Matches"
            WHERE result != 'no result'
              AND winner IS NOT NULL
            GROUP BY toss_decision
        """,
        "explanation": "Win percentage after winning the toss — bat vs field decision.",
        "chart_type": "pie", "chart_x": "toss_decision", "chart_y": "wins_after_toss",
    },

    # ── BUG FIXED: player_of_match curly brace cleaned ───────────────────────
    "player of match": {
        "sql": """
            SELECT
                REPLACE(REPLACE(player_of_match, '{"', ''), '"}', '')
                                  AS player,
                COUNT(*)          AS awards
            FROM "Matches"
            WHERE player_of_match IS NOT NULL
            GROUP BY player_of_match
            ORDER BY awards DESC
            LIMIT 10
        """,
        "explanation": "Players with the most Player of the Match awards in IPL history.",
        "chart_type": "bar", "chart_x": "player", "chart_y": "awards",
    },

    "season": {
        "sql": """
            SELECT season, COUNT(*) AS matches
            FROM "Matches"
            GROUP BY season
            ORDER BY season
        """,
        "explanation": "Total matches played in each IPL season from 2008 to 2025.",
        "chart_type": "bar", "chart_x": "season", "chart_y": "matches",
    },

    "economy": {
        "sql": """
            SELECT
                p.player_name,
                ROUND(SUM(d.runs_total) * 6.0 / NULLIF(COUNT(*), 0), 2) AS economy_rate,
                COUNT(DISTINCT d.match_id)                                AS matches
            FROM deliveries d
            JOIN "Players" p ON d.bowler_id = p.player_id
            GROUP BY p.player_name
            HAVING COUNT(DISTINCT d.match_id) >= 10
            ORDER BY economy_rate ASC
            LIMIT 10
        """,
        "explanation": "Bowlers with the best economy rates in IPL — minimum 10 matches.",
        "chart_type": "bar", "chart_x": "player_name", "chart_y": "economy_rate",
    },

    "strike rate": {
        "sql": """
            SELECT
                p.player_name,
                ROUND(SUM(d.runs_batter) * 100.0 / NULLIF(COUNT(*), 0), 2) AS strike_rate,
                SUM(d.runs_batter)                                           AS total_runs
            FROM deliveries d
            JOIN "Players" p ON d.batter_id = p.player_id
            GROUP BY p.player_name
            HAVING SUM(d.runs_batter) >= 500
            ORDER BY strike_rate DESC
            LIMIT 10
        """,
        "explanation": "Batsmen with the highest strike rates — minimum 500 runs scored.",
        "chart_type": "bar", "chart_x": "player_name", "chart_y": "strike_rate",
    },
}


# ══════════════════════════════════════════════════════════════════════════════
#  SMART FALLBACK
# ══════════════════════════════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════════════════════════════
#  DATA LIMITATION HANDLER
#  Detects questions that need data NOT available in the IPL dataset.
#  Instead of showing wrong answer or error — shows friendly message
#  AND suggests the closest available answer.
# ══════════════════════════════════════════════════════════════════════════════

# Each entry:
#   "trigger keywords" → {
#       missing  : what data is missing
#       suggest  : closest available answer key from FALLBACK_QUERIES
#       message  : friendly explanation shown to user
#   }
DATA_LIMITATIONS = [
    {
        "triggers": ["bouncy", "flat pitch", "pitch type", "pitch condition",
                     "hard pitch", "slow pitch", "turning pitch", "spin friendly",
                     "pace friendly", "green pitch", "dry pitch"],
        "missing": "pitch type / pitch condition",
        "suggest": "top wicket",
        "message": (
            "⚠️ Your question asks about **pitch type** (bouncy / flat / turning), "
            "but this information is **not recorded** in the IPL dataset. "
            "The dataset does not have a pitch condition column.\n\n"
            "📊 **Closest available answer:** I can show you the "
            "**top wicket-takers overall**, or wickets by venue "
            "(different venues have different pitch characteristics).\n\n"
            "💡 Try asking: *'Which bowler has most wickets at Wankhede Stadium?'* "
            "or *'Top wicket takers in IPL'*"
        ),
    },
    {
        "triggers": ["salary", "auction price", "contract value", "ipl auction",
                     "how much paid", "earning", "wage", "fee"],
        "missing": "player salary / auction price",
        "suggest": "top batsmen",
        "message": (
            "⚠️ Your question asks about **player salary or auction price**, "
            "but this information is **not available** in the IPL dataset. "
            "The dataset only contains match and ball-by-ball performance data.\n\n"
            "📊 **Closest available answer:** I can show you the "
            "**top run-scorers** or **Player of Match award winners** "
            "which reflect player value through performance.\n\n"
            "💡 Try asking: *'Top 10 batsmen all time'* "
            "or *'Player of match awards'*"
        ),
    },
    {
        "triggers": ["injury", "fitness", "medical", "physio", "rehabilitation",
                     "injured", "health", "recovery", "concussion"],
        "missing": "player injury / fitness records",
        "suggest": None,
        "message": (
            "⚠️ Your question asks about **player injuries or fitness**, "
            "but this information is **not available** in the IPL dataset. "
            "The dataset only contains on-field performance data.\n\n"
            "❌ There is no similar data available to suggest as an alternative.\n\n"
            "💡 Try asking performance questions like: "
            "*'Top 10 batsmen'*, *'Best economy bowlers'*, "
            "or *'Most sixes in IPL'*"
        ),
    },
    {
        "triggers": ["crowd", "attendance", "spectator", "audience",
                     "stadium capacity", "ticket", "viewership"],
        "missing": "crowd attendance / stadium capacity",
        "suggest": "venue_avg_score",
        "message": (
            "⚠️ Your question asks about **crowd attendance**, "
            "but this information is **not recorded** in the IPL dataset.\n\n"
            "📊 **Closest available answer:** I can show you "
            "**average scores per venue**, which shows the most active stadiums.\n\n"
            "💡 Try asking: *'Which venue has the highest average score?'*"
        ),
    },
    {
        "triggers": ["weather", "rain", "dew", "humidity", "temperature",
                     "wind", "cloudy", "overcast", "climate"],
        "missing": "weather conditions",
        "suggest": "toss",
        "message": (
            "⚠️ Your question asks about **weather conditions**, "
            "but weather data is **not recorded** in the IPL dataset.\n\n"
            "📊 **Closest available answer:** I can show you "
            "**toss decisions and win rates**, as teams often choose to "
            "field first due to dew factor in evening matches.\n\n"
            "💡 Try asking: *'Toss impact on results'*"
        ),
    },
    {
        "triggers": ["age", "date of birth", "born", "nationality",
                     "country", "international", "height", "weight"],
        "missing": "player personal details (age, nationality, height)",
        "suggest": "top batsmen",
        "message": (
            "⚠️ Your question asks about **player personal details** "
            "(age / nationality / physical attributes), "
            "but this information is **not in the IPL dataset**. "
            "Only player names and team information are available.\n\n"
            "📊 **Closest available answer:** I can show you "
            "**player performance stats** instead.\n\n"
            "💡 Try asking: *'Top 10 batsmen'* or *'Top wicket takers'*"
        ),
    },
    {
        "triggers": ["social media", "twitter", "instagram", "follower",
                     "fan following", "popular", "celebrity"],
        "missing": "social media / popularity data",
        "suggest": "player of match",
        "message": (
            "⚠️ Your question asks about **social media or popularity**, "
            "but this data is **not available** in the IPL dataset.\n\n"
            "📊 **Closest available answer:** I can show you "
            "**Player of Match award winners** as a measure of on-field popularity.\n\n"
            "💡 Try asking: *'Player of match awards'*"
        ),
    },
    {
        "triggers": ["coach", "captain history", "management", "support staff",
                     "trainer", "analyst", "selector"],
        "missing": "team management / coaching staff data",
        "suggest": "team win",
        "message": (
            "⚠️ Your question asks about **coaching staff or team management**, "
            "but this information is **not recorded** in the IPL dataset.\n\n"
            "📊 **Closest available answer:** I can show you "
            "**team win records** which reflect overall team performance.\n\n"
            "💡 Try asking: *'Which team has most wins?'*"
        ),
    },
    {
        "triggers": ["net run rate", "nrr", "points table", "qualification",
                     "playoff", "standing point"],
        "missing": "points table / net run rate",
        "suggest": "team win",
        "message": (
            "⚠️ Your question asks about the **points table or net run rate**, "
            "but this is **not stored** in the IPL dataset. "
            "Only individual match results are available.\n\n"
            "📊 **Closest available answer:** I can show you "
            "**total wins per team** across all seasons.\n\n"
            "💡 Try asking: *'Which team has most wins?'*"
        ),
    },
    {
        "triggers": ["broadcast", "tv rights", "sponsorship", "revenue",
                     "prize money", "commercial"],
        "missing": "financial / commercial data",
        "suggest": None,
        "message": (
            "⚠️ Your question asks about **IPL finances or commercial data**, "
            "but this information is **not in the dataset**. "
            "The dataset only contains on-field cricket data.\n\n"
            "❌ No similar data is available as an alternative.\n\n"
            "💡 Try asking performance questions like: "
            "*'Top 10 batsmen'*, *'Most sixes in IPL'*"
        ),
    },
]


def _check_data_limitation(question: str) -> dict | None:
    """
    Check if the question asks for data that is NOT in the IPL dataset.
    Returns a limitation response dict if found, else None.
    """
    q = question.lower()
    for limitation in DATA_LIMITATIONS:
        for trigger in limitation["triggers"]:
            if trigger in q:
                # Build response
                suggest_key = limitation.get("suggest")
                suggest_sql = None
                if suggest_key and suggest_key in FALLBACK_QUERIES:
                    suggest_sql = FALLBACK_QUERIES[suggest_key]

                return {
                    "sql":         suggest_sql["sql"] if suggest_sql else "",
                    "explanation": limitation["message"],
                    "chart_type":  suggest_sql["chart_type"] if suggest_sql else "none",
                    "chart_x":     suggest_sql.get("chart_x", "") if suggest_sql else "",
                    "chart_y":     suggest_sql.get("chart_y", "") if suggest_sql else "",
                    "source":      "limitation",
                    "limited":     True,
                }
    return None


# ══════════════════════════════════════════════════════════════════════════════
#  SMART FALLBACK
# ══════════════════════════════════════════════════════════════════════════════
def _fallback(question: str) -> dict:
    q = question.lower().strip()

    # ── Step 1: Greetings → friendly reply ───────────────────────────────────
    greetings = ["hello", "hi", "hey", "how are you", "what's up",
                 "good morning", "good evening", "thanks", "thank you",
                 "bye", "ok", "okay", "test", "testing"]
    if any(g == q or q.startswith(g) for g in greetings):
        return {
            "sql": "",
            "explanation": (
                "👋 Hello! I am IPL NEXUS AI. "
                "Ask me any IPL cricket question! Try: "
                "'Top 10 batsmen', 'Top wicket takers', "
                "'Probability of six in first two overs', "
                "'Win rate batting first', 'Death over stats'."
            ),
            "chart_type": "none", "chart_x": "", "chart_y": "",
            "source": "fallback",
        }

    # ── Step 2: KEYWORD_MAP (longest match wins) ──────────────────────────────
    sorted_kws = sorted(KEYWORD_MAP.keys(), key=len, reverse=True)
    for kw in sorted_kws:
        if kw in q:
            key = KEYWORD_MAP[kw]
            if key in FALLBACK_QUERIES:
                return {**FALLBACK_QUERIES[key], "source": "fallback"}

    # ── Step 3: direct FALLBACK_QUERIES keys ──────────────────────────────────
    for key in FALLBACK_QUERIES:
        if key in q:
            return {**FALLBACK_QUERIES[key], "source": "fallback"}

    # ── Step 4: no match → helpful message ────────────────────────────────────
    return {
        "sql": "",
        "explanation": (
            "❓ I could not find data for that question. "
            "The IPL dataset contains: match results, ball-by-ball deliveries, "
            "player stats, team info, and venue data.\n\n"
            "Try asking:\n"
            "• *Top 10 batsmen all time*\n"
            "• *Top wicket takers*\n"
            "• *Which team has most wins*\n"
            "• *Runs per season trend*\n"
            "• *Probability of six in first two overs*\n"
            "• *Win rate batting first vs second*\n"
            "• *Death over statistics*\n"
            "• *Toss impact on results*\n"
            "• *Player of match awards*\n"
            "• *Best economy bowlers*"
        ),
        "chart_type": "none", "chart_x": "", "chart_y": "",
        "source": "fallback",
    }


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN FUNCTION
# ══════════════════════════════════════════════════════════════════════════════
def generate_sql(question: str) -> dict:
    """
    Full pipeline:
      1. Check DATA_LIMITATIONS  → if question needs missing data, explain + suggest
      2. Try Groq LLM            → generate SQL from question
      3. Fallback                → pre-built templates or helpful message
    """

    # ── Step 1: Check data limitations FIRST ─────────────────────────────────
    limitation = _check_data_limitation(question)
    if limitation:
        return limitation

    # ── Step 2: Try Groq LLM ─────────────────────────────────────────────────
    client = _get_client()

    if client:
        for attempt in range(2):
            try:
                response = client.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user",   "content": question},
                    ],
                    temperature=0.0 if attempt == 0 else 0.1,
                    max_tokens=800,
                    stream=False,
                )

                raw = response.choices[0].message.content.strip()
                raw = re.sub(r"^```(?:json)?\s*", "", raw)
                raw = re.sub(r"\s*```$",           "", raw)

                json_match = re.search(r'\{.*\}', raw, re.DOTALL)
                if json_match:
                    raw = json_match.group(0)

                result           = json.loads(raw)
                result["source"] = "groq"

                sql = result.get("sql", "").strip().upper()
                if not sql or not sql.startswith("SELECT"):
                    continue

                return result

            except json.JSONDecodeError:
                continue
            except Exception:
                break

    # ── Step 3: Smart fallback ────────────────────────────────────────────────
    return _fallback(question)