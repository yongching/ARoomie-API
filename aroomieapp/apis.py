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

import datetime
from dateutil.relativedelta import relativedelta

from django.contrib.auth.models import User
from aroomieapp.models import Profile, Advertisement, Rating, Message
from aroomieapp.serializers import UserSerializer, ProfileSerializer, \
    OtherProfileSerializer, AdvertisementSerializer, RatingSerializer, \
    MessageSerializer

from push_notifications.models import APNSDevice

###############
# APNSDevice
##############

@csrf_exempt
def create_apns_device(request):

    if request.method == "POST":
        access_token = AccessToken.objects.get(token=request.POST.get("access_token"),
            expires__gt = timezone.now())
        user = access_token.user

        if request.POST["device_token"]:
            apns_device = APNSDevice.objects.filter(user=user)
            if len(apns_device) == 0:
                APNSDevice.objects.create(name="device_token", active=True, user=user, registration_id=request.POST["device_token"])
            else:
                apns_device = APNSDevice.objects.get(user=user)
                apns_device.registration_id = request.POST["device_token"]
                apns_device.save()
        return JsonResponse({"status": "success"})

    return JsonResponse({"status": "fail"})

###############
# PROFILE
##############

def user_get_profile(request):
    access_token = AccessToken.objects.get(token=request.GET.get("access_token"),
        expires__gt = timezone.now())

    user = access_token.user

    p = Profile.objects.get(user=user)
    age_min = p.age_min
    age_max = p.age_max

    if age_min != 0 and age_max != 0:
        age_range = str(age_min) + " - " + str(age_max)
    elif age_min == 0 and age_max != 0:
        age_range = "below " + str(age_max)
    elif age_min != 0 and age_max == 0:
        age_range = "above " + str(age_min)
    else:
        age_range == ""

    basic = UserSerializer(
        User.objects.filter(id=user.id).last()
    ).data

    profile = ProfileSerializer(
        Profile.objects.filter(user=user).last()
    ).data

    return JsonResponse({"basic": basic, "profile": profile, "age_range": age_range})

"""
    POST params:
        access_token
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
        access_token = AccessToken.objects.get(token=request.POST.get("access_token"),
            expires__gt = timezone.now())

        user = access_token.user

        profile = Profile.objects.get(user=user)

        if request.POST["race"]:
            profile.race = request.POST["race"]

        if request.POST["phone"]:
            profile.phone = request.POST["phone"]

        if request.POST["lifestyle_info"]:
            profile.lifestyle_info = request.POST["lifestyle_info"]

        if request.POST["gender_pref"]:
            profile.gender_pref = request.POST["gender_pref"]

        if request.POST["race_pref"]:
            profile.race_pref = request.POST["race_pref"]

        if request.POST["budget_pref"]:
            profile.budget_pref = request.POST["budget_pref"]

        if request.POST["move_in_pref"]:
            profile.move_in_pref = request.POST["move_in_pref"]

        profile.save()

        return JsonResponse({"status": "success"})

def user_get_other_profile(request, user_id):
    basic = UserSerializer(
        User.objects.filter(id=user_id).last()
    ).data

    profile = OtherProfileSerializer(
        Profile.objects.filter(user_id=user_id).last()
    ).data

    p = Profile.objects.filter(user_id=user_id).last()
    age_min = p.age_min
    age_max = p.age_max

    if age_min != 0 and age_max != 0:
        age_range = str(age_min) + " - " + str(age_max)
    elif age_min == 0 and age_max != 0:
        age_range = "below " + str(age_max)
    elif age_min != 0 and age_max == 0:
        age_range = "above " + str(age_min)
    else:
        age_range == ""

    return JsonResponse({"basic": basic, "profile": profile, "age_range": age_range})

###############
# ADVERTISEMENT - Trying Class-based Views
###############

class UserAdvertisement(APIView):
    def get(self, request, format=None):

        access_token = AccessToken.objects.get(token=request.GET.get("access_token"),
            expires__gt = timezone.now())

        user = access_token.user

        advertisements = Advertisement.objects.filter(created_by=user)

        serializer = AdvertisementSerializer(advertisements, many=True, context={"request": request})
        return Response(serializer.data)

class AdvertisementList(APIView):
    serializer_class = AdvertisementSerializer

    """
        GET params:
            gender_pref
            race_pref
            budget
            move_in
    """
    def get(self, request, format=None):

        advertisements = Advertisement.objects.all()

        # Request.GET data
        if request.GET["gender_pref"]:
            gender_pref = request.GET["gender_pref"]
            advertisements = advertisements.filter(gender_pref=gender_pref)

        if request.GET["race_pref"]:
            race_pref = request.GET["race_pref"]
            advertisements = advertisements.filter(race_pref=race_pref)

        if request.GET["budget"]:
            budget = request.GET["budget"]
            advertisements = advertisements.filter(rental__lte=budget)

        if request.GET["move_in"]:
            move_in = request.GET["move_in"]

            # Advanced two months move_in date to create search range
            start_date = datetime.datetime.strptime(move_in, "%Y-%m-%d").date()
            end_date = start_date + relativedelta(months=2)
            advertisements = advertisements.filter(move_in__range=(start_date, end_date))

        serializer = AdvertisementSerializer(advertisements, many=True, context={"request": request}).data

        # Get avatar urls
        for advertisement in serializer:
            advertisement["creator_avatar"] = Profile.objects.filter(user=advertisement["created_by"]).last().avatar

        return Response(serializer)

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
    def post(self, request, format=None):
        serializer = AdvertisementSerializer(data=request.data)

        if serializer.is_valid():

            # Save new advertisement
            access_token = AccessToken.objects.get(token=request.data["access_token"],
                expires__gt = timezone.now())
            user = access_token.user
            serializer.save(created_by=user)

            # Send notification for matched users
            profiles = Profile.objects.all()

            if request.POST["gender_pref"]:
                gender_pref = request.POST["gender_pref"]
                profiles = profiles.filter(gender_pref=gender_pref)

            if request.POST["race_pref"]:
                race_pref = request.POST["race_pref"]
                profiles = profiles.filter(race_pref=race_pref)

            if request.POST["rental"]:
                rental = request.POST["rental"]
                profiles = profiles.filter(budget_pref__gte=rental)

            if request.POST["move_in"]:
                move_in = request.POST["move_in"]

                # Advanced two months move_in date to create search range
                start_date = datetime.datetime.strptime(move_in, "%Y-%m-%d").date()
                end_date = start_date + relativedelta(months=2)
                profiles = profiles.filter(move_in_pref__range=(start_date, end_date))

            if len(profiles) > 0:
                for profile in profiles:
                    if APNSDevice.objects.filter(user=profile.user):
                        device = APNSDevice.objects.get(user=profile.user)
                        alert = {
                            "title": "Potential Room Found!",
                            "body": "View the advertisement now.",
                        }
                        device.send_message(alert, badge=0, sound="default", extra={"advertisementId": serializer.data["id"]})
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdvertisementDetail(APIView):
    def get_object(self, pk):
        try:
            return Advertisement.objects.get(pk=pk)
        except Advertisement.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        advertisement = Advertisement.objects.filter(id=pk).last()
        serializer = AdvertisementSerializer(advertisement, context={"request": request}).data

        user = User.objects.filter(id=serializer["created_by"]).last()
        serializer["creator_name"] = user.first_name + " " + user.last_name
        serializer["lifestyle_info"] = Profile.objects.filter(user=user).last().lifestyle_info
        serializer["creator_avatar"] = Profile.objects.filter(user=user).last().avatar

        return Response(serializer)

    def put(self, request, pk, format=None):
        advertisement = self.get_object(pk)
        serializer = AdvertisementSerializer(advertisement, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        advertisement = self.get_object(pk)
        advertisement.delete()
        return JsonResponse({"status": "success"})

###############
# RATING
###############

def user_get_rating(request, user_id):

    ratings = Rating.objects.filter(rated_to=user_id)
    count = ratings.count()
    if count > 0:
        score = sum(rating.score for rating in ratings) / count
        return JsonResponse({"score": round(score, 0)}) #round off to whole number
    else:
        return JsonResponse({"score": 0})

def user_rating_check(request, user_id):
    access_token = AccessToken.objects.get(token=request.GET.get("access_token"),
        expires__gt = timezone.now())

    user = access_token.user
    ratings = Rating.objects.filter(rated_by=user, rated_to=user_id)
    if ratings.count() > 0:
        return JsonResponse({"rated": "true"})
    else:
        return JsonResponse({"rated": "false"})

"""
    POST params:
        access_token
        score
