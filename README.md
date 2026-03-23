# BlockChain
import streamlit as st

# ---- CSS pour un style pro ----
st.markdown("""
    <style>
    /* Boutons sidebar */
    .sidebar .stButton > button {
        width: 220px;
        height: 50px;
        border-radius: 8px;
        background-color: #4A90E2;
        color: white;
        font-weight: bold;
        border: none;
        margin-bottom: 10px;
        transition: 0.3s;
    }
    .sidebar .stButton > button:hover {
        background-color: #357ABD;
    }

    /* Barre de recherche */
    .top-bar {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        gap: 10px;
        padding: 10px 20px;
        background-color: #F5F5F5;
        border-bottom: 1px solid #DDD;
    }
    .search-input {
        height: 35px;
        border-radius: 8px;
        border: 1px solid #CCC;
        padding-left: 10px;
        width: 250px;
        font-size: 14px;
    }
    .search-button {
        height: 35px;
        width: 40px;
        border-radius: 8px;
        background-color: #4A90E2;
        color: white;
        border: none;
        font-size: 16px;
        cursor: pointer;
    }
    .search-button:hover {
        background-color: #357ABD;
    }

    /* Bouton vert créer */
    .stButton > button.create-btn {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        height: 45px;
        width: 150px;
    }
    .stButton > button.create-btn:hover {
        background-color: #45A049;
    }

    /* Zones de texte */
    .stTextInput > div > input {
        border-radius: 6px;
        border: 1px solid #CCC;
        padding: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# ---- Gestion de la "page" via session_state ----
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# ---- Sidebar Menu ----
st.sidebar.title("Que voulez-vous faire ?")
if st.sidebar.button("Créer un lot"):
    st.session_state.page = 'create_lot'
if st.sidebar.button("Ajouter un contrôle qualité"):
    st.session_state.page = 'quality_control'
if st.sidebar.button("Transférer le lot"):
    st.session_state.page = 'transfer_lot'
if st.sidebar.button("Fractionner un lot"):
    st.session_state.page = 'split_lot'
if st.sidebar.button("Assembler des lots"):
    st.session_state.page = 'assemble_lot'

# ---- Top bar avec recherche ----
search_query = st.text_input("Rechercher un lot", "", key="search", placeholder="Rechercher un lot...")
if st.button("🔍 Rechercher"):
    st.write(f"Résultats pour : {search_query}")

# ---- Pages ----
if st.session_state.page == 'home':
    st.write("Bienvenue sur le tableau de bord.")

elif st.session_state.page == 'create_lot':
    st.title("Créer un lot")

    produit = st.text_input("Produit :")
    quantite = st.text_input("Quantité :")
    acteur = st.text_input("Acteur :")
    signature = st.text_input("Signature :")

    if st.button("Créer", key="create_lot_btn", help="Créer le lot", args=None):
        # Ici, tu peux ajouter le code pour enregistrer les infos dans une DB si besoin
        st.success("Lot créé avec succès !")

elif st.session_state.page == 'quality_control':
    st.write("Page de contrôle qualité (en cours de développement).")

elif st.session_state.page == 'transfer_lot':
    st.write("Page de transfert de lot (en cours de développement).")

elif st.session_state.page == 'split_lot':
    st.write("Page de fractionnement de lot (en cours de développement).")

elif st.session_state.page == 'assemble_lot':
    st.write("Page d'assemblage de lots (en cours de développement).")
