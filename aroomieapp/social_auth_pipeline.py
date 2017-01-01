from aroomieapp.models import Profile

def extend_user_profile(backend, user, request, response, *args, **kwargs):
    if backend.name == 'facebook':
        avatar = 'https://graph.facebook.com/%s/picture?type=large' % response['id']
        gender = response['gender']
        age_min = response['age_range']['min'] if response['age_range'].get('min') else 0
        age_max = response['age_range']['max'] if response['age_range'].get('max') else 0

        if not Profile.objects.filter(user_id=user.id):
            Profile.objects.create(user_id=user.id, age_min=age_min, age_max=age_max, gender=gender, avatar=avatar)
