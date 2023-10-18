from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from datetime import datetime
from .models import User, Category, Listing, ListingBid, Comment, Watchlist
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.contrib import messages

defaultimage = "/static/auctions/images/default.png" 
watchcnt=10

def getwatchcount(user):
	if user.is_authenticated:
		return Watchlist.objects.filter(user_id = user).count()
	else:
		return 0
		
def dictfetchall(cursor):

    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def index(request, viewtype='active', categoryid=-1):
	try: 
		title = ""
		userid = "0"
		userauth = False

		if request.user.is_authenticated:
			userauth = True
		cursor = connection.cursor()
		
		if request.user.is_authenticated:
			userid = str(request.user.id)
		
		if viewtype=='add':
			return newlisting(request, 'add')
		if viewtype=='active':
			title = "Active Listings"
			cursor.execute("""select l.id 'id', l.title 'title', l.image_link, l.description, l.listing_date, l.startbid, l.active, max(b.bid_amount) 'bid_amount', count(b.listing_id) 'bid_count', case when w.id is not null then 'true' else 'false' end 'watchlist' 
						from auctions_listing l 
						left join auctions_listingbid b on l.id = b.listing_id
						left join auctions_watchlist w on w.listing_id_id  = l.id and w.user_id_id = %s
						where l.active = true
						group by l.id,b.listing_id, w.id;""" %(userid))		
		elif viewtype=='category':
			category = Category.objects.get(id=categoryid)
			title = f"{category.category_name} Listings"
			cursor.execute("""select l.id 'id', l.title 'title', l.image_link, l.description, l.listing_date, l.startbid, l.active, max(b.bid_amount) 'bid_amount', count(b.listing_id) 'bid_count', case when w.id is not null then 'true' else 'false' end 'watchlist' 
				from auctions_listing l 
				left join auctions_listingbid b on l.id = b.listing_id
				left join auctions_watchlist w on w.listing_id_id  = l.id and w.user_id_id = %s
				inner join auctions_category c on l.category_id_id = c.id
				where l.active = true
				and c.id = %d
				group by l.id,b.listing_id, w.id;""" %(userid, categoryid))	
		else: 
			if request.user.is_authenticated:
				title = "Watchlist"
				cursor.execute("""select l.id 'id', l.title 'title', l.image_link, l.description, l.listing_date, l.startbid, l.active, max(b.bid_amount) 'bid_amount', count(b.listing_id) 'bid_count' 
						from auctions_listing l 
						left join auctions_listingbid b on l.id = b.listing_id 
						inner join auctions_Watchlist w on w.listing_id_id = l.id 
						where w.user_id_id = %s 
						group by l.id,b.listing_id;""" %(userid))		
			else:
				return render(request, "auctions/login.html", {"message": "Login required."})
		listings = dictfetchall(cursor)  
		
		renderdict = {"listings": listings, "userauth":userauth, "title": title, "viewtype":viewtype}
		renderdict['watchcnt']=getwatchcount(request.user)
		return render(request, "auctions/index.html", renderdict)
	except Exception as e:
		messages.error(request, f"An error occured, {e}, please try again")
		return index(request, 'active')		

def login_view(request):
	try:
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
	except Exception as e:
		messages.error(request, f"An error occured, {e}, please try again")
		return index(request, 'active')	

def logout_view(request):
	logout(request)
	return render(request, "auctions/login.html")

def register(request):
	try:
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
	except Exception as e:
		messages.error(request, f"An error occured, {e}, please try again")
		return index(request, 'active')	
		        
@login_required(login_url="/login")
def newlisting(request, formtype, listingid=None):
	try:
		if request.method == "POST":
			if formtype=="add":
				if request.POST["imageurl"].strip() == "":
					imageurl = "/static/auctions/images/default.png" 
				else:
					imageurl = 	request.POST["imageurl"].strip()
				categoryid = int(request.POST["category"])
				category = Category.objects.get(id=categoryid)
				listing = Listing.objects.create(user_id=request.user, title=request.POST["title"], description=request.POST["description"], 
				category_id=category, image_link=imageurl, listing_date=datetime.now(), active=True, startbid=float(request.POST["startbid"]))
				messages.success(request, "New listing posted successfully")
				return HttpResponseRedirect(reverse("index"))
			if formtype=="edit":
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
			categories = Category.objects.all().order_by('category_name').values()
			formlabel = "Edit"
			listing = Listing.objects.get(id=listingid)
			renderdict = { "categories": categories, "formlabel": formlabel, "scontent": listing.description, "title": listing.title, 
			"selectedcategory": listing.category_id, "image": listing.image_link, "formtype": formtype, "listingid":listingid, 
			"startbid":listing.startbid}
			renderdict['watchcnt'] = getwatchcount(request.user)
			return render(request, "auctions/newlisting.html", renderdict)
		else:	
			categories = Category.objects.all().order_by('category_name').values()
			formlabel = "Create"
			renderdict = { "categories": categories, "formlabel": formlabel, "formtype": formtype}
			renderdict['watchcnt'] = getwatchcount(request.user)
			
			return render(request, "auctions/newlisting.html", renderdict)	
	except Exception as e:
		messages.error(request, f"An error occured, {e}, please try again")
		return index(request, 'active')	
		
