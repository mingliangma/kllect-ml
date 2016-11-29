import templates.es_template as est

boosting = {
    est.raw_tags_text_field : 0.1,
    est.tags_field: 3.0,
    est.title_field: 3.0,
    est.description_field: 1.0
}

TOP_N = 20

PREFERENCE_BOOSTING_FACTOR = 3.0
POPULARITY_BOOSTING_FACTOR = 1.0

ENABLE_DATE_DECAY = True
PUB_DATE_SEARCH_OFFSET = '3d'
PUB_DATE_SEARCH_ScALE = '1w'
PUB_DATE_DECAY = 0.5

