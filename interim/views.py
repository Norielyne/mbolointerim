from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.views.generic import UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, authenticate, logout
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q, Avg
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt

# Tes modèles
from .models import User, Mission, Candidature, Portefeuille, Transaction, Message, Avis
# Tes formulaires
from .forms import InscriptionForm, MissionForm, VerificationForm

# --- CONSTANTES ---
EMAIL_ADMIN_PLATEFORME = 'norielyneheilles@gmail.com' # À adapter selon ton admin réel

# --- UTILITAIRES DE NOTIFICATION (CONSOLE) ---
def notifier_nouveau_candidat(mission):
    print(f"--- NOTIFICATION ---")
    print(f"Destinataire: {mission.auteur.email}")
    print(f"Message: Quelqu'un a postulé pour '{mission.titre}' !")

def notifier_candidat_accepte(candidature):
    print(f"--- NOTIFICATION ---")
    print(f"Destinataire: {candidature.travailleur.email}")
    print(f"Message: Félicitations {candidature.travailleur.first_name}, retenu pour '{candidature.mission.titre}' !")

# --- VUES D'INSCRIPTION ET PROFIL ---

@csrf_exempt
def inscription_view(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Connexion auto
            messages.success(request, f"Bienvenue {user.first_name} ! Ton compte Mbolo est prêt.")
            return redirect('dashboard')
    else:
        form = InscriptionForm()
    return render(request, 'registration/signup.html', {'form': form})

class ModifierProfilView(LoginRequiredMixin, UpdateView):
    model = User
    fields = [
        'first_name', 'last_name', 'photo', 'bio', 'cv', 
        'competences', 'ville', 'phone', 'nom_entreprise', 'niu'
    ]
    template_name = 'interim/modifier_profil.html'
    success_url = reverse_lazy('dashboard') 

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Profil mis à jour avec succès !")
        return super().form_valid(form)

def profil_public(request, user_id):
    travailleur = get_object_or_404(User, id=user_id)
    avis_recus = travailleur.avis_recus.all().order_by('-date_creation')
    return render(request, 'interim/profil_public.html', {
        'travailleur': travailleur,
        'avis_recus': avis_recus,
        'moyenne': travailleur.note_moyenne
    })

# --- GESTION DES MISSIONS ---

@login_required
def creer_mission(request):
    if request.method == 'POST':
        form = MissionForm(request.POST)
        if form.is_valid():
            mission = form.save(commit=False)
            mission.auteur = request.user
            mission.save()
            messages.success(request, "Mission publiée avec succès !")
            return redirect('dashboard')
    else:
        form = MissionForm()
    return render(request, 'interim/creer_mission.html', {'form': form})

def liste_missions(request):
    missions = Mission.objects.filter(statut='OUVERT').order_by('-is_boosted', '-date_creation')
    
    ville_filter = request.GET.get('ville')
    cat_filter = request.GET.get('categorie')

    if ville_filter:
        missions = missions.filter(ville=ville_filter)
    if cat_filter:
        missions = missions.filter(categorie=cat_filter)

    # Nettoyage des boosts expirés
    Mission.objects.filter(is_boosted=True, boost_expires_at__lt=timezone.now()).update(is_boosted=False)

    return render(request, 'interim/liste_missions.html', {'missions': missions})

def mission_detail_view(request, pk):
    mission = get_object_or_404(Mission, pk=pk)
    return render(request, 'interim/detail_mission.html', {'mission': mission})

@login_required
def supprimer_mission(request, mission_id):
    mission = get_object_or_404(Mission, id=mission_id, auteur=request.user)
    if request.method == 'POST':
        mission.delete()
        messages.success(request, "L'annonce a été supprimée.")
    return redirect('dashboard')

# --- SYSTÈME DE CANDIDATURE ET PAIEMENT SÉCURISÉ ---

@login_required
def postuler_mission(request, mission_id):
    mission = get_object_or_404(Mission, id=mission_id)
    if mission.auteur == request.user:
        messages.error(request, "Impossible de postuler à votre propre offre.")
        return redirect('home')

    candidature, created = Candidature.objects.get_or_create(
        mission=mission, travailleur=request.user
    )
    if created:
        notifier_nouveau_candidat(mission)
        messages.success(request, "Candidature envoyée !")
    else:
        messages.warning(request, "Vous avez déjà postulé.")
    return redirect('home')

@login_required
def accepter_candidat(request, candidature_id):
    candidature = get_object_or_404(Candidature, id=candidature_id, mission__auteur=request.user)
    mission = candidature.mission
    
    if mission.est_complete:
        messages.error(request, "Nombre maximum de travailleurs atteint.")
        return redirect('gestion_mission', mission_id=mission.id)

    with transaction.atomic():
        portefeuille = request.user.wallet
        prix_mission = Decimal(str(mission.prix))

        if portefeuille.solde >= prix_mission:
            portefeuille.solde -= prix_mission
            portefeuille.solde_bloque += prix_mission
            portefeuille.save()

            candidature.accepte = True
            candidature.save()

            if mission.est_complete:
                mission.statut = 'RESERVEE'
                mission.save()

            messages.success(request, "Candidat accepté. L'argent est sécurisé par Mbolo.")
        else:
            messages.error(request, f"Solde insuffisant ({prix_mission} F requis).")

    return redirect('gestion_mission', mission_id=mission.id)

@login_required
def valider_mission(request, mission_id):
    """Le recruteur confirme que le travail est fait : on libère l'argent"""
    mission = get_object_or_404(Mission, id=mission_id, auteur=request.user)
    
    if mission.statut in ['RESERVE', 'RESERVEE']:
        try:
            admin_mbolo = User.objects.get(email=EMAIL_ADMIN_PLATEFORME)
        except User.DoesNotExist:
            messages.error(request, "Erreur : Compte admin Mbolo introuvable.")
            return redirect('dashboard')

        # On paie tous les travailleurs acceptés pour cette mission
        candidatures_valides = mission.candidatures.filter(accepte=True)
        
        with transaction.atomic():
            for cand in candidatures_valides:
                montant_brut = Decimal(str(mission.prix))
                commission = montant_brut * Decimal('0.10')
                montant_net = montant_brut - commission

                # Libération du séquestre
                request.user.wallet.solde_bloque -= montant_brut
                request.user.wallet.save()

                # Paiement travailleur + plateforme
                cand.travailleur.wallet.solde += montant_net
                cand.travailleur.wallet.save()
                admin_mbolo.wallet.solde += commission
                
            admin_mbolo.wallet.save()
            mission.statut = 'TERMINE'
            mission.save()
            messages.success(request, "Mission clôturée. Les travailleurs ont été payés.")
        
    return redirect('dashboard')

# --- WALLET ET SERVICES PREMIUM ---
def gestion_mission(request, mission_id):
    # On récupère la mission ou on affiche une erreur 404 si elle n'existe pas
    mission = get_object_or_404(Mission, id=mission_id)
    
    # Sécurité : Seul l'auteur de la mission peut voir les candidats
    if mission.auteur != request.user:
        messages.error(request, "Accès refusé.")
        return redirect('dashboard')
    
    # On récupère toutes les candidatures pour cette mission
    candidatures = mission.candidatures.all() 
    
    return render(request, 'interim/gestion_mission.html', {
        'mission': mission,
        'candidatures': candidatures
    })
@login_required
def dashboard_view(request):
    wallet, _ = Portefeuille.objects.get_or_create(user=request.user)
    mes_postulations = Candidature.objects.filter(travailleur=request.user).select_related('mission')
    mes_annonces = Mission.objects.filter(auteur=request.user).order_by('-date_creation')
    nouveaux_messages = Message.objects.filter(destinataire=request.user, lu=False).count()
    
    return render(request, 'interim/dashboard.html', {
        'wallet': wallet,
        'mes_postulations': mes_postulations,
        'mes_annonces': mes_annonces,
        'nouveaux_messages': nouveaux_messages
    })

@login_required
def recharger_portefeuille(request):
    if request.method == 'POST':
        montant = request.POST.get('montant')
        if montant and int(montant) > 0:
            wallet = request.user.wallet
            wallet.solde += int(montant)
            wallet.save()
            Transaction.objects.create(user=request.user, montant=int(montant), type_transaction='DEPOT')
            messages.success(request, f"{montant} FCFA ajoutés.")
            return redirect('dashboard')
    return render(request, 'interim/recharger.html')

@login_required
def booster_mission(request, mission_id):
    mission = get_object_or_404(Mission, id=mission_id, auteur=request.user)
    wallet = request.user.wallet
    
    if wallet.solde >= 500:
        admin = User.objects.get(email=EMAIL_ADMIN_PLATEFORME)
        with transaction.atomic():
            wallet.solde -= 500
            admin.wallet.solde += 500
            wallet.save()
            admin.wallet.save()
            mission.is_boosted = True
            mission.boost_expires_at = timezone.now() + timedelta(days=3)
            mission.save()
        messages.success(request, "Mission boostée ! 🚀")
    else:
        messages.error(request, "Solde insuffisant (500 F).")
    return redirect('dashboard')

@login_required
def activer_premium(request):
    if request.method == 'POST':
        wallet = request.user.wallet
        PRIX = 2000
        if wallet.solde >= PRIX:
            admin = User.objects.get(email=EMAIL_ADMIN_PLATEFORME)
            with transaction.atomic():
                wallet.solde -= PRIX
                admin.wallet.solde += PRIX
                wallet.save()
                admin.wallet.save()
                request.user.is_premium = True
                request.user.date_expiration_premium = timezone.now() + timedelta(days=30)
                request.user.save()
            messages.success(request, "Vous êtes désormais Premium ! ⭐")
            return redirect('dashboard')
        else:
            messages.error(request, "Solde insuffisant.")
    return render(request, 'interim/premium.html')

# --- MESSAGERIE ET AVIS ---

@login_required
def chat_mission(request, mission_id, user_id):
    mission = get_object_or_404(Mission, id=mission_id)
    destinataire = get_object_or_404(User, id=user_id)
    
    Message.objects.filter(mission=mission, expediteur=destinataire, destinataire=request.user).update(lu=True)
    messages_list = Message.objects.filter(mission=mission).filter(
        (Q(expediteur=request.user) & Q(destinataire=destinataire)) |
        (Q(expediteur=destinataire) & Q(destinataire=request.user))
    ).order_by('date_envoi')

    if request.method == 'POST':
        contenu = request.POST.get('contenu')
        if contenu:
            Message.objects.create(mission=mission, expediteur=request.user, destinataire=destinataire, contenu=contenu)
            return redirect('chat_mission', mission_id=mission.id, user_id=user_id)

    return render(request, 'interim/chat.html', {'mission': mission, 'destinataire': destinataire, 'messages_list': messages_list})

@login_required
def laisser_avis(request, mission_id, user_id):
    mission = get_object_or_404(Mission, id=mission_id)
    travailleur = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        note = request.POST.get('note')
        commentaire = request.POST.get('commentaire')
        if note and commentaire:
            Avis.objects.create(mission=mission, evaluateur=request.user, travailleur=travailleur, note=int(note), commentaire=commentaire)
            messages.success(request, "Avis publié ! ⭐")
            return redirect('dashboard')
    return render(request, 'interim/laisser_avis.html', {'mission': mission, 'travailleur': travailleur})

# --- AUTRES ---

@login_required
def soumettre_verification(request):
    if request.method == 'POST':
        form = VerificationForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            user.statut_verification = 'EN_ATTENTE'
            user.date_soumission_verif = timezone.now()
            user.save()
            messages.success(request, "Pièce transmise pour vérification.")
            return redirect('dashboard')
    else:
        form = VerificationForm(instance=request.user)
    return render(request, 'interim/soumettre_verification.html', {'form': form})
def annuler_candidature(request, candidature_id):
    # On récupère la candidature, mais SEULEMENT si c'est celle de l'utilisateur connecté
    candidature = get_object_or_404(Candidature, id=candidature_id, travailleur=request.user)
    
    if request.method == 'POST':
        candidature.delete()
        messages.success(request, "Votre candidature a été retirée.")
    
    return redirect('dashboard')
@login_required
def liste_chats(request):
    # On récupère tous les messages où l'utilisateur est soit l'expéditeur, soit le destinataire
    # On trie pour avoir les plus récents en premier
    messages_recents = Message.objects.filter(
        Q(expediteur=request.user) | Q(destinataire=request.user)
    ).order_by('-date_envoi')

    # On crée une liste unique d'interlocuteurs par mission
    # (Pour ne pas afficher 50 fois la même personne pour la même mission)
    chats = []
    vus = set()

    for m in messages_recents:
        # On crée une clé unique (Interlocuteur + Mission)
        interlocuteur = m.destinataire if m.expediteur == request.user else m.expediteur
        cle = (interlocuteur.id, m.mission.id)
        
        if cle not in vus:
            chats.append({
                'interlocuteur': interlocuteur,
                'mission': m.mission,
                'dernier_message': m.contenu,
                'date': m.date_envoi,
                'non_lu': m.destinataire == request.user and not m.lu
            })
            vus.add(cle)

    return render(request, 'interim/liste_chats.html', {'chats': chats})
@login_required
def supprimer_compte(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "Compte supprimé définitivement.")
        return redirect('home')
    return render(request, 'interim/confirm_delete_account.html')

def page_aide(request):
    return render(request, 'aide.html')
def page_cgu(request):
    """Affiche la page des Conditions Générales d'Utilisation"""
    return render(request, 'cgu.html')
@login_required
def menu_mobile(request):
    return render(request, 'interim/menu_mobile.html')