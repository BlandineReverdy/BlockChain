import streamlit as st
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from utils.supabase_client import get_supabase
    supabase = get_supabase()
    _db = True
except Exception:
    _db = False

# Connexion à l'interface avec identifiant et mot de passe
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

if not st.session_state.admin_logged_in:
    st.title("🔐 Accès Administration")
    with st.form("login_admin"):
        id_admin = st.text_input("Identifiant")
        pwd_admin = st.text_input("Mot de passe", type="password")
        if st.form_submit_button("Se connecter"):
            if id_admin == "admin" and pwd_admin == "admin01":
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("Identifiants incorrects")
    st.stop()

# Interface admin
st.markdown("""
<div style="margin-bottom:2rem;">
    <div style="color:#ef4444;font-size:0.8rem;font-weight:600;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.4rem;">Espace Admin</div>
    <h1 style="margin:0;font-weight:700;color:#e2e8f0;letter-spacing:-0.03em;">Gestion des Acteurs</h1>
</div>
""", unsafe_allow_html=True)

if st.button("🚪 Déconnexion"):
    st.session_state.admin_logged_in = False
    st.rerun()

tab1, tab2, tab3 = st.tabs(["👥 Liste", "➕ Ajouter", "✏️ Modifier"])

roles_dispo = ["producteur", "transformateur", "controleur", "transporteur"]

# LISTE DES PROFILS
with tab1:
    if _db:
        res = supabase.table("profils").select("*").execute()
        st.dataframe(res.data, width="stretch")

# AJOUTER UN PROFIL
with tab2:
    with st.form("add_actor"):
        nouveau_nom = st.text_input("Nom de l'entité")
        nouveaux_roles = st.multiselect("Rôles", options = roles_dispo, placeholder= "choisir un ou plusieurs rôles")
        nouveau_code = st.text_input("Code de Signature (à créer manuellement)")
        
        if st.form_submit_button("Créer l'acteur"):
            if nouveau_nom and nouveaux_roles and nouveau_code:
                roles_str = ", ".join(nouveaux_roles)
                supabase.table("profils").insert({
                    "nom": nouveau_nom, 
                    "roles": roles_str, 
                    "code_signature": nouveau_code
                }).execute()
                st.success("Acteur créé !")
            else:
                st.warning("Champs manquants")

# MODIFIER UN PROFIL
# Pour chercher un profil, il faut avoir sa signature (sécurité)
with tab3:
    st.markdown("### Rechercher un acteur par sa signature")
    sig_recherche = st.text_input("Entrez la signature de l'acteur à modifier", type="password")
    
    if sig_recherche:
        # On cherche l'acteur dans la base
        res = supabase.table("profils").select("*").eq("code_signature", sig_recherche).execute()
        
        if res.data:
            acteur = res.data[0]
            st.info(f"Modification de : **{acteur['nom_acteur']}**")
            
            with st.form("edit_actor"):
                # On pré-remplit avec les anciennes valeurs
                edit_nom = st.text_input("Nom de l'entité", value=acteur['nom_acteur'])
                
                anciens_roles = [r.strip() for r in acteur['roles'].split(",")] if acteur['roles'] else []
                edit_roles = st.multiselect("Modifier les rôles", roles_dispo, default=anciens_roles)
                
                if st.form_submit_button("Mettre à jour l'acteur"):
                    roles_str = ", ".join(edit_roles)
                    supabase.table("profils").update({
                        "nom_acteur": edit_nom,
                        "roles": roles_str
                    }).eq("code_signature", sig_recherche).execute()
                    st.success("Mise à jour effectuée ! Rafraîchissez la liste.")
        else:
            st.error("Aucun acteur trouvé avec cette signature.")