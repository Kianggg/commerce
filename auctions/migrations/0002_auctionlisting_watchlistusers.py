# Generated by Django 4.1.7 on 2023-03-07 01:35

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='auctionlisting',
            name='watchlistUsers',
            field=models.ManyToManyField(blank=True, related_name='watchlistUsers', to=settings.AUTH_USER_MODEL),
        ),
    ]