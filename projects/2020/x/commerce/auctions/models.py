from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    category_name = models.CharField(max_length=24)
    
    def __str__(self):
        return self.category_name
    
class Bid(models.Model):
    bid = models.FloatField(default=0)
    lister = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="bid_lister")

    def __str__(self):
        return str(self.bid)

class Listing(models.Model):
    title = models.CharField(max_length=30)
    description = models.CharField(max_length=300)
    price = models.ForeignKey(Bid, on_delete=models.CASCADE, blank=True, null=True, related_name="bid_price")
    image_url = models.CharField(max_length=1000)
    active = models.BooleanField(default=True)
    lister = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="user")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True, related_name="category")
    watchlist = models.ManyToManyField(User, blank=True, null=True, related_name="wachlist_listing")

    def __str__(self):
        return self.title
    
class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="author")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, blank=True, null=True, related_name="listing")
    comment = models.CharField(max_length=300)

    def __str__(self):
        return f"{self.author}'s comment on {self.listing}:"
    