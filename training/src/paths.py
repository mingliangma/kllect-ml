import os.path

ROOT_DIR = 'D:/Codes/Kllect'
DATA_SUBDIR = os.path.join(ROOT_DIR, 'data')

MTURK_DATA_SUBDIR = os.path.join(DATA_SUBDIR, 'mturk')
MTURK_INPUT_FILENAME_SUFFIX = '.input'
MTURK_PROPERTIES_FILENAME_SUFFIX = '.properties'
MTURK_QUESTIONS_FILENAME_SUFFIX = '.question'
MTURK_INPUT_SUCCESS_FILENAME_SUFFIX = '.success'
MTURK_RESULTS_FILENAME_SUFFIX = '.results'
MTURL_SAMPLES_FILENAME = 'sample_ids.txt'

MODELING_SUBDIR = os.path.join(DATA_SUBDIR, 'modeling')
MODElS_SUBDIR = os.path.join(MODELING_SUBDIR, 'models')
MODELING_DATA_SUBDIR = os.path.join(MODELING_SUBDIR, 'data')
MODELING_RESULTS_SUBDIR = os.path.join(MODELING_SUBDIR, 'results')
