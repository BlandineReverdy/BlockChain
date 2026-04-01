import streamlit as st
import pandas as pd
from utils.supabase_client import get_supabase

# Configuration de la page (si pas déjà fait dans votre main)
supabase = get_supabase()

# --- 1. LOGIQUE DE DONNÉES ---

def get_lineage(lot_number, lineage=None):
    if lineage is None: lineage = []
    if lot_number not in lineage: lineage.append(lot_number)
    
    res = supabase.table("lots").select("lot_parent").eq("numero_lot", lot_number).execute()
    if res.data and res.data[0]['lot_parent']:
        parents = [p.strip() for p in str(res.data[0]['lot_parent']).split(',') if p.strip()]
        for p in parents:
            if p not in lineage:
                get_lineage(p, lineage)
    return lineage

def get_full_chain(target_lot):
    all_related_lots = get_lineage(target_lot)
    history = []

    for lot_id in all_related_lots:
        # --- A. ORIGINE (Table 'lots') ---
        res_l = supabase.table("lots").select("*").eq("numero_lot", lot_id).execute()
        for l in res_l.data:
            p_val = str(l.get('lot_parent', '')).strip()
            if not p_val or p_val.lower() in ['aucun', 'none', '']:
                history.append({
                    "date": l['created_at'], "type": "ORIGINE", "icon": "🌱",
                    "details": f"Matière première : **{l['produit']}**",
                    "acteur": l.get('acteur', 'Producteur'), "lot_id": lot_id
                })

        # --- B. QUALITÉ (Table 'controles_qualite') ---
        res_q = supabase.table("controles_qualite").select("*").eq("numero_lot", lot_id).execute()
        for q in res_q.data:
            history.append({
                "date": q['created_at'], "type": "QUALITÉ", "icon": "✅",
                "details": f"Contrôle : **{q['resultat']}**",
                "acteur": q.get('acteur', 'Qualité'), "lot_id": lot_id
            })

        # --- C. TRANSFERT (Table 'transferts') ---
        res_t = supabase.table("transferts").select("*").eq("numero_lot", lot_id).execute()
        for t in res_t.data:
            history.append({
                "date": t['created_at'], "type": "TRANSFERT", "icon": "🚚",
                "details": f"Expédié de **{t.get('depuis')}** vers **{t.get('vers')}**",
                "acteur": t.get('acteur', 'Logistique'), "lot_id": lot_id
            })

        # --- D. TRANSFORMATION (Table 'transformations') ---
        res_tr = supabase.table("transformations").select("*").eq("numero_lot", lot_id).execute()
        for tr in res_tr.data:
            history.append({
                "date": tr['created_at'], "type": "TRANSFORMATION", "icon": "🏭",
                "details": f"Action : {tr.get('transformation_realisee')} ➔ Nouveau produit : **{tr.get('nom_nouveau_produit')}** (Lot : `{tr.get('nouveau_numero_lot')}`)",
                "acteur": tr.get('acteur', 'Atelier'), "lot_id": lot_id
            })

        # --- E. ASSEMBLAGE (Table 'assemblages') ---
        res_as = supabase.table("assemblages").select("*").eq("nouveau_lot", lot_id).execute()
        for a in res_as.data:
            history.append({
                "date": a['created_at'], "type": "ASSEMBLAGE", "icon": "🔀",
                "details": f"Mélange des lots : `{a.get('lots_sources')}` pour créer le lot `{lot_id}`",
                "acteur": a.get('acteur', 'Production'), "lot_id": lot_id
            })

        # --- F. FRACTIONNEMENT (DÉPART UNIQUEMENT) ---
        # On ne garde que le cas où le lot actuel est le lot SOURCE qui a été divisé
        res_fs = supabase.table("fractionnements").select("*").eq("numero_lot", lot_id).execute()
        for fs in res_fs.data:
            history.append({
                "date": fs['created_at'], "type": "FRACTIONNEMENT", "icon": "✂️",
                "details": f"Ce lot a été fractionné pour créer les lots : `{fs.get('nouveaux_lots')}`",
                "acteur": fs.get('acteur', 'Logistique'), "lot_id": lot_id
            })

    # Tri par date
    history.sort(key=lambda x: x['date'])
    return history

# --- 2. INTERFACE DE RECHERCHE ---

st.title("🔍 Visualiser la Blockchain")

# Utilisation de colonnes pour la recherche (Python pur)
with st.form("search_form"):
    col_search1, col_search2 = st.columns(2)
    s_lot = col_search1.text_input("🔢 NUMÉRO DE LOT EXACT")
    s_name = col_search2.text_input("🍎 NOM DU PRODUIT")
    submit = st.form_submit_button("RECHERCHER")

if submit:
    if s_lot:
        st.session_state.target_lot = s_lot
        st.session_state.search_results = None
    elif s_name:
        res = supabase.table("lots").select("*").ilike("produit", f"%{s_name}%").execute()
        st.session_state.search_results = res.data
        st.session_state.target_lot = None

# Affichage des résultats de recherche par nom
if st.session_state.get('search_results') and not st.session_state.get('target_lot'):
    st.write("### Lots correspondants :")
    for r in st.session_state.search_results:
        c_t, c_b = st.columns([4, 1])
        c_t.write(f"**{r['numero_lot']}** — {r['produit']}")
        if c_b.button("Voir", key=f"btn_{r['numero_lot']}"):
            st.session_state.target_lot = r['numero_lot']
            st.rerun()

# --- 3. AFFICHAGE DE LA CHAINE ---

if st.session_state.get('target_lot'):
    st.divider()
    chain = get_full_chain(st.session_state.target_lot)
    
    if not chain:
        st.warning("Aucun historique trouvé pour ce lot.")
    else:
        st.subheader(f"Historique : {st.session_state.target_lot}")
        
        for i, step in enumerate(chain):
            # Le paramètre border=True crée le cadre automatiquement
            with st.container(border=True):
                c1, c2 = st.columns([1, 5])
                c1.title(step['icon'])
                with c2:
                    st.write(f"**{step['type']}** | Lot : `{step['lot_id']}`")
                    st.write(step['details'])
                    date_f = pd.to_datetime(step['date']).strftime('%d/%m/%Y')
                    st.caption(f"📅 {date_f} | 👤 {step['acteur']}")

            # Séparateur simple entre les blocs
            if i < len(chain) - 1:
                st.write("  \n  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ▼")

    if st.button("Fermer l'historique"):
        st.session_state.target_lot = None
        st.rerun()