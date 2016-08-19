
from django.conf.urls import url, include


urlpatterns = [
    url(r'^', include('profile.urls')),
    url(r'^api/', include('api.urls')),
]
