import templates.es_template as est
import math
import request_utils


def compute_popularity(doc):
    view_count = request_utils.get_dict_value(doc, est.view_count_field, 0)

    return math.log(view_count + 1, 10)
