def get_dict_value(d, k, default = None):
    if isinstance(d, dict) and k in d:
        return d[k]

    return default


def compose_missing_field_error_message(field):
    return {'error': 'Need to set the "%s" parameter.' % field}