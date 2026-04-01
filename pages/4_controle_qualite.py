import streamlit as st
import sys, os, datetime
from utils.auth import verifier_signature

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from utils.supabase_client import get_supabase
    supabase = get_supabase()
    _db = True
except Exception:
    _db = False


# En-tête
st.markdown("""
<div style="margin-bottom:2rem;">
    <div style="color:#10b981;font-size:0.8rem;font-weight:600;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.4rem;">Qualité</div>
    <h1 style="margin:0;font-weight:700;color:#e2e8f0;letter-spacing:-0.03em;">Contrôle qualité</h1>
    <p style="margin-top:0.4rem;color:#475569;">Ajoutez un contrôle qualité à un lot existant.</p>
</div>
""", unsafe_allow_html=True)


# 1. ON DÉFINIT LES COLONNES
col_form, col_info = st.columns([3, 2])


# RÉCUPÉRATION DES LOTS
lots = []
if _db:
    try:
        response = supabase.table("lots").select("numero_lot, produit").execute()
        lots_data = response.data

        if lots_data:
            lots = ["-- Choisir un lot --"] + [
                f"{lot['numero_lot']} - {lot['produit']}" for lot in lots_data
            ]
        else:
            lots = ["Aucun lot disponible"]

    except Exception as e:
        st.error(f"Erreur récupération lots : {e}")
        lots = ["Erreur chargement"]
else:
    lots = ["-- Mode démo --", "LOT-TEST - Produit A"]


# Formulaire pour ajouter un contrôle qualité
with col_form:
    with st.form("form_controle_qualite", clear_on_submit=True):
        st.markdown("#### Détails du contrôle")
        lot_selectionne = st.selectbox("Lot :", lots)
        resultat_ctrl = st.selectbox("Résultat", ["Conforme", "Non conforme"])
        commentaire = st.text_area("Commentaires")
        
        st.divider()
        signature = st.text_input("Code de Signature", type="password")
        
        submitted = st.form_submit_button("Valider le contrôle", use_container_width=True)

    # Le traitement reste dans la colonne de gauche pour que les messages s'affichent sous le bouton
    if submitted:
        if lot_selectionne == "-- Choisir un lot --":
            st.warning("Veuillez sélectionner un lot.")
        else:
            est_valide, message = verifier_signature(supabase, signature, "controleur")
            
            if est_valide:
                try:
                    num_lot_pur = lot_selectionne.split(" - ")[0]
                    if _db:
                        supabase.table("controles_qualite").insert({
                            "numero_lot": num_lot_pur,
                            "resultat": resultat_ctrl,
                            "commentaire": commentaire,
                            "acteur": message, 
                            "signature": signature
                        }).execute()
                    st.success(f"✅ Contrôle enregistré par **{message}**")
                except Exception as e:
                    st.error(f"Erreur BDD : {e}")
            else:
                st.error(message)


# Colonne de droite (infos)
with col_info:
    st.markdown("""
    <div class="card">
        <div style="color:#10b981;font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.8rem;">🔍 Processus</div>
        <div style="color:#94a3b8;font-size:0.88rem;line-height:1.7;">
            <b style="color:#e2e8f0;">1.</b> Sélectionnez un lot existant.<br><br>
            <b style="color:#e2e8f0;">2.</b> Indiquez le résultat du contrôle.<br><br>
            <b style="color:#e2e8f0;">3.</b> Ajoutez un commentaire si nécessaire.<br><br>
            <b style="color:#e2e8f0;">4.</b> Validez avec votre signature.
        </div>
    </div>

    <div class="card" style="margin-top:1rem;">
        <div style="color:#f59e0b;font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.8rem;">⚠️ Important</div>
        <div style="color:#94a3b8;font-size:0.85rem;line-height:1.6;">
            Chaque contrôle qualité est enregistré de manière <b style="color:#e2e8f0;">traçable et immuable</b>.
        </div>
    </div>
    """, unsafe_allow_html=True)