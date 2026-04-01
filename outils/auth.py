# utils/auth.py
import streamlit as st

def verifier_signature(supabase, code_signature, role_requis=None):
    """
    Vérifie la signature et les droits de l'acteur.
    Retourne (True, nom_acteur) si OK, (False, message_erreur) sinon.
    """
    if not code_signature:
        return False, "La signature est obligatoire."
    
    try:
        # Recherche du profil par son code de signature
        res = supabase.table("profils").select("*").eq("code_signature", code_signature).execute()
        
        if not res.data:
            return False, "Signature invalide."
        
        profil = res.data[0]
        nom = profil['nom_acteur']
        roles_utilisateur = [r.strip() for r in profil['roles'].split(',')]

        # Si un rôle spécifique est requis (ex: producteur)
        if role_requis and role_requis not in roles_utilisateur:
            return False, f"Action refusée : {nom} n'a pas le rôle '{role_requis}'."
        
        return True, nom
    except Exception as e:
        return False, f"Erreur lors de la vérification : {str(e)}"