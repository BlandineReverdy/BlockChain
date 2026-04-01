import streamlit as st
import pandas as pd
import sys, os, uuid, datetime
from utils.auth import verifier_signature

# Configuration du chemin pour l'import de Supabase
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from utils.supabase_client import get_supabase
    supabase = get_supabase()
    _db = True
except Exception as e:
    _db = False
    st.sidebar.error(f"Erreur de connexion : {e}")

# --- 1. EN-TÊTE ---
st.markdown("""
<div style="margin-bottom:2rem;">
    <div style="color:#3b82f6;font-size:0.8rem;font-weight:600;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.4rem;">Nouveau</div>
    <h1 style="margin:0;font-weight:700;color:#e2e8f0;letter-spacing:-0.03em;">Créer un lot</h1>
    <p style="margin-top:0.4rem;color:#475569;">Enregistrez un nouveau lot de produit dans la blockchain.</p>
</div>
""", unsafe_allow_html=True)

col_form, col_info = st.columns([3, 2])

# --- 2. FORMULAIRE DE CRÉATION ---
with col_form:
    with st.form("form_creer_lot", clear_on_submit=True):
        st.markdown("#### Informations du lot")
        produit   = st.text_input("Nom du produit",   placeholder="Ex : Tomates cerises bio")
        quantite  = st.text_input("Quantité",         placeholder="Ex : 100 kg")
        signature = st.text_input("Code de Signature", type="password", help="Votre code personnel")

        submitted = st.form_submit_button("📦 Créer le lot", use_container_width=True)

    if submitted:
        # 1. Vérification de la signature et du rôle 'producteur'
        est_valide, resultat = verifier_signature(supabase, signature, "producteur")
        
        if not est_valide:
            st.error(resultat)
        elif not produit or not quantite:
            st.warning("Veuillez remplir tous les champs.")
        else:
            # 2. Si la signature est valide, le nom de l'acteur s'affiche 
            nom_acteur = resultat
            try:
                nouveau_lot_id = f"LOT-{datetime.datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"
                supabase.table("lots").insert({
                    "numero_lot": nouveau_lot_id,
                    "produit": produit,
                    "quantite": quantite,
                    "acteur": nom_acteur,
                    "signature": signature
                }).execute()
                st.success(f"✅ Lot créé par {nom_acteur} !")
            except Exception as e:
                st.error(f"Erreur : {e}")

with col_info:
    st.markdown("""
    <div style="background-color: #1e293b; padding: 1.5rem; border-radius: 10px; border: 1px solid #334155;">
        <div style="color:#3b82f6;font-size:0.75rem;font-weight:700;text-transform:uppercase;margin-bottom:0.8rem;">💡 Aide</div>
        <div style="color:#94a3b8;font-size:0.88rem;line-height:1.7;">
            Le numéro de lot généré est unique. Il sera utilisé pour tracer le produit à chaque étape.
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 3. visualiser les 7 derniers lots
st.write("---")
st.subheader("📋 Derniers enregistrements")

if _db:
    try:
        # Récupération des données depuis Supabase
        res = supabase.table("lots").select("created_at, numero_lot, produit, acteur").order("created_at", desc=True).limit(7).execute()
        
        if res.data:
            # On transforme les données en tableau simple
            df = pd.DataFrame(res.data)
            
            # --- ASTUCE POUR COMMENCER À 1 ---
            df.index = df.index + 1 
            
            # On rend la date plus lisible
            df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%d/%m')
            
            # On renomme les colonnes
            df.columns = ['Date', 'Numéro de Lot', 'Produit', 'Acteur']
            
            # Affichage (On garde l'index cette fois car il commence à 1)
            st.table(df)
            
        else:
            st.info("Aucun lot trouvé.")
    except Exception as e:
        st.error(f"Erreur de chargement : {e}")