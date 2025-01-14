from django import forms

class ConnexionForm(forms.Form):
    numero_etudiant = forms.IntegerField(label="Numéro d'étudiant")
    mot_de_passe = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)
