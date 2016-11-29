from flask import Flask, request
from flask_json import FlaskJSON, json_response
from utils import request_utils
import templates.request_template as rt
from es.index.videos import incremental_index_video_data
from es.search import search_videos
from flask_cors import CORS

app = Flask(__name__)

FlaskJSON(app)
CORS(app)


@app.route('/index_videos', methods=['POST'])
def index_new_videos():
    try:
        r = request.get_json(force = True)
    except Exception, e:
        return json_response(result = {'error': 'Need to pass in a valid JSON request'},
                             status_code=500)

    new_videos = request_utils.get_dict_value(r, rt.input_data_field, [])
    if not isinstance(new_videos, list):
        return json_response(result = {'error': 'The parameter "%s" needs to be a list.' % rt.input_data_field}, status_code=500)

    max_allowed_num = 2000
    if len(new_videos) == 0:
        return json_response(result = {'error': 'The parameter "%s" cannot be empty.' % rt.input_data_field}, status_code=500)

    if len(new_videos) > max_allowed_num:
        return json_response(result = {'error': 'The parameter "%s" cannot exceed the size of %d.' % (rt.input_data_field, max_allowed_num)},
                             status_code=500)

    result = incremental_index_video_data.index_videos(new_videos)
    return json_response(result = result, status_code = 500 if rt.error_field in result else 200)


@app.route('/delete_videos', methods=['POST'])
def delete_old_videos():
    try:
        r = request.get_json(force = True)
    except Exception, e:
        return json_response(result = {'error': 'Need to pass in a valid JSON request'},
                             status_code=500)

    old_videos = request_utils.get_dict_value(r, rt.input_data_field, [])
    if not isinstance(old_videos, list):
        return json_response(result = {'error': 'The parameter "%s" needs to be a list.' % rt.input_data_field}, status_code=500)

    max_allowed_num = 2000
    if len(old_videos) == 0:
        return json_response(result = {'error': 'The parameter "%s" cannot be empty.' % rt.input_data_field}, status_code=500)

    if len(old_videos) > max_allowed_num:
        return json_response(result = {'error': 'The parameter "%s" cannot exceed the size of %d.' % (rt.input_data_field, max_allowed_num)},
                             status_code=500)

    result = incremental_index_video_data.delete_videos(old_videos)
    return json_response(result = result, status_code = 500 if rt.error_field in result else 200)


@app.route('/search_videos', methods=['POST'])
def search_videos_query():
    try:
        r = request.get_json(force = True)
    except Exception, e:
        return json_response(result = {'error' : 'Need to pass in a valid JSON request'},
                             status_code=500)

    start = request_utils.get_dict_value(r, rt.search_videos_start_field, 0)

    preferences = request_utils.get_dict_value(r, rt.search_videos_preferences_field, [])
    input_preferences = []
    if preferences:
        for p in preferences:
            category_name = request_utils.get_dict_value(p, rt.search_videos_preference_name_subfield)
            if not category_name:
                return json_response(result=request_utils.compose_missing_field_error_message(
                    '%s.%s' % (rt.search_videos_preferences_field, rt.search_videos_preference_name_subfield)
                ), status_code=500)

            category_weight = request_utils.get_dict_value(p, rt.search_videos_preference_weight_subfield)
            if not category_weight:
                return json_response(result=request_utils.compose_missing_field_error_message(
                    '%s.%s' % (rt.search_videos_preferences_field, rt.search_videos_preference_weight_subfield)
                ), status_code=500)

            input_preferences.append((category_name, category_weight))

    category = request_utils.get_dict_value(r, rt.search_videos_category_field, None)

    keyword = request_utils.get_dict_value(r, rt.search_videos_keyword_field, '')
    size = request_utils.get_dict_value(r, rt.search_videos_size_field, None)
    if size is not None:
        if not isinstance(size, int):
            return json_response(result={'error', 'The parameter "%s" needs to be an integer.' % rt.search_videos_size_field}, status_code=500)

        if size <= 0:
            return json_response(result={'error', 'The parameter "%s" needs to be a positive integer.' % rt.search_videos_size_field}, status_code=500)

    try:
        results, total = search_videos.search_videos(keyword = keyword, category=category, preferences=input_preferences,
                                                     start=start, top_n=size)

        result = {
            rt.search_videos_start_field : start,
            rt.search_videos_size_field : len(results),
            rt.search_videos_total_field : total,
            rt.search_videos_results_field : results
        }
        return json_response(result=result, status_code=200)
    except Exception, e:
        return json_response(result={'error' : e.message}, status_code=500)
