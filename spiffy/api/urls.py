
from django.conf.urls import url

from .views import (RandomProfileView, ProfileView, ProfilesView,
    CreateProfileView,
    )


urlpatterns = [
    url(r'^profiles/$', ProfilesView.as_view(), name='api_profiles'),
    url(r'^profile/$', RandomProfileView.as_view(), name='api_random_profile'),
    url(r'^profile/create/$', CreateProfileView.as_view(), name='api_create_profile'),
    url(r'^profile/(?P<profile_id>[0-9a-zA-Z+\-]+)/$', ProfileView.as_view(), name='api_profile'),  # keep me last
]
