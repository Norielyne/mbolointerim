# interim/services.py
import requests

def envoyer_sms_notification(telephone, message):
    """
    Fonction pour envoyer un SMS. 
    Au Gabon, on peut utiliser des passerelles comme Termii ou Twilio.
    """
    # Exemple de structure pour une API de SMS
    print(f"Envoi du SMS à {telephone} : {message}")
    # Logique d'appel API ici
    pass

def notifier_nouveau_candidat(mission):
    message = f"Mbolo ! Un nouveau candidat a postule a votre offre : {mission.titre}."
    envoyer_sms_notification(mission.auteur.phone, message)

def notifier_candidat_accepte(candidature):
    message = f"Felicitations ! Votre candidature pour '{candidature.mission.titre}' a ete acceptee. Connectez-vous pour voir les details."
    envoyer_sms_notification(candidature.travailleur.phone, message)