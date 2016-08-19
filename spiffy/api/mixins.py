
import json

from django.core.paginator import Paginator, InvalidPage
from django.http import HttpResponse, JsonResponse


class JsonRequestMixin(object):

    def dispatch(self, *args, **kwargs):
        if self.request.method == 'POST':
            if 'json' in self.request.META['CONTENT_TYPE']:
                try:
                    data = json.loads(self.request.body)
                    self.post_data = data

                except ValueError as e:
                    kwargs = {
                        'status_code': 400,
                        'message': e.message,
                    }
                    return self._response(**kwargs)

            else:
                kwargs = {
                    'status_code': 415,
                    'message': 'Bad Content-Type',
                }
                return self._response(**kwargs)

        return super(JsonRequestMixin, self).dispatch(*args, **kwargs)


class JsonResponseMixin(object):

    def render_to_response(self, context, **kwargs):
        if isinstance(context, JsonResponse):
            return context

        elif isinstance(context, str):
            return HttpResponse(context, **kwargs)

        else:
            return JsonResponse(context, **kwargs)


class PaginatorMixin(object):
    object_list = []
    paginator = None

    def __init__(self, pagination_count=10):
        self.pagination_count = pagination_count

    def get_context_data(self, **kwargs):
        context = super(PaginatorMixin, self).get_context_data(**kwargs)

        self.paginator = Paginator(self.object_list, self.pagination_count)
        page_num = self.request.GET.get('page', 1)

        try:
            self.page = self.paginator.page(page_num)
        except InvalidPage:
            page_num = 1
            self.page = self.paginator.page(page_num)

        pagination = {
            'count': len(self.page.object_list),
            'total_count': self.paginator.count,
            'page_num': self.page.number,
            'num_pages': self.paginator.num_pages,
        }

        context.update(
            pagination=pagination
        )

        return context
