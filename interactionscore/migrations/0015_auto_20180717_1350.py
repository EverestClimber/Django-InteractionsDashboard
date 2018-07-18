# Generated by Django 2.0.6 on 2018-07-17 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interactionscore', '0014_hcp_has_consented'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='interaction',
            name='is_follow_up_required',
        ),
        migrations.AddField(
            model_name='interaction',
            name='no_follow_up_required',
            field=models.BooleanField(default=False),
        ),
    ]