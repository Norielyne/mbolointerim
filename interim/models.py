from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal  # <--- AJOUTE CETTE LIGNE
from django.db import models
# ... tes autres imports


class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'adresse email est obligatoire")
        email = self.normalize_email(email)
        
        # On force le username à être l'email pour la compatibilité interne
        extra_fields.setdefault('username', email)
        
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Le superutilisateur doit avoir is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Le superutilisateur doit avoir is_superuser=True.')

        # On appelle create_user sans passer de 'username' manuellement
        return self.create_user(email, password, **extra_fields)

# 2. TON MODÈLE USER
class User(AbstractUser):
    # --- LES CHOIX ---
    USER_TYPE_CHOICES = (
        ('PARTICULIER', 'Particulier (Travailleur & Petit Recruteur)'),
        ('ENTREPRISE', 'Entreprise'),
    )
    TYPE_PIECE = [
        ('CNI', 'Carte Nationale d’Identité'),
        ('PASSEPORT', 'Passeport'),
        ('PERMIS', 'Permis de Conduire'),
        ('CNAMGS', 'Carte CNAMGS'),
    ]
    STATUT_VERIF = [
        ('NON_VERIFIE', 'Non vérifié'),
        ('EN_ATTENTE', 'En attente de validation'),
        ('VERIFIE', 'Profil Vérifié ✅'),
        ('REJETE', 'Pièce rejetée'),
    ]

    # --- CHAMPS PRINCIPAUX ---
    email = models.EmailField(unique=True, verbose_name="Adresse email")
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    
    # On définit l'Email comme identifiant unique
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    # !!! LA LIGNE MAGIQUE : On dit à Django d'utiliser notre MyUserManager !!!
    objects = MyUserManager()

    # --- TES AUTRES CHAMPS ---
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='PARTICULIER')
    phone = models.CharField(max_length=15, verbose_name="Numéro Mobile Money")
    ville = models.CharField(max_length=100, default="Libreville")
    photo = models.ImageField(upload_to='profiles/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    cv = models.FileField(upload_to='cvs/', null=True, blank=True)
    competences = models.CharField(max_length=255, blank=True)
    nom_entreprise = models.CharField(max_length=150, blank=True)
    niu = models.CharField(max_length=50, blank=True, verbose_name="Numéro NIU")
    first_name = models.CharField(max_length=150, verbose_name="Prénom")
    last_name = models.CharField(max_length=150, verbose_name="Nom")
    experiences = models.TextField(max_length=1000, blank=True, verbose_name="Expériences")
    is_premium = models.BooleanField(default=False)
    date_expiration_premium = models.DateTimeField(null=True, blank=True)
    type_piece_identite = models.CharField(max_length=20, choices=TYPE_PIECE, blank=True)
    fichier_piece_identite = models.FileField(upload_to='identite/', blank=True, null=True)
    statut_verification = models.CharField(max_length=20, choices=STATUT_VERIF, default='NON_VERIFIE')
    date_soumission_verif = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.email


    def note_moyenne(self):
        avis = self.avis_recus.all()
        if avis.exists():
            total = sum([a.note for a in avis])
            return round(total / avis.count(), 1)
        return "Nouveau"
    

# 2. MISSIONS
class Mission(models.Model):
    STATUT_CHOICES = [
        ('OUVERT', 'Ouvert'),
        ('RESERVE', 'Réservé (Paiement bloqué)'),
        ('TERMINE', 'Mission terminée'),
        ('CLOTURE', 'Clôturé (Payé)'),
    ]
    CATEGORIES = [
        ('MAISON', '🏠 Maison (Ménage, Cuisine, Nounou)'),
        ('BRICOLAGE', '🛠️ Travaux (Plomberie, Électricité, Maçonnerie)'),
        ('TRANSPORT', '🚗 Transport (Livraison, Chauffeur, Déménagement)'),
        ('TECH', '💻 Informatique (Réparation PC, Design, Web)'),
        ('BEAUTE', '✨ Beauté (Coiffure, Maquillage, Massage)'),
        ('SERVICES', '💼 Services (Cours particuliers, Gardiennage, Secrétariat)'),
        ('AUTRE', '➕ Autre service'),
    ]

    auteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mes_missions')
    titre = models.CharField(max_length=100)
    description = models.TextField()
    ville = models.CharField(max_length=50, default="Libreville")
    quartier = models.CharField(max_length=50, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='OUVERT')
    date_mission = models.DateField(verbose_name="Jour de la mission", null=True, blank=True)
    horaire = models.CharField(max_length=100, help_text="Ex: De 08h à 17h", blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    is_boosted = models.BooleanField(default=False)
    boost_expires_at = models.DateTimeField(null=True, blank=True)
    nombre_places = models.PositiveIntegerField(default=1)
    prix = models.DecimalField(max_digits=10, decimal_places=0)
    travailleur_selectionne = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='missions_effectuees'
    )
    
    categorie = models.CharField(
        max_length=50, 
        choices=CATEGORIES, 
        default='MAISON'
    )

    def __str__(self):
        return f"{self.titre} - {self.prix} FCFA"

    # Petite fonction pour l'icône dans la liste des missions
    def get_icon(self):
        icons = {
            'MAISON': '🏠', 'BRICOLAGE': '🛠️', 'TRANSPORT': '🚗',
            'TECH': '💻', 'BEAUTE': '✨', 'SERVICES': '💼', 'AUTRE': '➕',
        }
        return icons.get(self.categorie, '🔵')

    @property
    def prix_net_travailleur(self):
        """Ce que le travailleur va REELLEMENT recevoir (90%)"""
        return int(Decimal(str(self.prix)) * Decimal('0.90'))

    # --- LOGIQUE POUR LE RECRUTEUR (LE BLOQUÉ) ---
    @property
    def argent_bloque_total(self):
        """Calcule l'argent actuellement bloqué en séquestre pour cette mission"""
        try:
            nb_acceptes = self.candidatures.filter(accepte=True).count()
        except:
            nb_acceptes = 0
        # On bloque le prix BRUT (100%) par candidat accepté
        return int(Decimal(str(self.prix)) * nb_acceptes)

    @property
    def commission_mbolo(self):
        """Calcule la part qui revient à la plateforme (10%)"""
        return int(Decimal(str(self.prix)) * Decimal('0.10'))

    # --- GESTION DES PLACES ---
    @property
    def places_restantes(self):
        try:
            accepte_count = self.candidatures.filter(accepte=True).count()
        except:
            accepte_count = 0
        return max(0, self.nombre_places - accepte_count)

    @property
    def est_complete(self):
        return self.places_restantes <= 0

# 3. CANDIDATURES (L'OUBLI NUMÉRO 1)
class Candidature(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name='candidatures')
    travailleur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='postulations')
    message = models.TextField(blank=True)
    accepte = models.BooleanField(default=False)
    date_postulation = models.DateTimeField(auto_now_add=True)
    note_travailleur = models.PositiveIntegerField(null=True, blank=True) # Note de 1 à 5
