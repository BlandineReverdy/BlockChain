import streamlit as st
import sys, os, uuid, datetime
from utils.auth import verifier_signature

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from utils.supabase_client import get_supabase
    supabase = get_supabase()
    _db = True
except Exception:
    _db = False

st.markdown("""
<div style="margin-bottom:2rem;">
    <div style="color:#10b981;font-size:0.8rem;font-weight:600;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.4rem;">Assembler</div>
    <h1 style="margin:0;font-weight:700;color:#e2e8f0;letter-spacing:-0.03em;">Assembler des lots</h1>
    <p style="margin-top:0.4rem;color:#475569;">Fusionnez plusieurs lots existants pour créer un nouveau lot unique.</p>
</div>
""", unsafe_allow_html=True)

lots_options = ["-- Choisir un lot --"]
if _db:
    try:
        response = supabase.table("lots").select("numero_lot, produit").execute()
        for l in response.data:
            lots_options.append(f"{l['numero_lot']} - {l['produit']}")
    except Exception: pass

col_form, col_info = st.columns([3, 2])

with col_form:
    with st.form("form_assemble_lot", clear_on_submit=True):
        st.markdown("#### Sélection des composants")
        l1 = st.selectbox("Lot source 1 :", lots_options, key="as_l1")
        l2 = st.selectbox("Lot source 2 :", lots_options, key="as_l2")
        l3 = st.selectbox("Lot source 3 (Optionnel) :", lots_options, key="as_l3")
        
        st.divider()
        st.markdown("#### Nouveau lot généré")
        nom_nouveau_produit = st.text_input("Nom du produit final", placeholder="Ex: Mélange de Tomates Bio")
        nouvelle_quantite = st.text_input("Quantité totale obtenue", placeholder="Ex: 500 kg")
        
        signature = st.text_input("Signature", type="password", help="Votre code unique")
        submitted = st.form_submit_button("🔀 Créer l'assemblage", use_container_width=True)

    if submitted:
        sources = [l for l in [l1, l2, l3] if l != "-- Choisir un lot --"]
        est_valide, resultat = verifier_signature(supabase, signature, None)

        if not est_valide:
            st.error(resultat)
        elif len(sources) < 2 or not all([nom_nouveau_produit, nouvelle_quantite]):
            st.error("Veuillez sélectionner au moins 2 lots sources et remplir les informations du produit.")
        else:
            try:
                nom_acteur = resultat 
                ids_sources_purs = [s.split(" - ")[0] for s in sources]
                string_sources = ", ".join(ids_sources_purs)
                nouveau_lot_id = f"LOT-ASS-{datetime.date.today().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"

                if _db:
                    supabase.table("lots").insert({
                        "numero_lot": nouveau_lot_id,
                        "produit": nom_nouveau_produit,
                        "quantite": nouvelle_quantite,
                        "acteur": nom_acteur,
                        "signature": signature,
                        "lot_parent": string_sources
                    }).execute()
                    
                    supabase.table("assemblages").insert({
                        "lots_sources": string_sources,
                        "nouveau_lot": nouveau_lot_id,
                        "nouvelle_qte": nouvelle_quantite,
                        "acteur": nom_acteur,
                        "signature": signature
                    }).execute()
                    
                    st.success(f"✅ Assemblage réussi par **{nom_acteur}** !")
            except Exception as e:
                st.error(f"Erreur : {e}")
                
with col_info:
    display_name = nom_acteur if ('nom_acteur' in locals()) else "l'opérateur"
    st.markdown(f"""
<div style="background-color: #1e293b; padding: 1.5rem; border-radius: 10px; border: 1px solid #334155;">
    <div style="color:#10b981;font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.8rem;">💡 Principe d'assemblage</div>
    <div style="color:#94a3b8;font-size:0.88rem;line-height:1.7;">
        L'assemblage combine plusieurs sources. L'acteur <b>{display_name}</b> sera garant de la conformité du mélange.<br><br>
        Le nouveau lot est lié aux {len(sources) if ('sources' in locals()) else "lots"} parents.
    </div>
</div>
""", unsafe_allow_html=True)