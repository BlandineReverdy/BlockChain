import streamlit as st
import sys, os, datetime
import uuid 
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.auth import verifier_signature

try:
    from utils.supabase_client import get_supabase
    supabase = get_supabase()
    _db = True
except Exception:
    _db = False

st.markdown("""
<div style="margin-bottom:2rem;">
    <div style="color:#3b82f6;font-size:0.8rem;font-weight:600;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.4rem;">
        Transfert
    </div>
    <h1 style="margin:0;font-weight:700;color:#e2e8f0;letter-spacing:-0.03em;">Transférer un lot</h1>
    <p style="margin-top:0.4rem;color:#475569;">
        Enregistrez un transfert d'un lot de produit entre deux acteurs.
    </p>
</div>
""", unsafe_allow_html=True)

col_form, col_info = st.columns([3, 2])

with col_form:
    with st.form("form_transfer_lot", clear_on_submit=True):
        st.markdown("#### Informations du transfert")
        
        lots = ["-- Choisir un lot --"]
        if _db:
            try:
                response = supabase.table("lots").select("numero_lot, produit").execute()
                for lot in response.data:
                    lots.append(f"{lot['numero_lot']} - {lot['produit']}")
            except Exception:
                pass
        
        lot_selectionne = st.selectbox("Lot :", lots)
        if lot_selectionne != "-- Choisir un lot --":
            st.success(f"Lot sélectionné : {lot_selectionne}")
        
        depuis = st.text_input("De (acteur source)", placeholder="Ex : Ferme Dupont")
        vers = st.text_input("Vers (acteur destination)", placeholder="Ex : Magasin Bio")
        commentaire = st.text_input("Commentaire / Note")
        signature = st.text_input("Signature", placeholder="Code unique attribué à votre structure", type="password")
        
        submitted = st.form_submit_button("🚚 Transférer le lot", width="stretch")
        
        if submitted:
            if lot_selectionne == "-- Choisir un lot --":
                st.warning("Veuillez sélectionner un lot.")
            else:
                est_valide, message = verifier_signature(supabase, signature, "transporteur")
                
                if est_valide:
                    try:
                        # On récupère juste le numéro du lot (avant le " - ")
                        num_lot_pur = lot_selectionne.split(" - ")[0]
                        
                        supabase.table("transferts").insert({
                            "numero_lot": num_lot_pur,
                            "depuis": depuis,
                            "vers": vers,
                            "commentaire": commentaire, # Ajouté pour être complet
                            "acteur": message,
                            "signature": signature
                        }).execute()
                        
                        st.success(f"✅ Transfert validé par **{message}**")
                    except Exception as e:
                        st.error(f"Erreur lors de l'enregistrement : {e}")
                else:
                    st.error(message)

with col_info:
    st.markdown("""
<div class="card">
    <div style="color:#3b82f6;font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.8rem;">
💡 Comment ça marche
    </div>
    <div style="color:#94a3b8;font-size:0.88rem;line-height:1.7;">
        <b style="color:#e2e8f0;">1.</b> Sélectionnez le lot à transférer.<br><br>
        <b style="color:#e2e8f0;">2.</b> Indiquez l'acteur source et l'acteur destinataire.<br><br>
        <b style="color:#e2e8f0;">3.</b> Ajoutez un commentaire ou note si nécessaire.<br><br>
        <b style="color:#e2e8f0;">4.</b> Entrez votre code acteur pour authentifier le transfert.<br><br>
        <b style="color:#e2e8f0;">5.</b> Cliquez sur 'Transférer' pour enregistrer l'opération.
    </div>
</div>
<div class="card" style="margin-top:1rem;">
    <div style="color:#f59e0b;font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.8rem;">
⚠️ Rappel
    </div>
    <div style="color:#94a3b8;font-size:0.85rem;line-height:1.6;">
        Les transferts enregistrés dans la blockchain sont <b style="color:#e2e8f0;">immuables</b>. Vérifiez bien les informations avant de valider.
    </div>
</div>
""", unsafe_allow_html=True)