"""
@csrf_exempt
def user_add_rating(request, user_id):

    if request.method == "POST":
        access_token = AccessToken.objects.get(token=request.POST.get("access_token"),
            expires__gt = timezone.now())

        rated_by = access_token.user
        rated_to = User.objects.filter(id=user_id).last()

        # Check if target has been rated before
        if Rating.objects.filter(rated_to=rated_to, rated_by=rated_by):
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
    access_token = AccessToken.objects.get(token=request.GET.get("access_token"),
        expires__gt = timezone.now())

    user = access_token.user

    # TODO: get the unique senders order_by timestamp
    unique_senders = Message.objects.filter(sent_to=user).values('sent_by', 'sent_to').distinct()

    message_list = []
    for id in unique_senders:
        sent_to = id["sent_to"]
        sent_by = id["sent_by"]

        # Get the latest content for each of the messages
        latest = MessageSerializer(
            Message.objects.filter(
                Q(sent_by=sent_to, sent_to=sent_by) |
                Q(sent_by=sent_by, sent_to=sent_to)
            ).order_by('sent_at').last()
        ).data

        # Replace content with last chat and append the message into messsage_list
        message = MessageSerializer(
            Message.objects.filter(sent_to=user, sent_by=sent_by).order_by('sent_at').last()
        ).data
        message["content"] = latest["content"]
        message_list.append(message)

    for message in message_list:
        user = User.objects.filter(id=message["sent_by"]).last()
        message["sent_by_name"] = user.get_full_name()
        message["sender_avatar"] = Profile.objects.filter(user=user).last().avatar

    return JsonResponse({"messages_received": message_list})

def user_get_message_thread(request, user_id):
    access_token = AccessToken.objects.get(token=request.GET.get("access_token"),
        expires__gt = timezone.now())

    user = access_token.user
    other_user = User.objects.filter(id=user_id).last()

    message = MessageSerializer(
        Message.objects.filter(
            Q(sent_by=user, sent_to=other_user) |
            Q(sent_by=other_user, sent_to=user)
        ).order_by('sent_at'),
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
        access_token = AccessToken.objects.get(token=request.POST.get("access_token"),
            expires__gt = timezone.now())

        user = access_token.user
        other_user = User.objects.filter(id=user_id).last()

        Message.objects.create(
            content = request.POST["content"],
            sent_at = timezone.now(),
            sent_by = user,
            sent_to = other_user
        )

        return JsonResponse({"status": "success"})
