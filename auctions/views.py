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
    description = forms.CharField(label='Description', max_length=280)

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
        return render(request, "auctions/create.html", {
            "form": ListingForm()
        })
    elif request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid:
            # Populating and saving the new listing
            l = AuctionListing(
                title=request.POST.get("title"),
                startingBid=request.POST.get("startingBid"),
                image=request.POST.get("image"),
                category=request.POST.get("category"),
                description=request.POST.get("description"),
                poster=request.user.id,
                active=True)
            l.save()
            # Redirect to page for newly-created listing
            return HttpResponseRedirect(f"/{l.id}")
        else:
            return render(request, "auctions/create.html", {
            "form": form
        })
    else:
        return HttpResponseRedirect(reverse("index"))
    
# View an existing listing
@login_required
def listing(request, listing_id):
    listing = AuctionListing.objects.get(id=listing_id)

    # Get comments
    comments = Comment.objects.all()

    # Calculate greatest bid
    bids = Bid.objects.all()
    foundBid = False
    winningBid = None
    winningBidAmount = 0
    for bid in bids:
        if bid.listing == listing:
            if bid.amount > winningBidAmount and bid.amount > listing.startingBid:
                foundBid = True
                winningBidAmount = bid.amount
                winningBid = bid
    if not foundBid:
        winningBid = "No bids placed!"
    if listing.active:
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "winningBid": winningBid,
            "comments": comments
        })
    else:
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "winningBid": winningBid,
            "comments": comments,
            "winner": winningBid.bidder
        })

# Place a bid on a listing
@login_required
def bid(request, listing_id):
    if request.method == "POST":
        listing = AuctionListing.objects.get(pk=listing_id)

        # Get the winning bid amount for this listing
        # Calculate greatest bid
        bids = Bid.objects.all()
        foundBid = False
        winningBid = None
        winningBidAmount = 0
        for bid in bids:
            if bid.listing == listing:
                if bid.amount > winningBidAmount and bid.amount > listing.startingBid:
                    foundBid = True
                    winningBidAmount = bid.amount
                    winningBid = bid
        if not foundBid:
            winningBid = "No bids placed!"
        
        # Check to see if it is higher than the largest previous bid
        if int(request.POST.get("bidAmount")) <= winningBidAmount:
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "winningBid": winningBid,
                "error": "Your bid must be greater than the current highest bid!"
            })
        else:
            # The new bid is valid, so create it
            b = Bid(
                bidder=request.user,
                amount=request.POST.get("bidAmount"),
                listing=AuctionListing.objects.get(pk=listing_id))
            b.save()
            # Update listing page
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "winningBid": winningBid,
                "message": "Bid placed successfully!"
            })
    else:
        return HttpResponseRedirect(reverse("index"))

# Add a listing to a user's watchlist
@login_required
def watch(request, listing_id):
    if request.method == "POST":
        listing = AuctionListing.objects.get(pk=listing_id)
        user_id = request.user.id
        user = User.objects.get(pk=user_id)
        if not user in listing.watchlistUsers.all():
            listing.watchlistUsers.add(user)
        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
    else:
        return HttpResponseRedirect(reverse("index"))

# A user's individual watchlist
@login_required
def watchlist(request):
    return render(request, "auctions/watchlist.html", {
            "listings": AuctionListing.objects.all()
        })

# Close an auction
@login_required
def close(request, listing_id):
    if request.method == "POST":
        listing = AuctionListing.objects.get(pk=listing_id)
        # Double-check that the person who sent the close request is the listing's original poster
        user_id = request.user.id
        if user_id == listing.poster.id:
            listing.active = False
            listing.save()
        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
    else:
        return HttpResponseRedirect(reverse("index"))
    
# View list of all categories
@login_required
def categories(request):
    categoriesList = []
    listings = AuctionListing.objects.all()
    for listing in listings:
            if not listing.category in categoriesList:
                categoriesList.append(listing.category)
    return render(request, "auctions/categories.html", {
        "categories": categoriesList
    })

# View listings by given category
@login_required
def category(request, category_query):
    return render(request, "auctions/categories.html", {
        "category": category_query,
        "listings": AuctionListing.objects.all()
    })