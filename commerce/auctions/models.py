from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UniqueConstraint

class User(AbstractUser):
    pass

class Category(models.Model):
	category_name = models.CharField(max_length=64)
	category_description = models.CharField(max_length=500)
	
	def __str__(self):
		return self.category_name
		
class Listing(models.Model):
	title = models.CharField(max_length=64)
	description = models.CharField(max_length=500)
	image_link = models.CharField(max_length=64)
	listing_date = models.DateTimeField()
	active = models.BooleanField(default=False)
	allowedit = models.BooleanField(default=True)
	startbid = models.FloatField(default=0)
	user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="UserListings")
	category_id = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="ListingCategory")
	def __str__(self):
		return f"{title} {self.user_id} {self.listing_date}"
		
class ListingBid(models.Model):
	bid_amount = models.IntegerField() 
	bid_datetime = models.DateTimeField()
	user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="UserBid")
	listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="ListingBid")
	def __str__(self):
		return f"{self.user_id} {self.listing} {self.bid_amount} {self.bid_datetime}"
		
class Comment(models.Model):
	comment = models.CharField(max_length=500)
	comment_datetime = models.DateTimeField()
	listing_id = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="ListingComments")
	user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="UserComment")
	
	def __str__(self):
		return f"{self.comment} {self.comment_datetime}"

class Watchlist(models.Model):
	user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="UserWatchlist")
	listing_id = models.ForeignKey(Listing, on_delete=models.CASCADE)
	
	class Meta:
		constraints = [
		UniqueConstraint('user_id', 'listing_id', name='WatchlistComposite'),
	]
