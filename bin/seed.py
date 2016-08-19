
import sys

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'spiffy.settings'

from datetime import datetime
from pprint import pprint
import time

from django.conf import settings

from elasticsearch import Elasticsearch
from faker import Faker
import requests


GIPHY_BASE_URL = 'http://api.giphy.com'
GIPHY_TRENDING_PATH = '/v1/gifs/trending'
GIPHY_API_KEY = 'dc6zaTOxFJmzC'


def get_giphy_trending(offset=0):
    url = "%s%s" % (GIPHY_BASE_URL, GIPHY_TRENDING_PATH)
    params = {
        'api_key': GIPHY_API_KEY,
        'offset': offset,
    }

    res = requests.get(url, params=params)
    print "Queried: %s" % res.request.url

    if not res.ok:
        raise Exception('%s for request: %s' % (res.reason, res.request.url))

    return res.json()['data']


def init_es():
    global _es
    if not _es:
        print "Using config:"
        pprint(settings.ELASTICSEARCH_CONFIG)
        _es = Elasticsearch(**settings.ELASTICSEARCH_CONFIG)
    return _es


def bulk_index(index_name, index_type):
    from elasticsearch.helpers import bulk

    _create_index(index_name, index_type)

    print 'Bulk indexing...'
    sys.stdout.flush()
    bulk(client=_es, actions=_actions(index_name, index_type))
    print 'Done'
    pprint(_es.count(index=index_name))


def update_alias(index_name, alias):
    print 'Updating alias'

    # an alias cannot have the same name as an index
    assert alias != index_name

    # if alias doesn't exist:
    if not _es.indices.exists_alias(name=alias):
        # can't create alias with the name of an existing index
        if _es.indices.exists(alias):
            print "Index with alias: %s already exists, deleting" % alias
            _es.indices.delete(index=alias)

        print "Alias doesn't exist, creating"
        _es.indices.put_alias(index=index_name, name=alias)

    else:
        print "Flipping alias"
        body = {
            'actions' : [
                { 'remove' : { 'index' : '%s*' % index_name, 'alias' : index_name } },
                { 'add' : { 'index' : index_name, 'alias' : alias } }
            ]
        }
        _es.indices.update_aliases(body=body)


def close_old_indices(index_name):
    indices = _es.indices.get(index='%s*' % index_name, expand_wildcards='open')

    # sort by descending creation date
    if indices:
        key = lambda x: x[1]['settings']['index']['creation_date']
        indices = sorted(indices.items(), key=key, reverse=True)

        print 'Current index: %s' % indices[0][0]

        for index in indices[1:]:
            index_name = index[0]
            print 'Closing and deleting index %s' % index_name
            _es.indices.close(index=index_name)
            _es.indices.delete(index=index_name)


def _create_index(name, _type):
    body = {
        'mappings': {
            _type: {
                'properties': {
                    'name': { 'type': 'string' },
                    'bio': { 'type': 'string' },
                    'pic': { 'type': 'string' },
                }
            }
        }
    }

    if _es.indices.exists(name):
        print "Index: %s already exists, deleting" % name
        _es.indices.delete(index=name)

    print "Creating index: %s" % name
    _es.indices.create(name, body=body)


def _actions(index_name, index_type):
    """
    Return generator of actions for elasticsearch bulk indexing
    """
    _faker = Faker()

    mapping = {
        'name': str,
        'bio': str,
        'pic': str,
    }

    offset = 0
    for i in range(4):
        trending = get_giphy_trending(offset=offset)
        for t in trending:
            doc = dict(
                name=_faker.name(),
                bio=_faker.paragraph(),
                pic=t['images']['downsized_medium']['url'],
                _index=index_name,
                _type=index_type,
                _op_type='index',
                )
            yield {k: mapping[k](v) if k in mapping else v for k,v in doc.items()}

        offset += len(trending)

        print "Sleeping"
        time.sleep(10)


if __name__ == '__main__':
    global _es; _es = None

    timestamp = '{:%Y%m%d%H%M%S}'.format(datetime.now())
    alias = 'spiffy_profile'
    index_name = '%s_%s' % (alias, timestamp)
    index_type = 'profile_type'

    init_es()
    bulk_index(index_name, index_type)
    update_alias(index_name, alias)
    close_old_indices('%s*' % alias)
