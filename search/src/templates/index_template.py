from es_template import *


index_mapping = {
    "mappings": {
        "video": {
            "properties": {
                video_id_field: {
                    "type": "string",
                    "index": "not_analyzed"
                },
                title_field: {
                    "type": "string",
                    "norms": {
                        "enabled": False
                    }
                },
                site_name_field: {
                    "type": "string",
                    "index": "not_analyzed"
                },
                publisher_field: {
                    "type": "string",
                    "index": "not_analyzed"
                },
                publisher_id_field: {
                    "type": "string",
                    "index": "not_analyzed"
                },
                parse_date_field: {
                     "type": "date"
                },
                publish_date_field: {
                     "type": "date"
                },
                article_url_field: {
                    "type": "string",
                    "index": "not_analyzed"
                },
                youtube_url_field: {
                    "type": "string",
                    "index": "not_analyzed"
                },
                description_field: {
                    "type" : "string",
                    "norms": {
                        "enabled": False
                    }
                },
                is_video_field: {
                    "type": "boolean"
                },
                image_url_field: {
                    "type": "string",
                    "index": "not_analyzed"
                },
                raw_tags_field: {
                    "type": "string",
                    "index": "not_analyzed"
                },
                raw_tags_text_field : {
                    "type": "string",
                    "norms": {
                        "enabled": False
                    }
                },
                tagged_date_field: {
                    "type": "date"
                },
                extraction_method_field: {
                    "type": "string",
                    "index": "not_analyzed"
                },
                duration_field: {
                    "type": "integer"
                },
                src_id_field: {
                    "type": "string",
                    "index": "not_analyzed"
                },
                category_field: {
                    "type": "string",
                    "index": "not_analyzed"
                },
                tags_field: {
                    "type": "string",
                    "index": "not_analyzed"
                },
                view_count_field: {
                    "type": "integer"
                },
                like_count_field: {
                    "type": "integer"
                },
                dislike_count_field: {
                    "type": "integer"
                },
                favorite_count_field: {
                    "type": "integer"
                },
                comment_count_field: {
                    "type": "integer"
                },
                popularity_field: {
                    "type": "double"
                }
            }
        }
    }
}