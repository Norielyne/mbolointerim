from django.contrib import admin
from .models import User, Mission, Candidature, Portefeuille, Transaction, Message

# On personnalise l'affichage pour que ce soit plus lisible
@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display = ('titre', 'auteur', 'prix', 'statut', 'date_creation')
    list_filter = ('statut', 'ville')
    search_fields = ('titre', 'description')

@admin.register(Portefeuille)
class PortefeuilleAdmin(admin.ModelAdmin):
    list_display = ('user', 'solde', 'solde_bloque')
    search_fields = ('user__username',)

@admin.register(Candidature)
class CandidatureAdmin(admin.ModelAdmin):
    list_display = ('mission', 'travailleur', 'accepte', 'date_postulation')
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('expediteur', 'destinataire', 'mission', 'date_envoi', 'lu')
    list_filter = ('lu', 'date_envoi')
    search_fields = ('contenu', 'expediteur__username', 'destinataire__username')

# On enregistre les autres simplement
admin.site.register(User)
admin.site.register(Transaction)
