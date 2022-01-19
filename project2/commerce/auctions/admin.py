from django.contrib import admin

from auctions.models import *

# Register your models here.
class AuctionAdmin(admin.ModelAdmin):
    fields = ['name', 'description', 'feature1', 'feature2', 'feature3', 'feature4', 'feature5', 'category', 'price', 'image', 'user', 'timestamp', 'is_active']
    list_display = ("id_name", "category", "price_dollars", "owner", "image", 'is_active', "timestamp")

    def price_dollars(self, obj):
        return "$%s" % obj.price if obj.price else ""
    def owner(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    def id_name(self, obj):
        return f"{obj.id}.  {obj.name}"
   


class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name","last_name", "username", "email", "last_login", "is_superuser", "is_staff", "is_active", "date_joined")


class BidAdmin(admin.ModelAdmin):
    fields = ['user', 'listing','amount', 'timestamp']
    list_display = ("bidder", "listing_id", "amount_dollars", "timestamp")

    def amount_dollars(self, obj):
        return "$%s" % obj.amount if obj.amount else ""
    def bidder(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    def listing_id(self, obj):
        return f"{obj.listing.id}"


class CommentAdmin(admin.ModelAdmin):
    fields = ['user', 'listing', 'content', 'timestamp']
    list_display = ("commenter", "listid", "content", "timestamp")

    def commenter(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    def listid(self, obj):
        return f"{obj.listing.id}"


class ImageAdmin(admin.ModelAdmin):
    fields = [ 'title', 'image']
    list_display = ("id_title", "image")

    def id_title(self, obj):
        return f"{obj.id}.  {obj.title}"   


class WishlistAdmin(admin.ModelAdmin):
    fields = ['user', 'listings']
    filter_horizontal = ("listings",)
    list_display = ("user_id", "listing_count") 

    def user_id(self, obj):
        return f"{obj.user.id} {obj.user.first_name} {obj.user.last_name}"
    def listing_count(self, obj):
        count = 0
        for listing in obj.listings.all():
            count += 1
        return count



admin.site.register(User, UserAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(AuctionListing, AuctionAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(Wishlist, WishlistAdmin)