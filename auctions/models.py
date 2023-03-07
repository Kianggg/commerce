from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    id = models.AutoField(primary_key=True)
    def __str__(self):
        return f"{self.username}"

class AuctionListing(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50)
    startingBid = models.IntegerField(default=0)
    image = models.URLField(max_length=200)
    category = models.CharField(max_length=25)
    description = models.CharField(max_length=280, default="Description of the listing")
    poster = models.ForeignKey(User, on_delete=models.CASCADE)
    watchlistUsers = models.ManyToManyField(User, blank=True, related_name="watchlistUsers")
    active = models.BooleanField()

    def __str__(self):
        return f"{self.title}"

class Bid(models.Model):
    id = models.AutoField(primary_key=True)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.IntegerField()
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.bidder.username}: ${self.amount}."
    
class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    text = models.CharField(max_length=280)
    commenter = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.text}."