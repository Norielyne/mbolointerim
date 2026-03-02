from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Mission
from datetime import date  # <--- AJOUTE CETTE LIGNE

# interim/forms.py
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class InscriptionForm(UserCreationForm):
    # 1. Champs de base visibles
    first_name = forms.CharField(label="Prénom")
    last_name = forms.CharField(label="Nom")
    email = forms.EmailField(label="Email")
    
    # Indicatif caché
    indicatif_pays = forms.CharField(
        initial='+241',
        widget=forms.HiddenInput(),
        required=False  
    )
    
    phone = forms.CharField(
        label="Téléphone",
        help_text="Ex: 77123456"
    )

    date_naissance = forms.DateField(
        label="Date de naissance",
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )
    
    accept_cgu = forms.BooleanField(
        label="Conditions Générales",
        required=True
    )

    class Meta:
        model = User
        # IMPORTANT : On définit la liste EXACTE des champs. 
        # Si 'username' n'est pas ici, Django ne l'affichera pas.
        fields = (
            'first_name', 
            'last_name', 
            'email', 
            'phone', 
            'date_naissance', 
            'user_type', 
            'ville', 
            'accept_cgu',
            'indicatif_pays' # On l'inclut pour qu'il soit traité, mais il est Hidden
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # On s'assure que le champ username n'est pas requis par le formulaire
        if 'username' in self.fields:
            del self.fields['username']

        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.HiddenInput):
                continue

            if field_name == 'accept_cgu':
                field.widget.attrs.update({'class': 'mt-1 w-4 h-4 rounded border-gray-300 text-blue-600'})
                continue 

            base_class = 'w-full p-4 bg-gray-50 border-none rounded-2xl focus:ring-2 focus:ring-blue-500 transition-all font-semibold text-gray-700'
            field.widget.attrs.update({'class': base_class})
            
            if not field.widget.attrs.get('placeholder'):
                label_text = field.label if field.label else field_name
                field.widget.attrs.update({'placeholder': f'Votre {str(label_text).lower()}'})

    def clean_indicatif_pays(self):
        return '+241'

    def clean_date_naissance(self):
        date_naissance = self.cleaned_data.get('date_naissance')
        if date_naissance:
            today = date.today()
            age = today.year - date_naissance.year - ((today.month, today.day) < (date_naissance.month, date_naissance.day))
            if age < 18:
                raise forms.ValidationError("Désolé, vous devez avoir 18 ans ou plus pour utiliser Mbolo Intérim.")
        return date_naissance

    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Nettoyage du téléphone
        indicatif = self.cleaned_data.get('indicatif_pays', '+241')
        numero = self.cleaned_data.get('phone').strip().replace(" ", "")
        
        if numero.startswith('0'):
            numero = numero[1:]
            
        user.phone = f"{indicatif}{numero}"
        
        # UTILISATION DE L'EMAIL COMME IDENTIFIANT
        user.username = self.cleaned_data["email"]
        user.email = self.cleaned_data["email"]
        
        if commit:
            user.save()
        return user

class MissionForm(forms.ModelForm):
    class Meta:
        model = Mission
        fields = ['titre', 'description', 'categorie', 'prix', 'ville', 'quartier', 'date_mission', 'horaire','nombre_places']
        widgets = {
            'categorie': forms.Select(attrs={
                'class': 'w-full p-4 bg-gray-50 border-none rounded-2xl font-semibold text-gray-700 focus:ring-2 focus:ring-blue-500'
            }),
            'date_mission': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full p-4 bg-gray-50 border-none rounded-2xl focus:ring-2 focus:ring-blue-500'
            }),
            'nombre_places': forms.NumberInput(attrs={
                'class': 'w-full p-4 bg-gray-50 rounded-2xl border-none outline-none font-bold',
                'min': '1',
                'placeholder': 'Nombre de personnes'
            }),
            # Ajoute les autres widgets ici pour garder le design Tailwind partout
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full p-3 border border-gray-300 rounded-xl mb-1 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all'
            })
class ProfilUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'photo', 'bio', 'competences', 'experiences', 'cv', 'ville', 'phone']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'w-full p-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none'})
class VerificationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['type_piece_identite', 'fichier_piece_identite']
        widgets = {
            'type_piece_identite': forms.Select(attrs={'class': 'w-full p-4 bg-gray-50 rounded-2xl border-none'}),
            'fichier_piece_identite': forms.FileInput(attrs={'class': 'w-full p-4 bg-gray-50 rounded-2xl border-none'}),
        }
