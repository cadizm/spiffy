
from django.conf import settings
from django.core.cache import cache
from django.views.generic.base import TemplateView

from profile.models import Profile

import logging
logger = logging.getLogger('spiffy.' + __name__)


class RandomProfileView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        return super(RandomProfileView, self).get_context_data(**kwargs)
