# Generated by Django 5.2.1 on 2025-05-24 07:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SMSapp', '0013_grade'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='gwa',
            field=models.FloatField(default=0.0),
        ),
        migrations.DeleteModel(
            name='Grouping',
        ),
    ]
