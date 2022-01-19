from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.fields.related import ManyToManyField



categories = (('Home','Home'), ('Fashion','Fashion'), ('Beauty','Beauty'), ('Comics','Comics'), ('Education','Education'), ('Food/Beverage','Food/Beverage'), ('Technology','Technology'), ('Art','Art'), ('Pets','Pets'), ('Other','Other'))


class User(AbstractUser):
    pass

    def __str__(self):
        return f"{self.id} {self.first_name} {self.last_name} {self.username} {self.email} {self.last_login} {self.is_superuser} {self.is_staff} {self.is_active} {self.date_joined} {self.groups} {self.user_permissions}"


class Image(models.Model):
    title = models.CharField(max_length=64, null=True, blank=True)
    image = models.ImageField(default='image', upload_to='commerce/auctions/static/auctions/uploads/')


    def __str__(self):
        return f"{self.title} {self.image}"


class AuctionListing(models.Model):
    name  = models.CharField(max_length=64)
    description = models.TextField(max_length=1000)
    feature1 = models.CharField(max_length=1000, null=True, blank=True)
    feature2 = models.CharField(max_length=1000, null=True, blank=True)
    feature3 = models.CharField(max_length=1000, null=True, blank=True)
    feature4 = models.CharField(max_length=1000, null=True, blank=True)
    feature5 = models.CharField(max_length=1000, null=True, blank=True)
    category = models.CharField(max_length=64 ,choices=categories, default='')
    price = models.PositiveIntegerField()
    image = models.ForeignKey(Image, on_delete=models.SET_NULL , null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    timestamp = models.DateTimeField()


    def __str__(self):
        return f"{self.id}{self.name} {self.description} {self.feature1} {self.feature2} {self.feature3} {self.feature4} {self.feature5} {self.category} {self.price} {self.timestamp} {self.image} {self.is_active}"
    
    

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, null=True, default='')
    content = models.TextField()
    timestamp = models.DateTimeField()

    def __str__(self):
        return f"{self.user} {self.listing} {self.content} {self.timestamp}"



class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, null=True, default='')
    amount = models.PositiveIntegerField()
    timestamp = models.DateTimeField()

    def __str__(self):
        return f"{self.user} {self.listing} {self.amount} {self.timestamp}"



class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listings = models.ManyToManyField(AuctionListing)

    def __str__(self):
        return f"{self.user} {self.listings}"