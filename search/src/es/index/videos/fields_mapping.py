import templates.es_template as est
import templates.mongo_template as mt


fields_mapping = {
    est.title_field : mt.title_field,
    est.site_name_field : mt.site_name_field,
    est.publisher_field : mt.publisher_field,
    est.publisher_id_field : mt.publisher_id_field,
    est.parse_date_field : mt.parse_date_field,
    est.publish_date_field : mt.publish_date_field,
    est.article_url_field : mt.article_url_field,
    est.youtube_url_field : mt.youtube_url_field,
    est.description_field : mt.description_field,
    est.is_video_field : mt.is_video_field,
    est.image_url_field : mt.image_url_field,
    est.raw_tags_field : mt.raw_tags_field,
    est.extraction_method_field : mt.extraction_method_field,
    est.tagged_date_field : mt.tagged_date_field,
    est.duration_field : mt.duration_field,
    est.src_id_field : mt.src_id_field,
    est.category_field : mt.category_field,
    est.tags_field : mt.tags_field,
    est.view_count_field : mt.view_count_field,
    est.like_count_field : mt.like_count_field,
    est.dislike_count_field : mt.dislike_count_field,
    est.favorite_count_field : mt.favorite_count_field,
    est.comment_count_field : mt.comment_count_field
}