# Generated by Django 2.0.6 on 2018-06-19 11:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('interactionscore', '0013_auto_20180619_1131'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='engagement_plan',
        ),
        migrations.AddField(
            model_name='comment',
            name='engagement_list_item',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='interactionscore.EngagementListItem'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='hcp_objective',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='interactionscore.HCPObjective'),
        ),
    ]
