# Generated by Django 5.0.7 on 2024-08-06 20:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0001_initial'),
        ('planets', '0006_alter_question_hint'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='phase',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='games', to='planets.phase', verbose_name='Phase'),
        ),
    ]