commentaire_recruteur = models.TextField(blank=True)

class Meta:
    unique_together = ('mission', 'travailleur')
    ordering = ['-is_boosted', '-date_creation']

def __str__(self):
    return f"{self.travailleur.username} -> {self.mission.titre}"

# 4. PORTEFEUILLE ET TRANSACTIONS
class Portefeuille(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    solde = models.PositiveIntegerField(default=0)
    solde_bloque = models.PositiveIntegerField(default=0)

class Transaction(models.Model):
    TYPE_CHOICES = [('DEPOT', 'Dépôt'), ('PAIEMENT', 'Paiement'), ('RECEPTION', 'Réception')]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    montant = models.IntegerField()
    type_transaction = models.CharField(max_length=20, choices=TYPE_CHOICES)
    date = models.DateTimeField(auto_now_add=True)

# 5. AUTOMATISATION (L'OUBLI NUMÉRO 2 : Les Signals)
@receiver(post_save, sender=User)
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        Portefeuille.objects.create(user=instance)
class Avis(models.Model):
    mission = models.OneToOneField(Mission, on_delete=models.CASCADE, related_name='avis')
    evaluateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='avis_donnes')
    travailleur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='avis_recus')
    note = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    commentaire = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Note {self.note}/5 pour {self.travailleur.first_name}"
# interim/models.py

class Message(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name='messages')
    expediteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_envoyes')
    destinataire = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_recus')
    contenu = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)
    lu = models.BooleanField(default=False)

    class Meta:
        ordering = ['date_envoi']

    def __str__(self):
        return f"De {self.expediteur} à {self.destinataire} - {self.mission.titre}"
@property
def count_acceptes(self):
    return self.candidatures.filter(accepte=True).count()