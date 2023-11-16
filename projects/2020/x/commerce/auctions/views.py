from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Category, Listing, Comment, Bid


def listing(request, id):
    '''Displays items currently in a user's watchlist'''
    listing_info = Listing.objects.get(pk=id)
    listing_in_watchlist = request.user in listing_info.watchlist.all()
    all_comments = Comment.objects.filter(listing=listing_info)
    user_is_owner = request.user.username == listing_info.lister.username
    return render(request, "auctions/listing.html", {
        "listing": listing_info, 
        "listing_in_watchlist": listing_in_watchlist,
        "all_comments": all_comments,
        "user_is_owner": user_is_owner
    })

# Home display
def index(request):
    categories = Category.objects.all()
    active_listings = Listing.objects.filter(active=True)
    return render(request, "auctions/index.html", {
        "listings": active_listings,
        "categories": categories
    })

def closed_listing(request):
    categories = Category.objects.all()
    active_listings = Listing.objects.filter(active=False)
    return render(request, "auctions/closed.html", {
        "listings": active_listings,
        "categories": categories
    })

def add_comment(request, id):
    current_user = request.user
    listing_info = Listing.objects.get(pk=id)
    comment = request.POST['new_comment']

    new_comment = Comment(
        author = current_user,
        listing = listing_info,
        comment = comment
    )
    new_comment.save()
    return HttpResponseRedirect(reverse("listing", args=(id, )))

def add_bid(request, id):
    new_bid = request.POST['new_bid']
    listing_info = Listing.objects.get(pk=id)
    listing_in_watchlist = request.user in listing_info.watchlist.all()
    all_comments = Comment.objects.filter(listing=listing_info)
    user_is_owner = request.user.username == listing_info.lister.username
    try:
        if float(new_bid) > float(listing_info.price.bid):
            updated_bid = Bid(lister=request.user, bid=new_bid)
            updated_bid.save()

            listing_info.price = updated_bid
            listing_info.save()
            return render(request, "auctions/listing.html", {
                "listing": listing_info,
                "message": f"Bid updated successfully to ${listing_info.price}",
                "update": True,
                "listing_in_watchlist": listing_in_watchlist,
                "all_comments": all_comments,
                "user_is_owner": user_is_owner,

            })
        else:
            return render(request, "auctions/listing.html", {
                "listing": listing_info,
                "message": "Your bid amount is too low. Bid update failed!",
                "update": False,
                "listing_in_watchlist": listing_in_watchlist,
                "all_comments": all_comments,
                "user_is_owner": user_is_owner,
            })
    except ValueError:
        return render(request, "auctions/listing.html", {
                "listing": listing_info,
                "message": "Please enter a valid amount😏",
                "update": False,
                "listing_in_watchlist": listing_in_watchlist,
                "all_comments": all_comments,
                "user_is_owner": user_is_owner,
            })

def watchlist(request):
    current_user = request.user
    listings = current_user.wachlist_listing.all()
    return render(request, "auctions/watchlist.html", {
        "listings": listings
    })

def close_auction(request, id):
    listing_info = Listing.objects.get(pk=id)
    listing_info.active = False
    listing_info.save()
    user_is_owner = request.user.username == listing_info.lister.username
    listing_in_watchlist = request.user in listing_info.watchlist.all()
    all_comments = Comment.objects.filter(listing=listing_info)
    return render(request, "auctions/listing.html", {
        "listing": listing_info, 
        "listing_in_watchlist": listing_in_watchlist,
        "all_comments": all_comments,
        "user_is_owner": user_is_owner,
        "update": True,
        "message": "You've closed this auction."
    })

def remove_from_watchlist(request, id):
    '''Removes a listing from user's watchlist'''
    listing_info = Listing.objects.get(pk=id)
    current_user = request.user
    listing_info.watchlist.remove(current_user)
    return HttpResponseRedirect(reverse("listing", args=(id, )))

def add_to_watchlist(request, id):
    '''Adds a listing to a user's watchlist'''
    listing_info = Listing.objects.get(pk=id)
    current_user = request.user
    listing_info.watchlist.add(current_user)
    return HttpResponseRedirect(reverse("listing", args=(id, )))
def list_categories(request):
    '''Displays listings from the category selected only'''
    if request.method == "POST":
        current_category = request.POST['category']
        category = Category.objects.get(category_name=current_category)
        active_listings = Listing.objects.filter(active=True, category=category)
        categories = Category.objects.all()
        return render(request, "auctions/index.html", {
            "listings": active_listings,
            "categories": categories
        })

def create_listing(request):
    '''Creates a new listing'''
    categories = Category.objects.all()
    if request.method == "GET":
        return render(request, "auctions/create.html", {
            "categories": categories
        })
    else:
        # Get data from the submitted form
        title = request.POST["title"]
        description = request.POST["description"]
        image_url = request.POST["image_url"]
        price = request.POST["price"]
        category = request.POST["category"]

        # Get the current user
        current_user = request.user

        # Get the category data
        category_data = Category.objects.get(category_name=category)

        # Add a new bid
        bid = Bid(bid=float(price), lister=current_user)
        bid.save()
        # Create the listing object
        listing = Listing(
            title = title,
            description = description,
            image_url = image_url,
            price = bid,
            category = category_data,
            lister = current_user
        )

        # Save the object to database
        listing.save()

        # Redirect to index page
        return HttpResponseRedirect(reverse(index))
def login_view(request):
    '''View for a logged in user'''
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
    
def profile(request):
    return render(request, "auctions/profile.html", {
        "profile_icon":"profile_icon"
    })


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
