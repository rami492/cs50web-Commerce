from os import name
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.forms import ModelForm
from .models import *
import datetime


class AuctionListingForm(ModelForm):
    class Meta:
        model = AuctionListing
        fields = ['name', 'category', 'price', 'description', 'feature1', 'feature2', 'feature3', 'feature4', 'feature5']
     

class ImageForm(ModelForm):
    class Meta:
        model = Image
        fields = ['image']


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        labels = {
            "content": "Leave your comments here"
        }


class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['amount']
        labels = {
            "amount": "Place your Bid here"
        }



def index(request):
    listings = AuctionListing.objects.all()
    user = request.user
    counter = 0
    if user.is_authenticated:
        try:
            user_wishlist = Wishlist.objects.get(user=User.objects.get(pk=user.id))
        except Wishlist.DoesNotExist:
            counter = 0
        else:
            for item in user_wishlist.listings.all():
                item = item
                counter += 1
    
    return render(request, "auctions/index.html", {
        "listings": listings,
        "counter": counter
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


def create_listing(request):
    user = request.user
    counter = 0
    if user.is_authenticated:
        try:
            user_wishlist = Wishlist.objects.get(user=User.objects.get(pk=user.id))
        except Wishlist.DoesNotExist:
            counter = 0
        else:
            for item in user_wishlist.listings.all():
                item = item
                counter += 1

    if request.method == 'POST':
        form = AuctionListingForm(request.POST)
        img_form = ImageForm(request.POST, request.FILES)
        user = request.user
        date = datetime.datetime.now()

        if img_form.is_valid():
            img = img_form.cleaned_data['image']
            image = Image.objects.create(image=img)
            image.save()
        else:
            return render(request, "auctions/create_listing.html", {
                "form": AuctionListingForm(request.POST),
                "img_form": ImageForm(),
                "message": "Invalid IMAGE",
                "counter": counter,
            })

        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            category = form.cleaned_data['category']
            price = form.cleaned_data['price']
            
            listing = AuctionListing.objects.create(name=name, description=description, category=category, price=price, image=image, user=User.objects.get(pk=user.id), timestamp=date)
            listing.save()
            return HttpResponseRedirect("/")
        else:
            return render(request, "auctions/create_listing.html", {
                "form": AuctionListingForm(),
                "img_form": ImageForm(),
                "message": "Invalid Form",
                "counter": counter,
            })

    return render(request, "auctions/create_listing.html", {
        "form": AuctionListingForm(),
        "img_form": ImageForm(),
        "counter": counter,
    })


def listing_page(request, listing_id):
    user = request.user
    date = datetime.datetime.now()
    comments = Comment.objects.filter(listing=listing_id).all()
    current_bids = len(Bid.objects.filter(listing=listing_id).all())
    
    highest_bidder = None
    bid = 0
    all_bids = Bid.objects.filter(listing=listing_id).all()
    counter = 0

    if len(all_bids) == 0:
        highest_bid = 0
    else:
        clean_all_bids = []
        for bid in all_bids:
            amount = int(bid.amount)
            clean_all_bids.append(amount)   
        highest_bid = max(clean_all_bids)
        high_bid = Bid.objects.get(amount=highest_bid)
        highest_bidder = high_bid.user

    if user.is_authenticated:
        try:
            user_wishlist = Wishlist.objects.get(user=User.objects.get(pk=user.id))
        except Wishlist.DoesNotExist:
            counter = 0
        else:
            for item in user_wishlist.listings.all():
                item = item
                counter += 1

    current_listing = AuctionListing.objects.get(pk=listing_id)
    listing_user = current_listing.user
    close_btn = False
    if listing_user.id == user.id:
        close_btn = True

    if request.method == "POST" and 'bid-btn' in request.POST:
        bidform = BidForm(request.POST)
        if bidform.is_valid():
            bid = bidform.cleaned_data['amount']

        listing = AuctionListing.objects.get(pk=listing_id)
        listing_price = listing.price
             
        if bid <= listing_price:
           return render(request, "auctions/listing.html", {
            "listing": listing,
            "comments": comments,
            "highest_bid": highest_bid,
            "highest_bidder": highest_bidder,
            "close_btn": close_btn,
            "counter": counter,
            "comment": CommentForm(),
            "bid": BidForm(request.POST),
            "current_bids": current_bids,
            "message": "bid must be greater than starting price",
            })
        elif bid <= highest_bid:   
            return render(request, "auctions/listing.html", {
            "listing": listing,
            "comment": CommentForm(),
            "comments": comments,
            "bid": BidForm(request.POST),
            "highest_bid": highest_bid,
            "highest_bidder": highest_bidder,
            "close_btn": close_btn,
            "counter": counter,
            "current_bids": current_bids,
            "message": "bid must be greater than current highest bid",
            })
        else:
            valid_bid = Bid.objects.create(user=User.objects.get(pk=user.id), listing=AuctionListing.objects.get(pk=listing_id), amount=bid, timestamp=date)
            valid_bid.save()
            
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "highest_bid": highest_bid,
                "comments": comments,
                "highest_bidder": highest_bidder,
                "comment": CommentForm(),
                "bid": BidForm(),
                "close_btn": close_btn,
                "counter": counter,
                "current_bids": current_bids,
                "message1": "Bid placed succussfully", 
                })
    
    elif request.method == "POST" and 'comment-btn' in request.POST:
        commentform = CommentForm(request.POST)
        if commentform.is_valid():
            content = commentform.cleaned_data['content']
        comment = Comment.objects.create(user=User.objects.get(pk=user.id), listing=AuctionListing.objects.get(pk=listing_id), content=content, timestamp=date)
        comment.save()

        return render(request, "auctions/listing.html", {
            "listing": current_listing,
            "highest_bid": highest_bid,
            "comments": comments,
            "highest_bidder": highest_bidder,
            "comment": CommentForm(),
            "bid": BidForm(),
            "close_btn": close_btn,
            "counter": counter,
            "current_bids": current_bids,
            "message1": "Comment Added", 
            })

    elif request.method == "POST" and 'close' in request.POST:
        current_listing = AuctionListing.objects.filter(pk=listing_id).update(is_active=False)
        listing = AuctionListing.objects.get(pk=listing_id)

        return render(request, "auctions/listing.html", {
            "listing": listing,
            "highest_bid": highest_bid,
            "comments": comments,
            "highest_bidder": highest_bidder,
            "comment": CommentForm(),
            "bid": BidForm(),
            "close_btn": close_btn,
            "counter": counter,
            "current_bids": current_bids,
            "message1": "Auction Closed", 
            })

    elif request.method == "POST" and 'watchlist-btn' in request.POST:
        try:
            user_wishlist = Wishlist.objects.get(user=User.objects.get(pk=user.id))
            user_wishlist.listings.add(current_listing)
            counter += 1
            
            return render(request, "auctions/listing.html", {
                "listing": current_listing,
                "comment": CommentForm(),
                "comments": comments,
                "bid": BidForm(request.POST),
                "highest_bid": highest_bid,
                "close_btn": close_btn,
                "counter": counter,
                "current_bids": current_bids,
                "message1": "Added to Wishlist",
                })
        
        except Wishlist.DoesNotExist:
            create_wishlist = Wishlist.objects.create(user=User.objects.get(pk=user.id))
            create_wishlist.listings.add(current_listing)
            counter += 1
            
            return render(request, "auctions/listing.html", {
            "listing": current_listing,
            "comment": CommentForm(),
            "comments": comments,
            "bid": BidForm(request.POST),
            "highest_bid": highest_bid,
            "close_btn": close_btn,
            "counter": counter,
            "current_bids": current_bids,
            "message1": "Added to Watchlist",
            })          
        
    try:
        listing = AuctionListing.objects.get(pk=listing_id)
    except AuctionListing.DoesNotExist:
        return render(request, "auctions/error.html", {
            "message": "Listing Not Found",
            "counter": counter,
        })
  
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "highest_bid": highest_bid,
        "comments": comments,
        "highest_bidder": highest_bidder,
        "comment": CommentForm(),
        "bid": BidForm(),
        "close_btn": close_btn,
        "counter": counter,
        "current_bids": current_bids,
    })


