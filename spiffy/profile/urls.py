
from django.conf.urls import url

from .views import RandomProfileView


urlpatterns = [
    url(r'^profile/$', RandomProfileView.as_view(), name='profile'),
]
