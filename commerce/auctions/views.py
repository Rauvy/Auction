from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .models import User, Category, AuctionListing, Bid, Watchlist
from django.contrib.auth.decorators import login_required

def index(request):
    listings = AuctionListing.objects.all()
    return render(request, 'auctions/index.html',{
        "listings" : listings
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


# your_app/views.py


@login_required  # Ensure that only logged-in users can create a listing
def new_listing(request):
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        starting_bid = request.POST["starting_bid"]
        image = request.FILES.get("image")  # Use request.FILES to get the uploaded file
        
        # Retrieve the category instance based on the name from the form
        category_name = request.POST["category"]
        try:
            category = Category.objects.get(name=category_name)  # Get the Category instance
        except Category.DoesNotExist:
            category = None  # Handle the case where the category does not exist

        # Create a new listing
        listing = AuctionListing(
            title=title,
            description=description,
            starting_bid=starting_bid,
            image=image,  # Save the uploaded image
            category=category,  # Use the Category instance
            user=request.user  # Assign the current user
        )
        listing.save()  # Save the listing to the database

        return redirect('index')  # Redirect to the index page after saving

    return render(request, "auctions/new_listing.html")


def display_listing(request, listing_id):
    listing = get_object_or_404(AuctionListing, id=listing_id)
    user_is_owner = request.user == listing.user

    if request.method == "POST":
        bid_amount = request.POST.get("bid_amount")
        if bid_amount:
            bid_amount = float(bid_amount)

            # Ensure the bid amount is greater than the current highest bid
            if bid_amount > (listing.current_bid or listing.starting_bid):
                bid = Bid.objects.create(
                    auction_listing = listing,
                    user = request.user,
                    amount = bid_amount
                )
                listing.current_bid = bid_amount # Updating current bid on the listing
                listing.save()
    return render(request, "auctions/listing.html",{
        "listing" : listing,
        "user_is_owner" : user_is_owner
    })

def categories_listing(request):
    categories = Category.objects.all()
    return render(request, "auctions/category.html", {
        "categories": categories
    })

def listing_in_category(request, category):
    listings = AuctionListing.objects.filter(category__name=category)  # Filter listings by category name
    return render(request, "auctions/index.html", {  # Render the index template with the filtered listings
        "listings": listings
    })

@login_required
def add_to_watchlist(request, listing_id):
    listing = get_object_or_404(AuctionListing, id=listing_id)

    if request.user != listing.user:
        watchlist, created = Watchlist.objects.get_or_create(user=request.user)
        watchlist.listings.add(listing)
        watchlist.save()

    return redirect('display_listing', listing_id=listing_id)

@login_required
def remove_from_watchlist(request, listing_id):
    listing = get_object_or_404(AuctionListing, id=listing_id)
    watchlist = Watchlist.objects.filter(user=request.user).first()

    if watchlist:
        watchlist.listings.remove(listing)
        watchlist.save()
    
    return redirect('watchlist_page')

@login_required
def watchlist_page(request):
    watchlist = Watchlist.objects.filter(user=request.user).first()
    listings = watchlist.listings.all() if watchlist else []

    return render(request, 'auctions/watchlist.html', {
        'listings': listings
    })