def wishlist(request):
    user = request.user
    listings = []
    counter = 0
    
    if request.method == "POST" and 'remove-btn' in request.POST:
        listing_id = request.POST['listing_id']
        user_wishlist = Wishlist.objects.get(user=User.objects.get(pk=user.id))
        user_wishlist.listings.remove(listing_id)
        
        if len(user_wishlist.listings.all()) == 0:
            Wishlist.objects.get(user=User.objects.get(pk=user.id)).delete()   
        
        return HttpResponseRedirect(reverse('wishlist'))

    try:
        user_wishlist = Wishlist.objects.get(user=User.objects.get(pk=user.id))
    except Wishlist.DoesNotExist:
        return render(request, "auctions/wishlist.html" , {
            "message": "Wishlist empty.",
            "counter": counter
        })

    for listing in user_wishlist.listings.all():
        listings.append(AuctionListing.objects.get(pk=listing.id))
        counter += 1

    return render(request, "auctions/wishlist.html", {
        "listings": listings,
        "counter": counter
    })


def categories(request):
    user = request.user
    counter = 0
    categories = set()
    listings = AuctionListing.objects.filter().all()
    
    for listing in listings:
        categories.add(listing.category)
    
    if user.is_authenticated:
        try:
            user_wishlist = Wishlist.objects.get(user=User.objects.get(pk=user.id))
        except Wishlist.DoesNotExist:
            counter = 0
        else:
            for item in user_wishlist.listings.all():
                item = item
                counter += 1

    if request.method == "POST":
        category = request.POST.get('category')
        related_listings = AuctionListing.objects.filter(category=category).all()
        if len(related_listings) == 0:
            return render(request, "auctions/categories.html", {
            "counter": counter,
            "categories": categories,
            "message": "No Results.",
        })

        return render(request, "auctions/categories.html", {
            "counter": counter,
            "categories": categories,
            "listings": related_listings,
        })


    return render(request, "auctions/categories.html", {
        "counter": counter,
        "categories": categories,
    })


def search(request):
    if request.method == "POST":
        query = request.POST.get('search')
        try:
            int(query)
            try:
                listing = AuctionListing.objects.get(id=query)

                return render(request, "auctions/search.html", {
                    "listing": listing,
                })
            except AuctionListing.DoesNotExist:
                return render(request, "auctions/error.html", {
                    "message": "No Results."
                })
        except ValueError:
            return render(request, "auctions/error.html", {
                "message": "No Match.",
            })
