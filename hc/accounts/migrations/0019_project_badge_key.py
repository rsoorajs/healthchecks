# Generated by Django 2.1.5 on 2019-01-12 19:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("accounts", "0018_auto_20190112_1426")]

    operations = [
        migrations.AddField(
            model_name="project",
            name="badge_key",
            field=models.CharField(blank=True, max_length=150, null=True),
        )
    ]
