# Generated by Django 1.11.6 on 2018-01-27 12:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("api", "0036_auto_20180116_2243")]

    operations = [
        migrations.AlterField(
            model_name="ping",
            name="id",
            field=models.BigAutoField(primary_key=True, serialize=False),
        )
    ]
