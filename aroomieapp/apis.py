import json

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404

from oauth2_provider.models import AccessToken

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q

from django.contrib.auth.models import User
from aroomieapp.models import Profile, Advertisement, Rating, Message
from aroomieapp.serializers import UserSerializer, ProfileSerializer, \
    OtherProfileSerializer, AdvertisementSerializer, RatingSerializer, \
    MessageSerializer

###############
# PROFILE
##############

def user_get_profile(request):
    access_token = AccessToken.objects.get(token = request.GET.get("access_token"),
        expires__gt = timezone.now())

    user = access_token.user

    basic = UserSerializer(
        User.objects.filter(id = user.id).last()
    ).data

    profile = ProfileSerializer(
        Profile.objects.filter(user = user).last()
    ).data

    return JsonResponse({"basic": basic, "profile": profile})

"""
    POST params:
        access_token
        dob
        race
        phone
        lifestyle_info
        gender_pref
        race_pref
        budget_pref
        move_in_pref
"""
@csrf_exempt
def user_update_profile(request):

    if request.method == "POST":
        access_token = AccessToken.objects.get(token = request.POST.get("access_token"),
            expires__gt = timezone.now())

        user = access_token.user

        profile = Profile.objects.get(user = user)
        profile.dob = request.POST["dob"]
        profile.race = request.POST["race"]
        profile.phone = request.POST["phone"]
        profile.lifestyle_info = request.POST["lifestyle_info"]
        profile.gender_pref = request.POST["gender_pref"]
        profile.race_pref = request.POST["race_pref"]
        profile.budget_pref = request.POST["budget_pref"]
        profile.move_in_pref = request.POST["move_in_pref"]
        profile.save()

        return JsonResponse({"status": "success"})

def user_get_other_profile(request, user_id):
    basic = UserSerializer(
        User.objects.filter(id = user_id).last()
    ).data

    profile = OtherProfileSerializer(
        Profile.objects.filter(user_id = user_id).last()
    ).data

    return JsonResponse({"basic": basic, "profile": profile})

###############
# ADVERTISEMENT - Trying Class-based Views
###############

"""
    POST params:
        access_token
        rental
        move_in
        deposit
        amenity
        rule
        lat
        lng
        gender_pref
        race_pref
        photo
"""
class AdvertisementList(APIView):
    serializer_class = AdvertisementSerializer
    
    def get(self, request, format=None):
        advertisements = Advertisement.objects.all().order_by('-id')
        serializer = AdvertisementSerializer(advertisements, many=True, context = {"request": request})
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = AdvertisementSerializer(data=request.data)

        if serializer.is_valid():
            access_token = AccessToken.objects.get(token = request.data["access_token"],
                expires__gt = timezone.now())

            user = access_token.user
            serializer.save(created_by=user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdvertisementDetail(APIView):
    def get_object(self, pk):
        try:
            return Advertisement.objects.get(pk=pk)
        except Advertisement.DoesNotExist:
            raise Http404

    def put(self, request, pk, format=None):
        advertisement = self.get_object(pk)
        serializer = AdvertisementSerializer(advertisement, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

###############
# RATING
#############

def user_get_rating(request, user_id):

    ratings = Rating.objects.filter(rated_to = user_id)
    count = ratings.count()

    score = sum(rating.score for rating in ratings) / count
    return JsonResponse({"score": round(score, 0)}) #round off to whole number

"""
    POST params:
        access_token
        score
"""
@csrf_exempt
def user_add_rating(request, user_id):

    if request.method == "POST":
        access_token = AccessToken.objects.get(token = request.POST.get("access_token"),
            expires__gt = timezone.now())

        rated_by = access_token.user
        rated_to = User.objects.filter(id = user_id).last()

        # Check if target has been rated before
        if Rating.objects.filter(rated_to = rated_to, rated_by = rated_by):
            return JsonResponse({"status": "failed", "error": "You have already rated this user before"})

        rating = Rating.objects.create(
            score = request.POST["score"],
            rated_at = timezone.now(),
            rated_by = rated_by,
            rated_to = rated_to
        )

        return JsonResponse({"status": "success"})


###############
# MESSAGE
###############

def user_get_message_list(request):
    access_token = AccessToken.objects.get(token = request.GET.get("access_token"),
        expires__gt = timezone.now())

    user = access_token.user

    message_list = MessageSerializer(
        Message.objects.filter(Q(sent_by = user) | Q(sent_to = user)).order_by('sent_at'),
        many = True
    ).data

    for message in message_list:
        message["sent_by"] = User.objects.filter(id = message["sent_by"]).last().get_full_name()
        message["sent_to"] = User.objects.filter(id = message["sent_to"]).last().get_full_name()

    return JsonResponse({"message_list": message_list})

def user_get_message_thread(request, user_id):
    access_token = AccessToken.objects.get(token = request.GET.get("access_token"),
        expires__gt = timezone.now())

    user = access_token.user
    other_user = User.objects.filter(id = user_id).last()

    message = MessageSerializer(
        Message.objects.filter(Q(sent_by = user, sent_to = other_user) | Q(sent_by = other_user, sent_to = user)).order_by('sent_at'),
        many = True
    ).data

    return JsonResponse({"message_thread": message})

"""
    POST params:
        access_token
        content
"""
@csrf_exempt
def user_send_message(request, user_id):

    if request.method == "POST":
        access_token = AccessToken.objects.get(token = request.POST.get("access_token"),
            expires__gt = timezone.now())

        user = access_token.user
        other_user = User.objects.filter(id = user_id).last()

        Message.objects.create(
            content = request.POST["content"],
            sent_at = timezone.now(),
            sent_by = user,
            sent_to = other_user
        )

        return JsonResponse({"status": "success"})
