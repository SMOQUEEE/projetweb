# Generated by Django 5.0.6 on 2025-01-04 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0006_delete_reservationserverice'),
    ]

    operations = [
        migrations.AddField(
            model_name='utilisateur',
            name='is_admin',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='utilisateur',
            name='is_blocked',
            field=models.BooleanField(default=False),
        ),
    ]
