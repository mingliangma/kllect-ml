import templates.request_template as rt
import templates.error_codes as ec


def get_dict_value(d, k, default = None):
    if isinstance(d, dict) and k in d:
        return d[k]

    return default


def compose_missing_field_error_message(field):
    return {rt.response_error_field: 'Need to set the "%s" parameter.' % field,
            rt.response_error_code_field: ec.invalid_parameter_data_type_error
            }