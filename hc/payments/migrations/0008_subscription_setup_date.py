# Generated by Django 3.1.2 on 2020-11-06 12:07

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("payments", "0007_auto_20200727_1430"),
    ]

    operations = [
        migrations.AddField(
            model_name="subscription",
            name="setup_date",
            field=models.DateField(blank=True, null=True),
        ),
    ]
