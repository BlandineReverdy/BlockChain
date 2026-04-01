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
    <div style="color:#f59e0b;font-size:0.8rem;font-weight:600;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.4rem;">Fractionner</div>
    <h1 style="margin:0;font-weight:700;color:#e2e8f0;letter-spacing:-0.03em;">Fractionner un lot</h1>
    <p style="margin-top:0.4rem;color:#475569;">Divisez un lot existant en plusieurs nouveaux sous-lots.</p>
</div>
""", unsafe_allow_html=True)

col_form, col_info = st.columns([3, 2])

with col_form:
    with st.form("form_fractionner_lot", clear_on_submit=True):
        st.markdown("#### Configuration du fractionnement")
        lots_options = ["-- Choisir un lot --"]
        if _db:
            try:
                response = supabase.table("lots").select("numero_lot, produit").execute()
                for l in response.data:
                    lots_options.append(f"{l['numero_lot']} - {l['produit']}")
            except Exception: pass
        
        lot_selectionne = st.selectbox("Lot à fractionner :", lots_options)
        
        st.divider()
        st.write("Répartition des quantités :")
        c1, c2 = st.columns(2)
        with c1:
            q1 = st.text_input("Quantité Lot 1", placeholder="Ex: 25kg")
            q3 = st.text_input("Quantité Lot 3", placeholder="Ex: 25kg (optionnel)")
        with c2:
            q2 = st.text_input("Quantité Lot 2", placeholder="Ex: 25kg")
            q4 = st.text_input("Quantité Lot 4", placeholder="Ex: 25kg (optionnel)")
        
        st.divider()
        signature = st.text_input("Signature", placeholder="Votre code unique", type="password")
        submitted = st.form_submit_button("✂️ Fractionner le lot", use_container_width=True)

    if submitted:
        quantities = [q for q in [q1, q2, q3, q4] if q.strip() != ""]
        est_valide, resultat = verifier_signature(supabase, signature, None)

        if not est_valide:
            st.error(resultat)
        elif lot_selectionne == "-- Choisir un lot --" or len(quantities) < 2:
            st.error("Veuillez sélectionner un lot et remplir au moins 2 quantités.")
        else:
            try:
                nom_acteur = resultat 
                num_lot_source = lot_selectionne.split(" - ")[0]
                nom_produit = lot_selectionne.split(" - ")[1] if "-" in lot_selectionne else "Produit"
                nouveaux_ids = []
                
                if _db:
                    for qty in quantities:
                        nouveaux_id = f"LOT-{datetime.date.today().strftime('%Y%m%d')}-SPLIT-{str(uuid.uuid4())[:4].upper()}"
                        nouveaux_ids.append(nouveaux_id)
                        supabase.table("lots").insert({
                            "numero_lot": nouveaux_id,
                            "produit": nom_produit,
                            "quantite": qty,
                            "acteur": nom_acteur,
                            "signature": signature,
                            "lot_parent": num_lot_source
                        }).execute()
                
                    supabase.table("fractionnements").insert({
                        "numero_lot": num_lot_source,
                        "nouveaux_lots": ", ".join(nouveaux_ids),
                        "quantites": ", ".join(quantities),
                        "acteur": nom_acteur,
                        "signature": signature
                    }).execute()
                
                    st.success(f"✅ Fractionnement réussi par **{nom_acteur}** !")
            except Exception as e:
                st.error(f"Erreur : {e}")

with col_info:
    display_name = nom_acteur if ('nom_acteur' in locals()) else "l'opérateur"
    st.markdown(f"""
<div style="background-color: #1e293b; padding: 1.5rem; border-radius: 10px; border: 1px solid #334155;">
    <div style="color:#f59e0b;font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.8rem;">💡 Aide au fractionnement</div>
    <div style="color:#94a3b8;font-size:0.88rem;line-height:1.7;">
        Cette division est signée par <b>{display_name}</b>.<br><br>
        Chaque sous-lot créé hérite de la traçabilité du lot parent <b>{lot_selectionne.split(' - ')[0] if lot_selectionne != '-- Choisir un lot --' else ''}</b>.
    </div>
</div>
""", unsafe_allow_html=True)