def viewlisting(request, listingid):
	try:
		listing = Listing.objects.get(id=listingid)
		listingbids = ListingBid.objects.filter(listing = listing).order_by('bid_amount')
		bidcount = listingbids.count()
		bwatchlist = False
		userauth = False
		minbid = 0
		if request.user.is_authenticated:
			userauth = True
			#listinguser = Listing.user_id
			watchlist = Watchlist.objects.filter(listing_id=listing, user_id=request.user)
			for item in watchlist:
				if item.listing_id == listing:
					bwatchlist = True
		if(bidcount > 0):
			lastbid = listingbids.last().bid_amount
			lastbiduser = listingbids.last().user_id
			minbid = lastbid+1
		else:
			lastbid = 0
			lastbiduser = ""
			minbid = listing.startbid
			
		comments = Comment.objects.filter(listing_id = listing)
		renderdict = {"listing": listing, "userauth":userauth, "watchlist": bwatchlist, "minbid": minbid, "listingbids": lastbid, "comments":comments, "bidscount":bidcount, "lastbiduser":lastbiduser}
		renderdict['watchcnt'] = getwatchcount(request.user)
		return render(request, "auctions/viewlisting.html", renderdict)
	except Exception as e:
		messages.error(request, f"An error occured, {e}, please try again")
		return index(request, 'active')	
			
@login_required(login_url="/login")
def bid(request, listingid):
	try:
		if request.method == "POST":	
			listing = Listing.objects.get(id=listingid)
			listbid = ListingBid.objects.create(bid_amount=float(request.POST["txtBid"]), bid_datetime=datetime.now(), listing_id = listingid, user_id=request.user)
			messages.success(request, "Bid posted successfully. This item has been added to your watchlist." )
			return watchlist(request, listingid, 4)
			#return viewlisting(request, listingid) 
		else:
			return viewlisting(request, listingid) 
	except Exception as e:
		messages.error(request, f"An error occured, {e}, please try again")
		return index(request, 'active')	
				
@login_required(login_url="/login")
def comment(request, listingid):
	try:
		if request.method == "POST":	
			listing = Listing.objects.get(id=listingid)
			Comment.objects.create(comment=request.POST["comment"], comment_datetime = datetime.now(), listing_id = listing, user_id = request.user)
			return viewlisting(request, listingid) 
		else:
			return viewlisting(request, listingid) 
	except Exception as e:
		messages.error(request, f"An error occured, {e}, please try again")
		return index(request, 'active')	
				
@login_required(login_url="/login")
def watchlist(request, listingid, remove=0):
	try:
		listing = Listing.objects.get(id=listingid)
		if remove > 0 and remove < 4:
			Watchlist.objects.filter(user_id=request.user, listing_id = listing).delete()
		elif remove == 4 or remove==0:	
			Watchlist.objects.get_or_create(user_id=request.user, listing_id = listing)
		if remove >= 3:
			return viewlisting(request, listingid)
		if remove == 1:
			return index(request, 'watchlist') 	
		else:
			return index(request, 'active')	
	except Exception as e:
		messages.error(request, f"An error occured, {e}, please try again")
		return index(request, 'active')	

def categories(request, categoryid=-1):
	try:
		if categoryid > -1:
			return index(request, "category", categoryid)	
		else:	
			cursor = connection.cursor()
			cursor.execute("""select c.category_name, c.id, count(l.id) count from auctions_category c left join auctions_listing l on l.category_id_id = c.id 
							and l.active=true
							where c.category_name <> '<SELECT>'
							group by l.category_id_id,c.category_name, c.id""")
			categories = dictfetchall(cursor) 
			renderdict= {"categories":categories}
			renderdict['watchcnt'] = getwatchcount(request.user)
			return render(request, "auctions/categories.html",renderdict)			
	except Exception as e:
		messages.error(request, f"An error occured, {e}, please try again")
		return index(request, 'active')
				
def close(request, listingid):
	try:
		if request.method == "POST":
			listing = Listing.objects.get(id=listingid)
			listing.active = False
			listing.save()
		messages.success(request, "Listing closed successfully")	
		return index(request)	
	except Exception as e:
		messages.error(request, f"An error occured, {e}, please try again")
		return index(request)			
	
