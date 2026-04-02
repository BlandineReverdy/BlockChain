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
    <div style="color:#8b5cf6;font-size:0.8rem;font-weight:600;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.4rem;">Transformation</div>
    <h1 style="margin:0;font-weight:700;color:#e2e8f0;letter-spacing:-0.03em;">Ajouter une transformation</h1>
    <p style="margin-top:0.4rem;color:#475569;">Enregistrez une étape de transformation de votre produit.</p>
</div>
""", unsafe_allow_html=True)

# Récupération des lots
lots_options = ["-- Choisir un lot --"]
if _db:
    try:
        response = supabase.table("lots").select("numero_lot, produit").execute()
        for l in response.data:
            lots_options.append(f"{l['numero_lot']} - {l['produit']}")
    except Exception: pass

col_form, col_info = st.columns([3, 2])

with col_form:
    with st.form("form_transformation", clear_on_submit=True):
        st.markdown("#### Détails de l'opération")
        
        lot_source = st.selectbox("Lot à transformer :", lots_options)
        type_transfo = st.text_input("Transformation réalisée", placeholder="Ex: Lavage, Découpe, Cuisson...")
        nom_final = st.text_input("Nouveau nom produit", placeholder="Ex: Purée de tomates")
        quantite_finale = st.text_input("Quantité obtenue", placeholder="Ex : 150 Litres")
        
        st.divider()
        
        signature = st.text_input("Signature (Code personnel)", type="password", help="Votre code de transformateur")
        
        submitted = st.form_submit_button("🏭 Valider la transformation", use_container_width=True)

    if submitted:
        # VERIFICATION DE LA SIGNATURE (Rôle 'transformateur' requis)
        est_valide, resultat = verifier_signature(supabase, signature, "transformateur")

        if not est_valide:
            st.error(resultat)
        elif lot_source == "-- Choisir un lot --" or not all([type_transfo, nom_final, quantite_finale]):
            st.error("Veuillez remplir tous les champs du formulaire.")
        else:
            try:
                nom_acteur = resultat 
                num_lot_source = lot_source.split(" - ")[0]
                nouveau_lot_id = f"TRSF-{datetime.date.today().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
                
                if _db:
                    # ÉTAPE A : Créer le nouveau lot transformé
                    supabase.table("lots").insert({
                        "numero_lot": nouveau_lot_id,
                        "produit": nom_final,
                        "quantite": quantite_finale,
                        "acteur": nom_acteur,
                        "signature": signature,
                        "lot_parent": num_lot_source
                    }).execute()
                    
                    # ÉTAPE B : Enregistrer l'opération dans la table 'transformations'
                    supabase.table("transformations").insert({
                        "numero_lot": num_lot_source,
                        "transformation_realisee": type_transfo,
                        "nom_nouveau_produit": nom_final,
                        "nouveau_numero_lot": nouveau_lot_id,
                        "acteur": nom_acteur,
                        "signature": signature
                    }).execute()
                    
                    st.success(f"✅ Transformation validée par **{nom_acteur}** !")
                    st.info(f"Nouveau lot généré : **{nouveau_lot_id}**")
            
            except Exception as e:
                st.error(f"Erreur lors de l'enregistrement : {e}")

with col_info:
    st.markdown("""
<div style="background-color: #1e293b; padding: 1.5rem; border-radius: 10px; border: 1px solid #334155;">
    <div style="color:#8b5cf6;font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.8rem;">
        💡 Pourquoi transformer ?
    </div>
    <div style="color:#94a3b8;font-size:0.88rem;line-height:1.7;">
        La transformation est une étape clé de la valeur ajoutée.<br><br>
        En signant cette opération, vous engagez la responsabilité de votre entité sur la qualité du nouveau produit.
    </div>
</div>
""", unsafe_allow_html=True)
