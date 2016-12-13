from django.shortcuts import render
from django.conf import settings

# Create your views here.
def home(request):
    return render(request, 'home.html', {
        "BASE_DIR": settings.BASE_DIR,
        "STATICFILES_DIRS": settings.STATICFILES_DIRS
    })
