from elasticsearch import Elasticsearch
import config
import templates.es_template as est
import search_parameters as p
from datetime import datetime


# def compose_filters(category):
#     filters = [
#         {
#             "term" : {
#                 est.category_field : category
#             }
#         }
#     ]
#
#     filter = {
#         "and" : filters
#     }
#
#     return filter


def compose_query(keyword, preferences):
    preference_scoring = [
        {
            "boost_factor": 1.0
        }
    ]

    if len(preferences):
        total_weight = sum([x[1] for x in preferences])

        for tag, weight in preferences:
            norm_weight = weight / total_weight * p.PREFERENCE_BOOSTING_FACTOR

            preference_scoring.append({
                "filter": {
                    "term": {
                        est.category_tag_field : tag
                    }
                },
                "weight": norm_weight
            })

    rating_scoring = [
        {
            "field_value_factor": {
                "field": est.popularity_field,
                "modifier": "sqrt"
            }
        }
    ]

    pub_date_scoring = [
        {
            "boost_factor": 0.1
        }
    ]

    if p.ENABLE_DATE_DECAY:
        pub_date_decay = {
            "gauss": {
                est.parse_date_field: {
                    "origin": datetime.now().isoformat(),
                    "offset": p.PUB_DATE_SEARCH_OFFSET,
                    "scale": p.PUB_DATE_SEARCH_ScALE,
                    'decay': p.PUB_DATE_DECAY
                }
            }
        }

        pub_date_scoring.append(pub_date_decay)

    if keyword:
        match_clause = {
            'multi_match' : {
                "query": keyword,
                "operator": "or",
                "fields": [
                    '%s^%s' % (k, v) for (k, v) in p.boosting.items()
                ]
            }
        }
    else:
        match_clause = {
            "match_all" : {}
        }

    query = {
        "function_score" : {
            "query" : {
                "function_score" : {
                    "query" : {
                        "function_score": {
                            "query": match_clause,
                            "functions": rating_scoring,
                            "score_mode": "sum",
                            "boost_mode": "multiply"
                            }
                        },
                    "functions": preference_scoring,
                    "score_mode": "sum",
                    "boost_mode": "sum"
                }
            },
            "functions": pub_date_scoring,
            "score_mode": "max",
            "boost_mode": "multiply"
        }
    }

    return query


def search_videos(keyword, preferences=[], start=0, top_n=p.TOP_N):
    inner_query = {
        "filtered": {
            "query": compose_query(keyword, preferences)
        }
    }

    # if category:
    #     inner_query["filtered"]['filter'] = compose_filters(category)

    query = {
        "from" : start,
        "size" : top_n,
        "query" : inner_query
    }

    # print json.dumps(query, indent=2)

    try:
        es = Elasticsearch(config.es_hosts)

        res = es.search(index=config.video_read_index_alias,
                        body=query)

        total = res['hits']['total']
        results = res['hits']['hits']

        return [r['_source'] for r in results], total
    except Exception, e:
        raise e


# if __name__ == '__main__':
#     preferences = [('smartphones', 0.7),
#                    ('artificial intelligence', 0.2)]
#
#     keyword = 'apple'
#     results, total = search_videos(keyword=keyword,
#                                    preferences=preferences,
#                                    start=0,
#                                    top_n=p.TOP_N)
#
#     for result in results:
#         print {x : result[x] for x in ['video_id', 'title', 'tags', 'category_tag']}

