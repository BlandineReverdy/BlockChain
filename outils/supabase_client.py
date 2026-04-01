import streamlit as st
from supabase import create_client

def get_supabase():
    # Récupération sécurisée depuis ton secrets.toml
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)