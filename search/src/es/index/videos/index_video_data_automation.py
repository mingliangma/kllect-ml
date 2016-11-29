# -*- coding: utf-8 -*-

from datetime import datetime
import templates.index_template as it
import templates.request_template as rt
from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient
from pyelasticsearch import ElasticSearch
from pymongo import MongoClient
import config
import helpers


mongo_client = MongoClient(config.mongodb_uri)
db = mongo_client[config.db]


def _index_video_data(es, write_index):
    i = 0
    batch_size = 500
    article_col = db[config.article_mongo_col]
    batch = []
    for doc in article_col.find().batch_size(batch_size):
        # if doc[mt.attraction_title_field] != 'Toronto Zoo':
        #     continue

        if i % batch_size == 0:
            print 'Processing video batch #%d...' % (i // batch_size)

        batch.append(doc)

        if len(batch) == batch_size:
            try:
                res = helpers.index_video_data_batch(batch, es, write_index)
                if not res[rt.success_field]:
                    print 'Unable to index the %d videos in this batch.' % len(batch)

                if rt.error_field in res and res[rt.error_field]:
                    print res[rt.error_field]

            except Exception, e:
                print 'Unable to index the %d videos in this batch.' % len(batch)
                print e
                print

            batch = []

        i += 1

    if len(batch):
        try:
            res = helpers.index_video_data_batch(batch, es, write_index)
            if not res[rt.success_field]:
                print 'Unable to index the %d videos in this batch.' % len(batch)

            if rt.error_field in res and res[rt.error_field]:
                print res[rt.error_field]
        except Exception, e:
            print 'Unable to index the %d videos in this batch.' % len(batch)
            print e


def index_video_data_automation():
    import json

    client = Elasticsearch(config.es_hosts)

    index_client = IndicesClient(client)

    existing_indices = []

    write_index = '%s_%s' % (config.video_index_prefix,
                             datetime.now().strftime(config.index_datetime_format))
    index_template_mapping = json.dumps(it.index_mapping)

    # This part will remove the "attractions-write" alias from the existing (if there's one) index
    # and add to a new index
    for index_name in index_client.get_alias(index=config.video_index_prefix + '*'):
        existing_indices.append(index_name)

    if len(existing_indices):
        print 'The write alias "%s" exists on the following existing indices:' % config.video_write_index_alias
        print existing_indices

    if index_client.exists_alias(name=config.video_write_index_alias):
        for index_name in index_client.get_alias(name=config.video_write_index_alias):
            index_client.delete_alias(index=index_name, name=config.video_write_index_alias)

    # if client.indices.exists(index):
    #    client.indices.delete(index)

    index_client.create(index=write_index, body=index_template_mapping)
    index_client.put_alias(index=write_index,
                           name=config.video_write_index_alias)

    es = ElasticSearch(urls=['http://%s' % x for x in config.es_hosts],
                       timeout=600)

    _index_video_data(es, write_index)

    print 'Deleting the old indices with the read alias...'
    try:
        if len(existing_indices):
            index_client.delete(index=existing_indices)
    except Exception, e:
        print 'Error deleting old indices.'
        print e.message

    # Move the "attractions-read" alias to the new index just created
    index_client.put_alias(index=config.video_write_index_alias,
                           name=config.video_read_index_alias)


# if __name__ == '__main__':
#     index_video_data_automation()
