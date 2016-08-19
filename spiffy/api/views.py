
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic.base import View
from django.views.decorators.csrf import csrf_exempt

from api.mixins import JsonRequestMixin, JsonResponseMixin, PaginatorMixin
from profile.models import Profile

import logging
logger = logging.getLogger('spiffy.' + __name__)


class JsonView(JsonResponseMixin, View):
    status_code = 200

    def get_context_data(self, **kwargs):
        return kwargs if kwargs else {}

    def get(self, *args, **kwargs):
        return self._response(*args, **kwargs)

    def post(self, *args, **kwargs):
        return self._response(*args, **kwargs)

    def put(self, *args, **kwargs):
        return self._response(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return self._response(*args, **kwargs)

    def _response(self, *args, **kwargs):
        headers = kwargs.pop('headers', {})

        if 'context' in kwargs:
            context = kwargs.get('context', {})
        else:
            context = self.get_context_data(**kwargs)

        status_code = context.get('status_code', self.status_code)
        response = self.render_to_response(context, status=status_code)

        for k,v in headers.items():
            response[k] = v

        return response


class RandomProfileView(JsonView):

    def get_context_data(self, **kwargs):
        context = super(RandomProfileView, self).get_context_data(**kwargs)

        profile = Profile.objects.get_random_profile()

        context.update(
            profile=profile,
        )

        return context


class ProfilesView(PaginatorMixin, JsonView):

    @method_decorator(cache_page(settings.ALL_PROFILES_PAGE_CACHE_SECONDS))
    def dispatch(self, *args, **kwargs):

        logger.debug('Caching %s' % self)

        return super(ProfilesView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        # set object_list before calling superclass
        self.object_list = Profile.objects.all() or []
        context = super(ProfilesView, self).get_context_data(**kwargs)

        context.update(
            profiles=self.object_list,
        )

        return context


class ProfileView(JsonView):

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)

        try:
            profile = Profile.objects.get(pk=kwargs['profile_id'])

        except Profile.DoesNotExist as e:
            kwargs = {
                'status_code': 404,
                'message': e.message,
            }
            return super(ProfileView, self).get_context_data(**kwargs)

        context.update(
            profile=profile,
        )

        return context


class CreateProfileView(JsonRequestMixin, JsonView):

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(CreateProfileView, self).dispatch(*args, **kwargs)

    def get(self, *args, **kwargs):
        kwargs = {
            'status_code': 405,
            'message': 'Method Not Allowed',
            'headers': {
                'Allow': 'POST',
            }
        }

        return super(CreateProfileView, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        fields = ('name', 'bio', 'pic')
        data = {k: self.post_data.get(k) for k in fields}

        try:
            profile = Profile.objects.create(**data)
            profile_id = profile.get('_id', None)

            context = {
                'status_code': 201,
                'message': 'Created',
                'profile_id': profile_id,
            }

        except Exception as e:
            logger.exception(e.message)
            context = {
                'status_code': 500,
                'message': e.message,
            }

        return self._response(**context)
