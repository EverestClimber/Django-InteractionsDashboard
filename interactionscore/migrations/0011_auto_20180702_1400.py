# Generated by Django 2.0.6 on 2018-07-02 14:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('interactionscore', '0010_project_user'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='interaction',
            options={'permissions': [('list_all_interaction', 'Can list all Interactions'), ('list_own_ag_interaction', 'Can list Interactions of own AGs')]},
        ),
    ]
