# Generated by Django 1.11.4 on 2017-09-12 14:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("accounts", "0010_profile_team_limit")]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="sort",
            field=models.CharField(default="created", max_length=20),
        )
    ]
