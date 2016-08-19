from __future__ import unicode_literals

import sys
import random
import time

from django.db import models
from django.conf import settings

from elasticsearch import Elasticsearch, NotFoundError, ElasticsearchException
_es = Elasticsearch(**settings.ELASTICSEARCH_CONFIG)

import logging
logger = logging.getLogger('spiffy.' + __name__)


class ProfileManager(models.Manager):

    def all(self, **kwargs):
        # this is not how we really want to do pagination
        # https://www.elastic.co/guide/en/elasticsearch/guide/current/pagination.html
        # https://www.elastic.co/guide/en/elasticsearch/reference/current/search-request-from-size.html
        try:
            count = _es.count(index='spiffy_profile')['count']
            return _es.search(index='spiffy_profile', from_=0, size=count)['hits']['hits']

        except ElasticsearchException as e:
            logger.error('elasticsearch exception', exc_info=sys.exc_info())

    def get(self, **kwargs):
        index = 'spiffy_profile'
        try:
            return _es.get(index=index,  id=kwargs.get('pk'))

        except NotFoundError as e:
            e.message = "Profile not found: %s" % kwargs.get('pk')
            raise Profile.DoesNotExist(e.message)

        except ElasticsearchException as e:
            logger.error('elasticsearch exception', exc_info=sys.exc_info())

    def get_random_profile(self, **kwargs):
        index = 'spiffy_profile'
        query = {
            'query': {
                'function_score': {
                    'functions': [
                        { 'random_score': {'seed': int(time.time())} }
                    ]
                }
            },
            'size': 1,
        }

        return self._query_es(index, query, first=True)

    def create(self, **kwargs):
        try:
            return _es.create(index='spiffy_profile', doc_type='profile_type', body=kwargs)

        except (IndexError, ElasticsearchException) as e:
            logger.error('elasticsearch exception', exc_info=sys.exc_info())

    def _query_es(self, index, query, first=False):
        try:
            res = _es.search(index=index, body=query)
            if first:
                return res['hits']['hits'][0]
            return res['hits']['hits']

        except IndexError:
            pass  # No hits

        except ElasticsearchException as e:
            logger.error('elasticsearch exception for query: %s', query, exc_info=sys.exc_info())


class Profile(models.Model):
    objects = ProfileManager()

    name = models.CharField(max_length=128)
    bio = models.TextField()
    pic = models.URLField()

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def to_dict(self):
        return {k: str(v) for k,v in self.__dict__.items()}
