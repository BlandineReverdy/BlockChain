import streamlit as st
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from outils.supabase_client import get_supabase
    supabase = get_supabase()
    _db = True
except Exception:
    _db = False

# Tête de page 
st.markdown("""
<div style="margin-bottom:2rem;">
    <div style="color:#3b82f6;font-size:0.8rem;font-weight:600;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.4rem;">Tableau de bord</div>
    <h1 style="margin:0;font-size:2rem;font-weight:700;color:#e2e8f0;letter-spacing:-0.03em;">Vue d'ensemble</h1>
    <p style="margin-top:0.4rem;color:#475569;">Bienvenue sur ChainTrace — la traçabilité agroalimentaire sécurisée par blockchain.</p>
</div>
""", unsafe_allow_html=True)

#Indicateurs 
lots_total, controles, transferts, transformations = 0, 0, 0, 0

if _db:
    try:
        lots_total      = supabase.table("lots").select("id", count="exact").execute().count or 0
        controles       = supabase.table("controles_qualite").select("id", count="exact").execute().count or 0
        transferts      = supabase.table("transferts").select("id", count="exact").execute().count or 0
        transformations = supabase.table("transformations").select("id", count="exact").execute().count or 0
    except Exception:
        pass

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("📦 Lots créés",        lots_total)
with c2:
    st.metric("✅ Contrôles qualité", controles)
with c3:
    st.metric("🚚 Transferts",        transferts)
with c4:
    st.metric("🏭 Transformations",   transformations)

st.markdown("---")

#Derniers événements
st.markdown("### 📋 Derniers événements")

if _db:
    try:
        rows = supabase.table("lots").select("*").order("created_at", desc=True).limit(8).execute().data
        if rows:
            import pandas as pd
            df = pd.DataFrame(rows)[["numero_lot", "produit", "quantite", "acteur", "created_at"]]
            df.columns = ["N° Lot", "Produit", "Quantité", "Acteur", "Date de création"]
            st.dataframe(df, width="stretch", hide_index=True)
        else:
            st.info("Aucun lot enregistré pour l'instant.")
    except Exception as e:
        st.info(f"Connectez Supabase pour voir les données. ({e})")
else:
    st.markdown("""
    <div style="background:#0d1117;border:1px dashed #1e2d45;border-radius:12px;padding:2rem;text-align:center;">
        <div style="font-size:2rem;margin-bottom:0.8rem;">🔌</div>
        <div style="color:#94a3b8;font-size:0.95rem;margin-bottom:0.4rem;font-weight:600;">Base de données non connectée</div>
        <div style="color:#475569;font-size:0.85rem;">Configurez vos identifiants Supabase dans <code style="background:#1a2235;padding:2px 6px;border-radius:4px;color:#3b82f6;">.streamlit/secrets.toml</code></div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

#Actions rapides
st.markdown("### ⚡ Actions rapides")
cols = st.columns(3)
actions = [
    ("📦", "Créer un lot",              "Enregistrer un nouveau lot produit"),
    ("✅", "Contrôle qualité",           "Ajouter un résultat de contrôle"),
    ("🚚", "Transférer un lot",          "Déplacer un lot vers un acteur"),
    ("✂️", "Fractionner un lot",         "Diviser un lot en sous-lots"),
    ("🔀", "Assembler des lots",         "Fusionner plusieurs lots"),
    ("🏭", "Ajouter une transformation", "Transformer un produit"),
]
for i, (ico, titre, desc) in enumerate(actions):
    with cols[i % 3]:
        st.markdown(f"""
        <div class="card" style="cursor:pointer;min-height:90px;">
            <div style="font-size:1.5rem;margin-bottom:0.4rem;">{ico}</div>
            <div style="color:#e2e8f0;font-weight:600;font-size:0.95rem;">{titre}</div>
            <div style="color:#475569;font-size:0.8rem;margin-top:0.2rem;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
