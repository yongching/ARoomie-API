from rest_framework import serializers
from django.contrib.auth.models import User
from aroomieapp.models import Profile, Advertisement, Rating, Message

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "email")

class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ("id", "age_min", "age_max", "gender", "race", "phone", "avatar", "lifestyle_info",
            "gender_pref", "race_pref", "budget_pref", "move_in_pref")

class OtherProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ("id", "gender", "race", "phone", "avatar", "lifestyle_info")

class AdvertisementSerializer(serializers.ModelSerializer):
    # photo = serializers.SerializerMethodField()
    #
    # def get_photo(self, advertisement):
    #     request = self.context.get('request')
    #     photo_url = advertisement.photo.url
    #     return request.build_absolute_uri(photo_url)

    class Meta:
        model = Advertisement
        fields = ("id", "place_name", "rental", "move_in", "deposit", "amenity", "rule",
            "lat", "lng", "gender_pref", "race_pref", "photo", "created_by")

        def create(self, validated_data):
            return Advertisement.objects.create(**validated_data)

class RatingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rating
        fields = ("id", "score")

class MessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = ("id", "content", "sent_by", "sent_to")
