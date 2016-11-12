from pymongo import MongoClient
import src.config as config
import src.paths as paths
import os.path
import random
import src.template as template
import io
from unidecode import unidecode
import re
from xml.sax.saxutils import escape
import csv
import math


p = re.compile('\+\+.*')


def generate_mturk_files():
    uri = "mongodb://%s:%s@%s:%s/%s?authMechanism=SCRAM-SHA-1" % (config.username,
                                                                  config.password,
                                                                  config.mongodb_host,
                                                                  config.mongodb_port,
                                                                  config.db)
    client = MongoClient(uri)
    col = client[config.db][config.col]

    i = 0
    batch_size = 1000
    data = []
    labelled_data = []
    questions_per_hit = 3
    unlabelled_questions_per_hit = 2

    for doc in col.find({template.description_field : {'$ne': None},
                         template.is_video_field : True,
                         template.youtube_url_field : {'$ne': None},
                         template.image_url_field: {'$ne': None}}).batch_size(batch_size):
        if i % batch_size == 0:
            print 'Reading document #%d...' % i

        if template.ml_label_field in doc:
            labelled_data.append(doc)
        # else:
        #     data.append(doc)

        i += 1

    i = 0
    unlabelled_col = client[config.db][config.unlabelled_col]
    for doc in unlabelled_col.find({template.description_field: {'$ne': None},
                                    template.is_video_field: True,
                                    '$or' : [
                                        {template.youtube_url_field: {'$ne': None}},
                                        {template.article_url_field : {'$ne': None}}
                                       ],
                                    template.image_url_field: {'$ne': None}
                                    }).batch_size(batch_size):

        if i % batch_size == 0:
            print 'Reading document #%d...' % i

        video_url = doc[template.youtube_url_field]
        article_url = doc[template.article_url_field]

        if video_url is None:
            doc[template.youtube_url_field] = article_url
            #print doc[template.id_field]
        data.append(doc)

        i += 1

    print 'Total instances: %d' % len(data)
    print 'Total labelled instances: %d' % len(labelled_data)
    #return

    #sample_size = 100
    #samples = random.sample(data, sample_size)
    samples = data
    #labelled_samples = random.sample(labelled_data, num_hits)
    labelled_samples = labelled_data
    num_hits = int(math.ceil(len(samples) * 1.0 / unlabelled_questions_per_hit))

    out_data_subdir = os.path.join(paths.MTURK_DATA_SUBDIR, 'batch_3')
    sample_id_filename = os.path.join(out_data_subdir, paths.MTURL_SAMPLES_FILENAME)
    with open(sample_id_filename, 'w') as fout:
        fout.write('VideoID\tLabelled\n')
        for sample in samples:
            fout.write('%s\t%s\n' % (sample[template.id_field],
                                     template.ml_label_field in sample))
        for labelled_sample in labelled_samples:
            fout.write('%s\t%s\n' % (labelled_sample[template.id_field],
                                     template.ml_label_field in labelled_sample))

    output_fields = [template.id_field,
                     template.title_field,
                     template.site_name_field,
                     template.description_field,
                     template.image_url_field,
                     template.image_type_field,
                     template.youtube_url_field
                     ]

    num_batches = 1
    num_hits_per_batch = int(math.ceil(len(data) * 1.0 / (num_batches * unlabelled_questions_per_hit)))

    for batch_id in xrange(num_batches):
        input_filename = os.path.join(out_data_subdir, 'data_%d%s' % (batch_id, paths.MTURK_INPUT_FILENAME_SUFFIX))

        with open(input_filename, 'wb') as fout:
            heading = []
            for i in xrange(questions_per_hit):
                for x in output_fields:
                    heading.append('%s_%d' % (x, i))

            csv_writer = csv.DictWriter(fout, fieldnames=heading, delimiter='\t',
                                        quoting=csv.QUOTE_ALL)
            csv_writer.writeheader()

            #fout.write(u'%s\n' % '\t'.join(heading))

            for hit_id in xrange(num_hits_per_batch):
                offset = num_hits_per_batch * batch_id + hit_id
                unlabelled_hit_samples = samples[offset * unlabelled_questions_per_hit : (offset + 1) * unlabelled_questions_per_hit]
                labeled_hit_samples = random.sample(labelled_samples, questions_per_hit - unlabelled_questions_per_hit)

                hit_samples = labeled_hit_samples + unlabelled_hit_samples

                print 'Generating unlabelled HIT data #%d...' % hit_id
                #print len(hit_samples)

                row = {}
                for (i, hit_sample) in enumerate(hit_samples):
                    #columns = []
                    for x in output_fields:
                        if x == template.id_field:
                            row['%s_%d' % (x, i)] = str(hit_sample[x])
                            #columns.append(str(hit_sample[x]))
                        elif x == template.image_type_field:
                            image_url = hit_sample[template.image_url_field]
                            if image_url:
                                image_type = os.path.splitext(image_url)[-1][1 : ]
                                image_type = re.sub(p, '', image_type)
                                #print image_type
                            else:
                                image_type = None

                            row['%s_%d' % (x, i)] = image_type
                            #columns.append(image_type)
                        elif x in [template.description_field, template.title_field]:
                            clean_text = ' '.join([y.strip() for y in unidecode(hit_sample[x]).split('\n') if y.strip() != ''])
                            clean_text = re.sub('\t', ' ', clean_text).strip()
                            #columns.append(clean_text)
                            #columns.append(escape(clean_text))
                            row['%s_%d' % (x, i)] = clean_text
                        else:
                            row['%s_%d' % (x, i)] = hit_sample[x].strip()
                            #columns.append(hit_sample[x].strip())

                #print row.keys()
                    #all_columns.extend(columns)
                #print row
                csv_writer.writerow(row)
               # fout.write(u'%s\n' % '\t'.join(all_columns))


if __name__ == '__main__':
    generate_mturk_files()