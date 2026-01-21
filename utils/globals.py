STOP_FLAGS = [
    "_results",
    ".feat",
    "scripts",
    "_all_stls",
#    "_from_stls",
#    "3d_generation",
    "roots_out",
    "physiolog",
    "blender",
    "tmp",
    "code",
    "aspinalgen",
    "roots_rootlets"
    ]

EXACT_STOP_FLAGS = [
        #'3d_generation',
        '_all_stls',
        'stls',
        'objs',
        'roots_out',
        'screenshots',
        'dicom'
    ]

STRS_TO_IGNORE_FOR_RUN = [
        'model_9',
        'model_10',
        'fat_candidate_1',
        'fat_candidate_2',
        'fat_candidate_3',
        '_-_DLIR',
        "_viz_99p",
        "_bin_99p"
    ]

MAX_FILE_SIZE_FOR_COMPARISON = (2**10)**3 # 1Go limit when downloading for comparison

STRS_TO_REMOVE_FOR_JSONS_TO_DATA = [
        '.',
        'dicoms_',
        't2g002_',
        'brain_',
        'nonanonymous_',
        'ct_'
    ]