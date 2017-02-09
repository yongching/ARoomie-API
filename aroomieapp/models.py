from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from aroomieapp.constants import *

# Create your models here.
class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    age_min = models.IntegerField(blank=True, null=True)
    age_max = models.IntegerField(blank=True, null=True)
    gender = models.CharField(max_length=6)
    race = models.IntegerField(choices=RACE_CHOICES, blank=True, null=True)
    phone = models.CharField(max_length=10, blank=True) #Consider +60 as default
    avatar = models.CharField(max_length=500)
    lifestyle_info = models.CharField(max_length=500, blank=True)
    gender_pref = models.IntegerField(choices=GENDER_CHOICES, blank=True, null=True)
    race_pref = models.IntegerField(choices=RACE_CHOICES, blank=True, null=True)
    budget_pref = models.IntegerField(default=0)
    move_in_pref = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.user.get_full_name()

class Advertisement(models.Model):

    place_name = models.CharField(max_length=500, blank=True)
    rental = models.IntegerField(default=0)
    move_in = models.DateField()
    deposit = models.IntegerField(default=0)
    amenity = models.CharField(max_length=500, blank=True)
    rule = models.CharField(max_length=500, blank=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    lng = models.DecimalField(max_digits=9, decimal_places=6)
    gender_pref = models.IntegerField(choices=GENDER_CHOICES)
    race_pref = models.IntegerField(choices=RACE_CHOICES)
    #photo = models.ImageField(upload_to='advertisement/', blank=False)
    photo = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, null=True, blank=True, related_name='advertisement')

    def __str__(self):
        return self.created_by.get_full_name()

class Rating(models.Model):
    score = models.IntegerField()
    rated_at = models.DateTimeField(default=timezone.now)
    rated_by = models.ForeignKey(User, null=True, blank=True, related_name='rater')
    rated_to = models.ForeignKey(User, null=True, blank=True, related_name='target')

    def __str__(self):
        return self.rated_to.get_full_name()

class Message(models.Model):
    content = models.CharField(max_length=500)
    sent_at = models.DateTimeField(default=timezone.now)
    sent_by = models.ForeignKey(User, null=True, blank=True, related_name='sender')
    sent_to = models.ForeignKey(User, null=True, blank=True, related_name='recipient')

    def __str__(self):
        return self.sent_to.get_full_name()
