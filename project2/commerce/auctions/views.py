from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from datetime import datetime
from .models import User, Category, Listing, ListingBid, Comment, Watchlist
from django.contrib.auth.decorators import login_required
from django.db import connection


def dictfetchall(cursor):

    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def index(request, viewtype='active'):
	title = ""
	if request.user.is_authenticated:
		cursor = connection.cursor()
		# convert to int first to prevent any possible userid spoofing sql injection
		userid = str(int(request.user.id))
	#	sSQL = """select l.id 'id', l.title 'title', l.image_link, l.description, l.listing_date, l.startbid, max(b.bid_amount) 'bid_amount', count(b.listing_id) 'bid_count' 
	#			from auctions_listing l 
	#			left join auctions_listingbid b on l.id = b.listing_id 
	#			group by l.id,b.listing_id;"""
		if viewtype=='active':
			sSQL = f"""select l.id 'id', l.title 'title', l.image_link, l.description, l.listing_date, l.startbid, max(b.bid_amount) 'bid_amount', count(b.listing_id) 'bid_count', case when w.id is not null then 'true' else 'false' end 'watchlist' 
						from auctions_listing l 
						left join auctions_listingbid b on l.id = b.listing_id
						left join auctions_watchlist w on w.listing_id_id  = l.id and w.user_id_id = {userid}
						group by l.id,b.listing_id, w.id;"""
			title = "Active Listings"
			cursor.execute(sSQL)		
		else: 
			title = "Watchlist"

			sSQL = (f"""select l.id 'id', l.title 'title', l.image_link, l.description, l.listing_date, l.startbid, max(b.bid_amount) 'bid_amount', count(b.listing_id) 'bid_count' 
					from auctions_listing l 
					left join auctions_listingbid b on l.id = b.listing_id 
					inner join auctions_Watchlist w on w.listing_id_id = l.id 
					where w.user_id_id = {userid} 
					group by l.id,b.listing_id;""")			
			cursor.execute(sSQL)		
			#cursor.execute("select l.id 'id', l.title 'title', l.image_link, l.description, l.listing_date, l.startbid, max(b.bid_amount) 'bid_amount', count(b.listing_id) 'bid_count' from auctions_listing l left join auctions_listingbid b on l.id = b.listing_id group by l.id,b.listing_id;")		
		listings = dictfetchall(cursor)  #Listing.objects.raw("select l.id 'id', l.title 'title', l.image_link, l.startbid, b.bid_amount 'bid_amount', b.bid_count 'bid_count' from auctions_listing l left join (select listing_id, max(bid_amount) 'bid_amount', count(listing_id) 'bid_count' from auctions_listingbid group by listing_id) b on l.id = b.listing_id;")
		return render(request, "auctions/index.html", {"listings": listings, "title": title, "viewtype":viewtype})
	else:
		return render(request, "auctions/login.html", {"message": "Login required."})

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
        
def newlisting(request, formtype, listingid=None):
	print(formtype)
	if request.method == "POST":
		if formtype=="add":
			categoryid = int(request.POST["category"])
			category = Category.objects.get(id=categoryid)
			listing = Listing.objects.create(user_id=request.user, title=request.POST["title"], description=request.POST["description"], 
			category_id=category, image_link=request.POST["imageurl"], listing_date=datetime.now(), active=True, startbid=float(request.POST["startbid"]))
			return HttpResponseRedirect(reverse("index"))
		if formtype=="edit":
			print(listingid)
			listing = Listing.objects.get(id=int(request.POST["listingid"]))
			categoryid = int(request.POST["category"])
			listing.category = Category.objects.get(id=categoryid)
			listing.user_id=request.user
			listing.title = request.POST["title"]
			listing.description=request.POST["description"]
			listing.image_link=request.POST["imageurl"] 
			listing.active=True
			listing.startbid = startbid=float(request.POST["startbid"])
			listing.save()
			return HttpResponseRedirect(reverse("index"))
				
	elif formtype=="edit":
		categories = Category.objects.all()
		formlabel = "Edit"
		listing = Listing.objects.get(id=listingid)
		print(listing.description)
		return render(request, "auctions/newlisting.html", { "categories": categories, "formlabel": formlabel, "scontent": listing.description, 
		"title": listing.title, "selectedcategory": listing.category_id, "image": listing.image_link, "formtype": formtype, "listingid":listingid, "startbid":listing.startbid})	
	else:	
		categories = Category.objects.all()
		formlabel = "Create"
		return render(request, "auctions/newlisting.html", { "categories": categories, "formlabel": formlabel, "formtype": formtype})	

def viewlisting(request, listingid):
	listing = Listing.objects.get(id=listingid)
	listingbids = ListingBid.objects.filter(listing = listing)
	bidcount = listingbids.count()
	if(bidcount > 0):
		lastbid = listingbids.last().bid_amount
		lastbiduser = listingbids.last().user_id
	else:
		lastbid = 0
		lastbiduser = ""
	comments = Comment.objects.filter(listing_id = listing)
	listinguser = Listing.user_id
	#return render(request, "auctions/viewlisting.html", { "categories": categories, "formlabel": formlabel, "scontent": listing.description, 
	#"title": listing.title, "selectedcategory": listing.category_id, "image": listing.image_link, "formtype": formtype, "listingid":listingid, "startbid":listing.startbid,
	#"comments":comments, "listinguser":listinguser})	
	return render(request, "auctions/viewlisting.html", {"listing": listing, "listingbids": lastbid, "comments":comments, "bidscount":bidcount, "lastbiduser":lastbiduser})
	
@login_required
def bid(request, listingid):
	if request.method == "POST":	
		listing = Listing.objects.get(id=listingid)
		listbid = ListingBid.objects.create(bid_amount=request.POST["txtBid"], bid_datetime=datetime.now(), listing_id = listingid, user_id=request.user)
		return viewlisting(request, listingid) 
	else:
		return viewlisting(request, listingid) 
		
@login_required
def comment(request, listingid):
	if request.method == "POST":	
		listing = Listing.objects.get(id=listingid)
		Comment.objects.create(comment=request.POST["comment"], comment_datetime = datetime.now(), listing_id = listing, user_id = request.user)
		return viewlisting(request, listingid) 
	else:
		return viewlisting(request, listingid) 
		
@login_required
def watchlist(request, listingid, remove=0):
		listing = Listing.objects.get(id=listingid)
		if remove > 0:
			Watchlist.objects.filter(user_id=request.user, listing_id = listing).delete()
		else:	
			Watchlist.objects.create(user_id=request.user, listing_id = listing)
		if remove == 1:
			return index(request, 'watchlist') 	
		else:
			return index(request, 'active')	
	
