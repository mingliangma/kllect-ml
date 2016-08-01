def parse_request_params(request_body, argument, default = None):
    return get_dict_value(request_body, argument, default)


def get_dict_value(d, k, default= None):
    return d[k] if k in d else default