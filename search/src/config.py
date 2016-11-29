import os

EXPOSED_PORT = 5011

DEBUG_FLAG = 'DEBUG'
if DEBUG_FLAG in os.environ:
    debug = os.environ[DEBUG_FLAG] == 'true'
else:
    debug = True

ENV_FLAG = 'environment'

environment = 'dev'

if ENV_FLAG in os.environ:
    if os.environ[ENV_FLAG] in ['dev', 'prd']:
        environment = os.environ[ENV_FLAG]

if environment == 'dev':
    es_hosts = ['ec2-54-175-64-170.compute-1.amazonaws.com:9200',
                'ec2-54-210-216-186.compute-1.amazonaws.com:9200',
                'ec2-54-175-64-170.compute-1.amazonaws.com:9200']
    mongodb_host = 'ds033046.mlab.com'
    mongodb_port = 33046
    username = 'kllect_app'
    password = 'JM9MQWh9xwRbeKD'
    db = 'tagged-dev'

    mongodb_uri = "mongodb://%s:%s@%s:%s/%s?authMechanism=SCRAM-SHA-1" % (username,
                                                                          password,
                                                                          mongodb_host,
                                                                          mongodb_port,
                                                                          db)
elif environment == 'prd':
    es_hosts = ['ec2-54-175-64-170.compute-1.amazonaws.com:9200',
                'ec2-54-210-216-186.compute-1.amazonaws.com:9200',
                'ec2-54-175-64-170.compute-1.amazonaws.com:9200']

    mongodb_host = 'ds033046.mlab.com'
    mongodb_port = 33046
    username = 'kllect_app'
    password = 'JM9MQWh9xwRbeKD'
    db = 'tagged-dev'

    mongodb_uri = "mongodb://%s:%s@%s:%s/%s?authMechanism=SCRAM-SHA-1" % (username,
                                                                          password,
                                                                          mongodb_host,
                                                                          mongodb_port,
                                                                          db)

video_index_prefix = 'videos'
video_doc_type = 'video'
index_datetime_format = '%Y-%m-%d_%H-%M-%S'
video_read_index_alias = 'videos-read'
video_write_index_alias = 'videos-write'

article_mongo_col = 'article'
