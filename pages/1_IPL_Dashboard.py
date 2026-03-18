import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from style import GLOBAL_CSS, sidebar_html, sidebar_nav

st.set_page_config(page_title="IPL NEXUS · Dashboard", page_icon="⚡", layout="wide")
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

with st.sidebar:
    st.markdown(sidebar_html(), unsafe_allow_html=True)
    sidebar_nav()

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="neon-hero" style="border-left-color:var(--cyan);">
    <div class="hero-eyebrow" style="color:var(--cyan);">
        <span style="background:var(--cyan);display:inline-block;width:20px;height:1px;"></span>
        ANALYTICS HUB · POWER BI EMBEDDED
    </div>
    <div class="hero-title">IPL PERFORMANCE <span style="color:var(--cyan);">ANALYTICS</span></div>
    <div class="hero-sub">
        Explore 17 seasons of IPL data through interactive Power BI dashboards.
       Analyze team performance, venue impact, toss influence, scoring trends, and match statistics.
    </div>
</div>
""", unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
for col, (v, l, d) in zip([c1,c2,c3,c4,c5], [
    ("17",    "Editions",     "2008 – 2025"),
    ("1,034", "Matches",      "All formats"),
    ("15",    "Teams",        "Inc. defunct"),
    ("35+",   "Venues",       "Across India"),
    ("5x",    "MI & CSK",     "Most titles"),
]):
    with col:
        st.metric(l, v, d)

st.markdown('<div class="slash-divider"></div>', unsafe_allow_html=True)

# ── Power BI + Highlights tabs ────────────────────────────────────────────────
tab1, tab2 = st.tabs(["  ⚡  POWER BI REPORT  ", "  📋  SEASON HIGHLIGHTS  "])

with tab1:
    st.markdown("""
    <div style="display:flex;align-items:center;justify-content:space-between;
                margin-bottom:1rem;flex-wrap:wrap;gap:.5rem;">
        <div>
            <div class="sec-label" style="margin-bottom:.3rem;">Live Report</div>
            <div style="font-family:'Barlow Condensed',sans-serif;font-size:.82rem;color:var(--muted2);">
                Interactive Power BI dashboard — scroll &amp; filter inside the panel below.
            </div>
        </div>
        <span class="nx-tag tag-c">POWER BI EMBEDDED</span>
    </div>
    """, unsafe_allow_html=True)

    # ── REPLACE THIS URL WITH YOUR POWER BI PUBLISH-TO-WEB LINK ──────────────
    POWERBI_URL = "https://app.powerbi.com/view?r=eyJrIjoiNWU1MGVhZDItNDc3MS00NzNlLWEyZmUtZGEyODY5ZjMxMDFkIiwidCI6IjU2ODFiZGZlLTk3NmMtNGE5Ny05MGU2LWExOGE5YTNjNDlmOCJ9"
    
    # Embed wrapper with neon border
    st.markdown(f"""
    <div style="border:1px solid var(--border-c);border-top:2px solid var(--cyan);
                padding:0;position:relative;background:var(--void2);">
        <iframe
            src="{POWERBI_URL}"
            width="100%"
            height="640"
            frameborder="0"
            allowFullScreen="true"
            style="display:block;">
        </iframe>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top:.8rem;padding:.8rem 1rem;background:rgba(0,240,255,0.04);
                border:1px solid var(--border-c);border-left:2px solid var(--cyan);">
        <div style="font-family:'Barlow Condensed',sans-serif;font-size:.8rem;color:var(--muted2);">
            💡 <b style="color:var(--cyan);">How to embed your report:</b>
            Power BI Service → Open Report → File → Embed Report → Publish to Web →
            copy the iframe <code>src</code> URL → paste as <code>POWERBI_URL</code>
            in <code>pages/1_IPL_Dashboard.py</code>
        </div>
    </div>
    """, unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="sec-label">Season-by-Season Highlights</div>', unsafe_allow_html=True)

    seasons = [
        ("2008", "Rajasthan Royals",        "Shane Warne",   "Sohail Tanvir (22)",  "Shaun Marsh (616)"),
        ("2009", "Deccan Chargers",        "Adam Gilchrist",   "RP Singh (23)",  "Matthew Hayden (572)"),
        ("2010", "Chennai Super Kings",        "MS Dhoni",   "Pragyan Ojha (21)",  "Sachin Tendulkar (618)"),
        ("2011", "Chennai Super Kings",        "MS Dhoni",   "Lasith Malinga (28)",  "Chris Gayle (608)"),
        ("2012", "Kolkata Knight Riders",        "Gautam Gambhir",   "Morne Morkel (25)",  "Chris Gayle (733)"),
        ("2013", "Mumbai Indians",           "Rohit Sharma",  "Dwayne Bravo (32)",   "Michael Hussey (733)"),
        ("2014", "Kolkata Knight Riders",        "Gautam Gambhir",   "Mohit Sharma (23)",  "Robin Uthappa (660)"),
        ("2015", "Mumbai Indians",        "Rohit Sharma",   "Dwayne Bravo (26)",  "David Warner (562)"),
        ("2016", "Sunrisers Hyderabad",      "David Warner",  "Bhuvneshwar Kumar(23)",   "Virat Kohli (973)"),
        ("2017", "Mumbai Indians",        "Rohit Sharma",   "Bhuvneshwar Kumar (26)",  "David Warner (641)"),
        ("2018", "Chennai Super Kings",        "MS Dhoni",   "Andrew Tye (24)",  "Kane Williamson (735)"),
        ("2019", "Mumbai Indians",        "Rohit Sharma",   "Imran Tahir (26)",  "David Warner (692)"),
        ("2020", "Mumbai Indians",           "Rohit Sharma",  "Kagiso Rabada (30)",  "KL Rahul (670)"),
        ("2021", "Chennai Super Kings",        "MS Dhoni",   "Harshal Patel (32)",  "Ruturaj Gaikwad (635)"),
        ("2022", "Gujarat Titans",           "Hardik Pandya", "Yuzvendra Chahal(27)","Jos Buttler (863)"),
        ("2023", "Chennai Super Kings",        "MS Dhoni",   "Mohammed Shami (28)",  "Shubman Gill (890)"),
        ("2024", "Kolkata Knight Riders",    "Shreyas Iyer",  "Harshal Patel (24)",  "Virat Kohli (741)"),
        ("2025", "Royal Challengers Bengaluru",        "Rajat Patidar",   "	Prasidh Krishna (25)",  "	Sai Sudharsan (759)"),
    ]

    for yr, champ, cap, purp, oran in seasons:
        with st.expander(f"🏆  {yr}  ·  {champ}"):
            s1, s2, s3, s4 = st.columns(4)
            s1.metric("Champion", champ)
            s2.metric("Captain", cap)
            s3.metric("Purple Cap", purp)
            s4.metric("Orange Cap", oran)

    st.markdown('<div class="slash-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-label">Titles Tally</div>', unsafe_allow_html=True)

    tally = [
        ("Mumbai Indians",        5, "var(--orange)"),
        ("Chennai Super Kings",   5, "var(--orange)"),
        ("Kolkata Knight Riders", 3, "var(--cyan)"),
        ("Sunrisers Hyderabad",   1, "var(--cyan2)"),
        ("Rajasthan Royals",      1, "var(--cyan2)"),
        ("Deccan Chargers",       1, "var(--cyan2)"),
        ("Gujarat Titans",        1, "var(--cyan2)"),
        ("Royal Challengers Bangalore", 1, "var(--cyan2)"),
    ]
    for name, titles, color in tally:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:1rem;margin-bottom:.85rem;">
            <div style="font-family:'Barlow Condensed',sans-serif;font-size:.85rem;
                        color:var(--text);min-width:200px;">{name}</div>
            <div style="flex:1;height:4px;background:var(--void4);">
                <div style="height:100%;width:{titles/5*100}%;
                            background:{color};
                            box-shadow:0 0 8px {color};
                            transition:width .6s ease;"></div>
            </div>
            <div style="font-family:'Orbitron',sans-serif;font-size:.8rem;
                        font-weight:700;color:{color};min-width:1.5rem;text-align:right;">
                {titles}
            </div>
        </div>
        """, unsafe_allow_html=True)
