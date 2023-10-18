from django.contrib import admin
from .models import Listing, ListingBid, Comment, Watchlist, Category

# Register your models here.
admin.site.register(Listing)
admin.site.register(ListingBid)
admin.site.register(Comment)
admin.site.register(Watchlist)
admin.site.register(Category)
