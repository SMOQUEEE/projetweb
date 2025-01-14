# Generated by Django 5.0.6 on 2025-01-05 20:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0007_utilisateur_is_admin_utilisateur_is_blocked'),
    ]

    operations = [
        migrations.AddField(
            model_name='utilisateur',
            name='last_password_reset',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='utilisateur',
            name='annee_etude',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='utilisateur',
            name='nom',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='utilisateur',
            name='numero_etudiant',
            field=models.CharField(max_length=8, unique=True),
        ),
        migrations.AlterField(
            model_name='utilisateur',
            name='prenom',
            field=models.CharField(max_length=100),
        ),
    ]
