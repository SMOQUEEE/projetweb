# Generated by Django 5.0.6 on 2024-12-28 21:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='utilisateur',
            old_name='mots_de_passe',
            new_name='mot_de_passe',
        ),
    ]
