mongodb_host = 'ds023213.mlab.com'
mongodb_port = 23213
db = 'ml-labels'
#col = 'article'
col = 'mturk'
unlabelled_col = 'mturk_all'
result_col = 'mturk_results'
result_relaxed_col = 'mturk_results'

username = 'kllect_app'
password = 'Np64vQUcVeitBn'

sql_cnn_str = 'DRIVER={SQL Server};SERVER=VANESSAPC;Trusted_Connection=True;'

input_data_sql_table = '[Kllect].[dbo].[INPUT_DATA]'
sample_labels_sql_table = '[Kllect].[dbo].[SAMPLE_LABELS]'
hits_sql_table = '[Kllect].[dbo].[HITS]'
hit_results_sql_table = '[Kllect].[dbo].[HIT_RESULTS]'
hit_selected_descriptions_sql_table = '[Kllect].[dbo].[MTURK_SELECTED_DESCRIPTION_YN]'
hit_selected_labels_sql_table = '[Kllect].[dbo].[MTURK_SELECTED_LABELS]'
hit_selected_labels_relaxed_sql_table = '[Kllect].[dbo].[MTURK_SELECTED_LABELS_RELAXED]'
predefined_labels_sql_table = '[Kllect].[dbo].[PREDEFINED_LABELS]'