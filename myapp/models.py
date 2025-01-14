from django.db import models
from datetime import datetime, timedelta


class Utilisateur(models.Model):
    numero_etudiant = models.CharField(max_length=8, unique=True)
    mot_de_passe = models.CharField(max_length=128)
    annee_etude = models.CharField(max_length=50)
    prenom = models.CharField(max_length=100)
    nom = models.CharField(max_length=100)
    is_blocked = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    last_password_reset = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.prenom} {self.nom}"   

class Box(models.Model):
    id = models.AutoField(primary_key=True)
    nom_ufr = models.CharField(max_length=15)
    
    def __str__(self):
        return self.nom_ufr
    
class Reservation(models.Model):
    box = models.ForeignKey(Box, on_delete=models.CASCADE)
    numero_etudiant = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    creneau_horaire = models.DateTimeField(max_length=10)

    def __str__(self):
        return f"{self.box} - {self.numero_etudiant} - {self.creneau_horaire}"

def block_user(self):
    self.is_blocked = True
    self.save()

def unblock_user(self):
    self.is_blocked = False
    self.save()