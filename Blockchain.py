import streamlit as st

st.set_page_config(
    page_title="ChainTrace | Blockchain Agroalimentaire",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS global ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg-primary:   #07090f;
    --bg-card:      #0d1117;
    --bg-surface:   #111827;
    --bg-elevated:  #1a2235;
    --border:       #1e2d45;
    --border-light: #243352;
    --accent:       #3b82f6;
    --accent-soft:  #1d3a6e;
    --accent-glow:  rgba(59,130,246,0.15);
    --success:      #10b981;
    --warning:      #f59e0b;
    --danger:       #ef4444;
    --text-primary: #e2e8f0;
    --text-secondary:#94a3b8;
    --text-muted:   #475569;
}

* { font-family: 'Space Grotesk', sans-serif !important; }

/* Hide default Streamlit chrome */
#MainMenu, footer { visibility: hidden; }
header {
    background: transparent !important;
    height: 0px !important;
}

header > div {
    display: none !important;
}

[data-testid="stAppViewBlockContainer"] {
    padding-top: 0rem !important;
}
[data-testid="stAppViewBlockContainer"] { padding-top: 1rem; }

/* Page background */
.stApp { background-color: var(--bg-primary); color: var(--text-primary); }

/* ── Sidebar ──────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--bg-card) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text-primary) !important; }

/* Nav links */
[data-testid="stSidebarNavLink"] {
    border-radius: 8px !important;
    margin: 2px 8px !important;
    padding: 10px 16px !important;
    transition: all 0.2s !important;
    color: var(--text-secondary) !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
}
[data-testid="stSidebarNavLink"]:hover {
    background: var(--bg-elevated) !important;
    color: var(--text-primary) !important;
}
[data-testid="stSidebarNavLink"][aria-current="page"] {
    background: var(--accent-soft) !important;
    color: var(--accent) !important;
    border-left: 3px solid var(--accent) !important;
}

/* Cards */
.card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.card:hover { border-color: var(--border-light); }

/* Inputs */
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea,
[data-baseweb="select"] div {
    background: var(--bg-surface) !important;
    border-color: var(--border) !important;
    color: var(--text-primary) !important;
    border-radius: 8px !important;
    font-family: 'Space Grotesk', sans-serif !important;
}
[data-baseweb="input"] input:focus,
[data-baseweb="textarea"] textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-glow) !important;
}

/* Buttons */
[data-testid="stButton"] > button {
    background: var(--accent) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 1.4rem !important;
    transition: all 0.2s !important;
    letter-spacing: 0.02em !important;
}
[data-testid="stButton"] > button:hover {
    background: #2563eb !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 15px rgba(59,130,246,0.3) !important;
}

/* Success/Error messages */
[data-testid="stAlert"] {
    border-radius: 8px !important;
    border: 1px solid !important;
}

/* Labels */
label { color: var(--text-secondary) !important; font-size: 0.85rem !important; font-weight: 500 !important; text-transform: uppercase !important; letter-spacing: 0.05em !important; }

/* Metrics */
[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 1.2rem 1.5rem !important;
}
[data-testid="stMetricValue"] { color: var(--text-primary) !important; font-weight: 700 !important; font-size: 2rem !important; }
[data-testid="stMetricLabel"] { color: var(--text-secondary) !important; font-size: 0.8rem !important; text-transform: uppercase; letter-spacing: 0.08em; }
[data-testid="stMetricDelta"] { font-size: 0.85rem !important; }

/* Divider */
hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }

/* Select boxes */
[data-baseweb="select"] [data-testid="stMarkdownContainer"] p { color: var(--text-primary) !important; }

/* Page titles */
h1 { color: var(--text-primary) !important; font-weight: 700 !important; font-size: 1.8rem !important; letter-spacing: -0.02em !important; }
h2 { color: var(--text-primary) !important; font-weight: 600 !important; font-size: 1.3rem !important; }
h3 { color: var(--text-secondary) !important; font-weight: 500 !important; font-size: 1rem !important; }
p { color: var(--text-secondary) !important; }

/* Dataframe */
[data-testid="stDataFrame"] {
    background: var(--bg-card) !important;
    border-radius: 10px !important;
    border: 1px solid var(--border) !important;
    overflow: hidden !important;
}
</style>
""", unsafe_allow_html=True)

# Sidebar logo
st.sidebar.markdown("""
<div style="padding: 1.5rem 1rem 1rem; border-bottom: 1px solid #1e2d45; margin-bottom: 0.5rem;">
    <div style="display:flex; align-items:center; gap:10px;">
        <div style="width:36px;height:36px;background:linear-gradient(135deg,#3b82f6,#1d4ed8);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px;">🌿</div>
        <div>
            <div style="color:#e2e8f0;font-weight:700;font-size:1.1rem;letter-spacing:-0.02em;">ChainTrace</div>
            <div style="color:#475569;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.08em;">Blockchain Agro</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

pg = st.navigation([
    st.Page("pages/1_accueil.py",          title="Accueil",               icon="🏠"),
    st.Page("pages/2_visualiser_blockchain.py",title="Visualiser la blockchain", icon="🔗"),
    st.Page("pages/3_creer_lot.py",         title="Créer un lot",          icon="📦"),
    st.Page("pages/4_controle_qualite.py",  title="Contrôle qualité",      icon="✅"),
    st.Page("pages/5_transfert.py",         title="Transférer un lot",     icon="🚚"),
    st.Page("pages/6_fractionner.py",       title="Fractionner un lot",    icon="✂️"),
    st.Page("pages/7_assembler.py",         title="Assembler des lots",    icon="🔀"),
    st.Page("pages/8_transformation.py",   title="Ajouter une transformation", icon="🏭"),
])
pg.run()
