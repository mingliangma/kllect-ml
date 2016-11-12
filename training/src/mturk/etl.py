import pyodbc
import src.paths as paths
import src.config as config
import os.path
import csv
import collections
from pymongo import MongoClient
import src.template as template
from bson import ObjectId
import src.labels as taxonomy
from dateutil import parser
from datetime import datetime


batch_id = 1
batch_create_dttm = '2016-07-15'
batch_category = 'Technology'
num_chunks = 5
questions_per_hit = 3


def _output_batch_to_data_table(batch, cursor):
    if len(batch):
        print 'Inserting %d rows into table %s...' % (len(batch), config.input_data_sql_table)

        #print batch[0]
        #print len(batch[0])

        cursor.executemany('''
        INSERT INTO %s
              VALUES (%s)
        ''' % (config.input_data_sql_table,
               ','.join(['?'] * len(batch[0]))),
                           batch)

        cursor.commit()


def input_data_etl():
    cnn = pyodbc.connect(config.sql_cnn_str)
    cursor = cnn.cursor()

    # print 'Truncating original data...'
    # cursor.execute('TRUNCATE TABLE %s' % config.input_data_sql_table)
    # cursor.connection.commit()

    batch = []
    batch_size = 1000
    input_id = 0

    for chunk_num in xrange(num_chunks):
        input_filename = os.path.join(paths.MTURK_DATA_SUBDIR, 'batch_%d' % batch_id,
                                      'data_%d%s' % (chunk_num, paths.MTURK_INPUT_FILENAME_SUFFIX))

        with open(input_filename) as csvfile:
            reader = csv.reader(csvfile, delimiter='\t', quoting=csv.QUOTE_ALL)

            i = 0
            for row in reader:
                if i == 0:
                    i += 1
                    continue

                num_columns = len(row)
                num_columns_per_question = num_columns / questions_per_hit
                for q_id in xrange(questions_per_hit):
                    batch.append([batch_id, input_id, q_id] + \
                                 row[q_id * num_columns_per_question : (q_id + 1) * num_columns_per_question] + \
                                 [batch_create_dttm])
                input_id += 1

            if len(batch) >= batch_size:
                _output_batch_to_data_table(batch, cursor)
                batch = []

    if len(batch):
        _output_batch_to_data_table(batch, cursor)

    cursor.close()


