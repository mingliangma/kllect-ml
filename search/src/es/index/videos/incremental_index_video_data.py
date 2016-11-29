# -*- coding: utf-8 -*-

import templates.mongo_template as mt
import templates.request_template as rt
from pyelasticsearch import ElasticSearch

import config
import helpers


def index_videos(new_videos):
    try:
        es = ElasticSearch(urls=['http://%s' % x for x in config.es_hosts],
                           timeout=600)

        batch_size = 500
        i = 0

        batch_responses = []
        while i < len(new_videos):
            batch = new_videos[i : i + batch_size]
            input_ids = [str(x[mt.id_field]) if mt.id_field in x else None for x in new_videos[i: i + batch_size]]
            batch_response = {
                rt.batch_id_subfield: (i // batch_size),
                rt.input_ids_subfield: input_ids
            }

            try:
                if config.debug:
                    print 'Indexing batch %d...' % (i // batch_size)

                res = helpers.index_video_data_batch(batch, es, config.video_write_index_alias)

                for k, v in res.items():
                    batch_response[k] = v

                batch_responses.append(batch_response)
            except Exception, e:
                batch_response[rt.error_field] = e.message

                batch_responses.append(batch_response)

            i += batch_size

        return {
            rt.success_field : True,
            rt.batch_responses_field : batch_responses,
            rt.total_skips_field : sum([len(x[rt.skipped_ids_field]) for x in batch_responses])
        }
    except Exception, e:
        return {
            rt.success_field : False,
            rt.error_field : e.message
        }


def delete_videos(old_videos):
    try:
        es = ElasticSearch(urls=['http://%s' % x for x in config.es_hosts],
                           timeout=600)

        batch_size = 500
        i = 0

        batch_responses = []
        while i < len(old_videos):
            input_ids = [str(x[mt.id_field]) if mt.id_field in x else None for x in old_videos[i: i + batch_size]]
            batch_response = {
                rt.batch_id_subfield: (i // batch_size),
                rt.input_ids_subfield: input_ids
            }

            try:
                if config.debug:
                    print 'Indexing batch %d...' % (i // batch_size)

                res = helpers.remove_video_data_batch(input_ids, es, config.video_write_index_alias)

                for k, v in res.items():
                    batch_response[k] = v

                batch_responses.append(batch_response)
            except Exception, e:
                batch_response[rt.error_field] = e.message

                batch_responses.append(batch_response)

            i += batch_size

        return {
            rt.success_field : True,
            rt.batch_responses_field : batch_responses,
            rt.total_successes_field : sum([len(x[rt.successes_field]) for x in batch_responses]),
            rt.total_fails_field : sum([len(x[rt.fails_field]) for x in batch_responses])
        }
    except Exception, e:
        return {
            rt.success_field : False,
            rt.error_field : e.message
        }


# if __name__ == '__main__':
#     from pymongo import MongoClient
#
#     mongo_client = MongoClient(config.mongodb_uri)
#     db = mongo_client[config.db]
#     es = ElasticSearch(urls=['http://%s' % x for x in config.es_hosts],
#                        timeout=600)
#     batch = []
#     i = 0
#     batch_size = 500
#
#     for doc in db[config.article_mongo_col].find().batch_size(batch_size=batch_size):
#         batch.append(doc)
#         if len(batch) == batch_size:
#             res = index_videos(batch)
#             print res
#             print {x : res[x] for x in res if x not in [rt.batch_responses_field]}
#
#             break
#
#         i += 1
