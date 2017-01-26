"""aroomie URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from aroomieapp import views, apis

# To use images uploaded, we need this
from django.conf.urls.static import static
from django.conf import settings

from aroomieapp.apis import UserAdvertisement, AdvertisementList, AdvertisementDetail

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.home, name='home'),

    # FACEBOOK
    url(r'^api/social/', include('rest_framework_social_oauth2.urls')),

    # USER
    url(r'^api/user/profile/$', apis.user_get_profile),
    url(r'^api/user/profile/edit/$', apis.user_update_profile),
    url(r'^api/user/profile/other/(?P<user_id>\d+)/$', apis.user_get_other_profile),

    # ADVERTISEMENT
    url(r'^api/advertisements/self/$', UserAdvertisement.as_view()),
    url(r'^api/advertisements/$', AdvertisementList.as_view()),
    url(r'^api/advertisement/add/$', AdvertisementList.as_view()),
    url(r'^api/advertisement/(?P<pk>[0-9]+)/$', AdvertisementDetail.as_view()),
    url(r'^api/advertisement/edit/(?P<pk>[0-9]+)/$', AdvertisementDetail.as_view()),
    url(r'^api/advertisement/delete/(?P<pk>[0-9]+)/$', AdvertisementDetail.as_view()),

    # RATING
    url(r'^api/rating/(?P<user_id>\d+)/$', apis.user_get_rating),
    url(r'^api/rating/add/(?P<user_id>\d+)/$', apis.user_add_rating),
    url(r'^api/rating/check/(?P<user_id>\d+)/$', apis.user_rating_check),

    # MESSAGE
    url(r'^api/messages/$', apis.user_get_message_list),
    url(r'^api/message/(?P<user_id>\d+)/$', apis.user_get_message_thread),
    url(r'^api/message/send/(?P<user_id>\d+)/$', apis.user_send_message),

    # NOTIFICATION
    url(r'^api/device/apns/$', apis.create_apns_device),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
