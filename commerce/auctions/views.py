from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from datetime import datetime
from .models import User, Category, Listing, ListingBid


def index(request):
    return render(request, "auctions/index.html")


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
        
def newlisting(request, formtype="list"):
	if request.method == "POST":
		print('Add Listing')
		print(request.POST['category'])
		categoryid = int(request.POST["category"])
		category = Category.objects.get(id=categoryid)
		print (f"category: {category.category_name}")
		listing = Listing.objects.create(user_id=request.user, title=request.POST["title"], description=request.POST["description"], 
		category_id=category, image_link=request.POST["imageurl"], listing_date=datetime.now(), active=True)
		
		return HttpResponseRedirect(reverse("index"))
		#pass
	else:
		categories = Category.objects.all()
		formlabel = "Create"
		return render(request, "auctions/newlisting.html", { "categories": categories, "formlabel": formlabel})	
