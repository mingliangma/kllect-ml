from fields_mapping import fields_mapping
import templates.es_template as est
import templates.mongo_template as mt
import config
import utils.popularity
import traceback
import templates.request_template as rt


def index_video_data_batch(batch_data, es, write_index):
    batch = []
    skipped_ids = []

    for doc in batch_data:
        try:
            out = {
                x: doc[fields_mapping[x]] for x in fields_mapping if x in doc
            }

            out[est.video_id_field] = str(doc[mt.id_field])
            out[est.popularity_field] = utils.popularity.compute_popularity(out)
            if mt.raw_tags_field in doc and doc[mt.raw_tags_field]:
                out[est.raw_tags_text_field] = ' '.join(doc[mt.raw_tags_field])

            batch.append(out)
        except Exception, e:
            # print doc[mt.id_field]

            video_id = doc[mt.id_field] if mt.id_field in doc else None
            skipped_ids.append(video_id)

    if len(batch):
        actions = [es.index_op(x, id= x[est.video_id_field]) for x in batch]

        response = es.bulk(actions,
                           index=write_index,
                           doc_type=config.video_doc_type
                           )

        try:
            errors = response['errors']

            result = {
                rt.success_field : not errors
            }

            if len(skipped_ids):
                result[rt.error_field] = 'Skipped %d malformed instances.' % len(skipped_ids)
            result[rt.skipped_ids_field] = skipped_ids

            return result

        except Exception, e:
            import traceback
            traceback.print_exc()

            return {
                rt.success_field : False,
                rt.error_field : e.message
            }


def remove_video_data_batch(input_ids, es, write_index):
    if len(input_ids):
        actions = [es.delete_op(id=str(x)) for x in input_ids]

        response = es.bulk(actions,
                           index=write_index,
                           doc_type=config.video_doc_type
                           # id_field=est.id_field,
                           )
        try:
            errors = response['errors']
            deleted_ids = []
            not_found_ids = []

            for item in response['items']:
                op = item['delete']
                if op['found']:
                    deleted_ids.append(op['_id'])
                else:
                    not_found_ids.append(op['_id'])

            result = {
                rt.success_field : not errors,
                rt.successes_field : deleted_ids,
                rt.fails_field : not_found_ids
            }

            return result
        except Exception, e:
            return {
                rt.success_field: False,
                rt.error_field: e.message
            }


