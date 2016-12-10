from aroomieapp.models import Profile

def extend_user_profile(backend, user, request, response, *args, **kwargs):
    if backend.name == 'facebook':
        avatar = 'https://graph.facebook.com/%s/picture?type=large' % response['id']
        gender = response['gender']
        print(avatar)

        if not Profile.objects.filter(user_id=user.id):
            Profile.objects.create(user_id=user.id, gender=gender, avatar=avatar)
