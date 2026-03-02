from django.urls import path
from . import views
from .views import ModifierProfilView
from django.contrib.auth import views as auth_views  # <-- C'EST ELLE QUI MANQUE

urlpatterns = [
    path('', views.liste_missions, name='home'),
    path('connexion/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('inscription/', views.inscription_view, name='signup'),
    path('profil/modifier/', views.ModifierProfilView.as_view(), name='modifier_profil'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('mission/creer/', views.creer_mission, name='creer_mission'),
    path('mission/<int:mission_id>/postuler/', views.postuler_mission, name='postuler'),
    path('mission/<int:mission_id>/gestion/', views.gestion_mission, name='gestion_mission'),
    path('candidature/<int:candidature_id>/accepter/', views.accepter_candidat, name='accepter_candidat'),
    path('portefeuille/recharger/', views.recharger_portefeuille, name='recharger'),
    path('mission/<int:mission_id>/valider/', views.valider_mission, name='valider_mission'),
    path('profil/<int:user_id>/', views.profil_public, name='profil_public'),
    path('profil/modifier/', ModifierProfilView.as_view(), name='modifier_profil'),
    path('mission/<int:mission_id>/supprimer/', views.supprimer_mission, name='supprimer_mission'),
    path('candidature/<int:candidature_id>/annuler/', views.annuler_candidature, name='annuler_candidature'),
    path('profil/supprimer-compte/', views.supprimer_compte, name='supprimer_compte'),
    path('soumettre-verification/', views.soumettre_verification, name='soumettre_verification'),
    path('activer-premium/', views.activer_premium, name='activer_premium'),
    path('mission/<int:mission_id>/booster/', views.booster_mission, name='booster_mission'),
    path('mission/<int:pk>/', views.mission_detail_view, name='detail_mission'), # Vérifie bien le 'name'
    path('', views.liste_missions, name='liste_missions'), # <-- Assure-toi que le name est identique
    path('mission/<int:mission_id>/postuler/', views.postuler_mission, name='postuler_mission'),
    path('mission/<int:mission_id>/chat/<int:user_id>/', views.chat_mission, name='chat_mission'),
    path('mission/<int:mission_id>/laisser-avis/<int:user_id>/', views.laisser_avis, name='laisser_avis'),
    path('aide/', views.page_aide, name='aide'),
    path('conditions-generales/', views.page_cgu, name='cgu'),
    path('chats/', views.liste_chats, name='liste_chats'),
    
    # 1. Page pour demander la réinitialisation
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset.html'), name='password_reset'),
    
    # 2. Confirmation que l'email est envoyé
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    
    # 3. Le lien secret reçu par email
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    
    # 4. Message de succès final
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    
]