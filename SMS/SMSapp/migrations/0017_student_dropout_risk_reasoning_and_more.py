# Generated by Django 5.2.1 on 2025-05-24 10:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SMSapp', '0016_rename_performance_summary_student_performance_analysis_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='dropout_risk_reasoning',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='student',
            name='profile_reasoning',
            field=models.TextField(blank=True, null=True),
        ),
    ]