def sample_data_etl():
    batch_subdir = os.path.join(paths.MTURK_DATA_SUBDIR, 'batch_%d' % batch_id)
    sample_id_fname = os.path.join(batch_subdir, paths.MTURL_SAMPLES_FILENAME)

    labelled_samples = []

    for line in open(sample_id_fname).readlines()[1 : ]:
        line = line.strip()

        if line != '':
            fields = line.split('\t')
            sample_id = fields[0]
            is_labelled = fields[1]

            if is_labelled == 'True':
                labelled_samples.append(ObjectId(sample_id))

    print '%d labelled samples.' % len(labelled_samples)

    uri = "mongodb://%s:%s@%s:%s/%s?authMechanism=SCRAM-SHA-1" % (config.username,
                                                                  config.password,
                                                                  config.mongodb_host,
                                                                  config.mongodb_port,
                                                                  config.db)

    mongo_client = MongoClient(uri)
    ml_label_col = mongo_client[config.db][config.col]

    i = 0
    batch_size = 100
    result = []

    target_labels = {x.lower() : x for x in taxonomy.inv_labels[batch_category]}
    target_labels['wearable technology'] = 'Wearable Tech'
    target_labels['virtual reality'] = 'Virtual Reality and Augmented Reality'
    target_labels['driverless car'] = 'Driverless Cars'

    unmatches = set()
    matches = set()
    while i < len(labelled_samples):
        sub_sample_ids = labelled_samples[i : i + batch_size]

        for doc in ml_label_col.find({template.id_field : {'$in' : sub_sample_ids}}):
            sample_id = str(doc[template.id_field])
            #print sample_id
            labels = doc[template.ml_label_field]

            for label in labels.split(','):
                label = label.strip().lower()
                if label not in target_labels:
                    unmatches.add(sample_id)
                    #print label
                    continue

                matches.add(sample_id)
                result.append((batch_id, sample_id, batch_category, target_labels[label], batch_create_dttm))

        i += batch_size

    invalid_samples = unmatches.difference(matches)
    print 'Invalid samples: %d' % len(invalid_samples)
    for sample_id in invalid_samples:
        print sample_id
        doc = ml_label_col.find_one({template.id_field: ObjectId(sample_id)})
        print doc[template.ml_label_field]

    #return

    cnn = pyodbc.connect(config.sql_cnn_str)
    cursor = cnn.cursor()

    cursor.execute('DELETE FROM %s WHERE batch_id=?' % config.sample_labels_sql_table, batch_id)
    cnn.commit()

    i = 0
    while i < len(result):
        print 'Transferring data group #%d...' % (i // batch_size)
        sub_result = result[i : i + batch_size]
        cursor.executemany('''
        INSERT INTO %s
        VALUES (%s)
        ''' % (config.sample_labels_sql_table,
               ','.join(['?'] * len(sub_result[0]))),
                           sub_result)

        cnn.commit()
        i += batch_size

    cursor.close()


def hit_etl():
    input_id = 0
    batch = []
    for chunk_num in xrange(num_chunks):
        success_filename = os.path.join(paths.MTURK_DATA_SUBDIR, 'batch_%d' % batch_id,
                                        'data_%d%s%s' % (chunk_num,
                                                         paths.MTURK_INPUT_FILENAME_SUFFIX,
                                                         paths.MTURK_INPUT_SUCCESS_FILENAME_SUFFIX))

        with open(success_filename) as reader:
            i = 0
            for row in reader:
                if i == 0:
                    i += 1
                    continue

                row = row.strip()
                if row:
                    fields = row.split('\t')
                    hit_id = fields[0]
                    hit_group_id = fields[1]

                    batch.append((batch_id, input_id, hit_id, hit_group_id, batch_create_dttm))
                    input_id += 1

    batch_size = 1000
    cnn = pyodbc.connect(config.sql_cnn_str)
    cursor = cnn.cursor()

    i = 0
    while i < len(batch):
        sub_batch = batch[i : i + batch_size]
        print 'Transferring data group #%d...' % (i // batch_size)
        cursor.executemany('''
            INSERT INTO %s
            VALUES (%s)
            ''' % (config.hits_sql_table,
                   ','.join(['?'] * len(sub_batch[0]))),
                           sub_batch)

        cnn.commit()

        i += batch_size

    cursor.close()


def result_etl():
    result = []
    for chunk_num in xrange(num_chunks):
        results_filename = os.path.join(paths.MTURK_DATA_SUBDIR, 'batch_%d' % batch_id,
                                        'data_%d%s' % (chunk_num,
                                                       paths.MTURK_RESULTS_FILENAME_SUFFIX))

        with open(results_filename) as csvfile:
            reader = csv.DictReader(csvfile, delimiter='\t', quoting=csv.QUOTE_ALL)

            i = 0
            for row in reader:
                if i == 0:
                    i += 1
                    continue

                hit_id = row['hitid']
                assignment_id = row['assignmentid']
                worker_id = row['workerid']
                assignment_accept_time = parser.parse(row['assignmentaccepttime'])
                assignment_submit_time = parser.parse(row['assignmentsubmittime'])

                for q_id in xrange(questions_per_hit):
                    description_q_answer = 'Y' if row['Answer.descriptionType%d' % (q_id + 1)] == 'yes' else 'N'
                    tags_q_answers = row['Answer.tags%d' % (q_id + 1)].split('|')

                    for tag_id in tags_q_answers:
                        if tag_id in taxonomy.labels[batch_category]:
                            label_name = taxonomy.labels[batch_category][tag_id]
                            manual_label = 'N'
                        else:
                            label_name = tag_id.strip().title()
                            #print label_name
                            manual_label = 'Y'
                        result.append((batch_id, hit_id,
                                       assignment_id, worker_id,
                                       assignment_accept_time,
                                       assignment_submit_time,
                                       q_id, description_q_answer,
                                       label_name, manual_label))

    #return

    batch_size = 1000
    cnn = pyodbc.connect(config.sql_cnn_str)
    cursor = cnn.cursor()

    i = 0
    while i < len(result):
        sub_result = result[i: i + batch_size]
        print 'Transferring data group #%d...' % (i // batch_size)
        cursor.executemany('''
                INSERT INTO %s
                ([batch_id]
                , [hit_id]
                , [assignment_id]
                , [worker_id]
                , [assignment_accept_time]
                , [assignment_submit_time]
                , [question_id]
                , [description_YN]
                , [label]
                , [manual_label]
                )
                VALUES (%s)
                ''' % (config.hit_results_sql_table,
                       ','.join(['?'] * len(sub_result[0]))),
                           sub_result)

        cnn.commit()

        i += batch_size

    cursor.close()


def populate_predefined_labels():
    cnn = pyodbc.connect(config.sql_cnn_str)
    cursor = cnn.cursor()
    cursor.execute('DELETE FROM %s' % config.predefined_labels_sql_table)
    cursor.commit()

    batch = []
    for category in taxonomy.inv_labels:
        for label in taxonomy.inv_labels[category]:
            batch.append((category, label))

    cursor.executemany('''
    INSERT INTO %s (category, label) VALUES (?,?)''' % config.predefined_labels_sql_table,
                       batch)
    cursor.commit()
    cursor.close()


def populate_labelled_samples(relaxed = False):
    cnn = pyodbc.connect(config.sql_cnn_str)
    cursor = cnn.cursor()
    uri = "mongodb://%s:%s@%s:%s/%s?authMechanism=SCRAM-SHA-1" % (config.username,
                                                                  config.password,
                                                                  config.mongodb_host,
                                                                  config.mongodb_port,
                                                                  config.db)

    mongo_client = MongoClient(uri)
    col = mongo_client[config.db][config.unlabelled_col]

    if not relaxed:
        out_col = mongo_client[config.db][config.result_col]
    else:
        out_col = mongo_client[config.db][config.result_relaxed_col]

    out_col.remove()

    sample_id2info = {}
    cursor.execute('''
    SELECT *
    FROM %s
    ''' % config.hit_selected_descriptions_sql_table)

    for row in cursor:
        video_id = row.video_id
        description_yn = row.description_YN
        batch_id = row.batch_id

        sample_id2info[video_id] = {
            template.contains_content_field : description_yn == 'Y',
            template.batch_id_field: batch_id
        }

    label_sql_table = config.hit_selected_labels_sql_table if not relaxed else config.hit_selected_labels_relaxed_sql_table
    print label_sql_table
    cursor.execute('''
    SELECT *
    FROM %s
    ''' % label_sql_table)
    for row in cursor:
        batch_id = row.batch_id
        video_id = row.video_id
        label = row.label

        if video_id in sample_id2info:
            if template.ml_label_field not in sample_id2info[video_id]:
                sample_id2info[video_id][template.ml_label_field] = []

            sample_id2info[video_id][template.ml_label_field].append(label)
        else:
            sample_id2info[video_id] = {
                template.ml_label_field : [label],
                template.batch_id_field : batch_id
            }

    print 'Populating results into Mongo...'
    i = 0
    batch_size = 100
    all_ids = sample_id2info.keys()
    print 'Total samples: ', len(all_ids)
    etl_dttm = datetime.now()
    while i < len(all_ids):
        print 'Processing video group #%d...' % (i // batch_size)
        sub_ids = all_ids[i : i + batch_size]
        processed_ids = set()
        batch = []

        for video in col.find({template.id_field : {'$in' : [ObjectId(x) for x in sub_ids]}}):
            video_id = str(video[template.id_field])
            for k, v in sample_id2info[video_id].items():
                video[k] = v

            #print video_id, sample_id2info[video_id]
            video[template.batch_id_field] = sample_id2info[video_id][template.batch_id_field]
            video[template.etl_dttm_field] = etl_dttm

            batch.append(video)

            processed_ids.add(video_id)

        out_col.insert_many(batch)
        i += batch_size

    cursor.close()


def merge_all_samples():
    uri = "mongodb://%s:%s@%s:%s/%s?authMechanism=SCRAM-SHA-1" % (config.username,
                                                                  config.password,
                                                                  config.mongodb_host,
                                                                  config.mongodb_port,
                                                                  config.db)


    mongo_client = MongoClient(uri)
    out_col = mongo_client[config.db][config.unlabelled_col]

    processed_ids = set()
    videos = []
    for col_name in ['mturk', 'mturk2', 'mturk3']:
        col = mongo_client[config.db][col_name]
        for doc in col.find():
            video_id = str(doc[template.id_field])
            if video_id not in processed_ids:
                processed_ids.add(video_id)
                videos.append(doc)


    print 'All videos: %d' % len(videos)
    out_col.insert_many(videos)


if __name__ == '__main__':
    #input_data_etl()
    #sample_data_etl()
    #hit_etl()
    #result_etl()
    #populate_predefined_labels()
    #merge_all_samples()
    populate_labelled_samples(relaxed= True)
