# Generated by Django 4.1.7 on 2023-03-06 23:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='auctionlisting',
            name='description',
            field=models.CharField(default='Description of the listing', max_length=280),
        ),
        migrations.AddField(
            model_name='auctionlisting',
            name='startingBid',
            field=models.IntegerField(default=0),
        ),
    ]