from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django import forms

from .models import *

# Form for creating a new listing
class ListingForm(forms.Form):
    title = forms.CharField(label='Listing Title', max_length=50)
    startingBid = forms.IntegerField(label='Starting Bid')
    image = forms.URLField(label='Image', max_length=200)
    category = forms.CharField(label='Category', max_length=25)
    active = forms.BooleanField(initial=True)

def index(request):
    return render(request, "auctions/index.html", {
        "listings": AuctionListing.objects.all()
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

# Create a new listing
@login_required  
def create(request):
    if request.method == "GET":
        return render(request, "auctions/create.html")
    elif request.method == "POST":
        return render(request, "auctions/create.html")
    else:
        return HttpResponseRedirect(reverse("index"))
    
# View an existing listing
@login_required  
def listing(request, listing_id):
    listing = AuctionListing.objects.get(id=listing_id)
    return render(request, "auctions/listing.html", {
        "listing": listing
    })