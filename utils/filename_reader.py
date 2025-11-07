from .misc import pick_largest_str_in_list, get_path_info, remove_extension, extract_extension
import json



    
def extract_id(str, debug=False):
    """
    Returns the id of a filename (SeriesNumber with sometimes additional characters) as a string

    Parameters
    --------
        str : str,
            a path/filename string
    
    Returns
    --------
        id_elt: str,
            the id of the specified filename
    """
    filename = remove_extension(str).split('/')[-1].lower()
    id_index = None

    # curate filename to avoid confusions
    strs_to_ignore = [
        'model_9',
        'model_10',
        'fat_candidate_1',
        'fat_candidate_2',
        'fat_candidate_3',
    ]
    
    for s in strs_to_ignore:
        filename = filename.replace(s, '')
    

    split = filename.split("_")
    for i,elt in enumerate(split):
        if is_date(elt):
            id_index = i+1
            break
    id_elt = ''

    if id_index is not None:
        for split_elt in split[id_index:]:
            if (not split_elt.isalpha()) and (not split_elt in ['s4l', ]):
                id_elt = id_elt + split_elt.lower()
    return id_elt


def extract_sub(str, participants_dict):
    """
    Returns the participant code of a string, raises an assertion error if it cannot find it in the filename

    Parameters
    --------
        str : str,
            a path/filename string
        participants_dict : dict
            participants[old_name] = new_name, e.g. participants_dict['REEVOID_001'] = 'sub-01'
    
    Returns
    --------
        new_name: str,
            the new participant code ('sub-*')
    """
    filename = str.split("/")[-1]
    split = filename.split("_")
    old_name = split[0]
    i=1
    while (old_name not in participants_dict.keys()) and i <len(split):
        old_name += '_' + split[i]
        i+=1
    if old_name not in participants_dict.keys():
        return ''
    else:
        return participants_dict[old_name]

def extract_type(str, debug=False):
    """
    Possible types (so far):
     - anat
     - anat_segmentation
     - ct
     - ct_segmentation
     - func
     - simulation

    Parameters
    --------
        str : str,
            a path/filename string
    
    Returns
    --------
        type: str,
            the type of the specified file
    """
    filename = remove_extension(str.split('/')[-1]).lower()
    dirs = '/'.join(str.split('/')[:-1]).lower()
    extension = extract_extension(str)
    keywords = [keyword.lower() for keyword in filename.split('_')]
    root_dirs_keywords = []
    for dir in str.split('/')[:-1:]:
        root_dirs_keywords+= [keyword.lower() for keyword in dir.split('_')]

    if debug:
        print(root_dirs_keywords)
    
    
    if extension in ['.py', '.ipynb', '.pyc', '.sh', '.fsf' ] or 'scripts' in root_dirs_keywords or 'scripts' in filename :
        type = 'code'
    elif extension in ['.avi', '.png', '.pdf']:
        type = 'misc'
    elif 'dti' in keywords or extension in ['.bval', '.bvec']:
        type = 'dti'
    elif 'ct' in keywords or 'ct' in root_dirs_keywords:
        if 'seg' in keywords or 'seg' in root_dirs_keywords or 'tissues' in root_dirs_keywords:
            type = 'ct_segmentation'
        elif 'bin' in keywords or 'metal' in keywords: 
            ### this case might be specific to t2g_sub02 !!
            type= 'ct_segmentation' 
        else:
            type = 'ct'
    elif extension == '.smash':
        type = 'simulation'

    elif 'restingstate' in keywords or 'fmri' in str.lower() or 'functional' in str.lower() or 'physiolog' in filename:
        if 'seg' in root_dirs_keywords or 'segmentation' in root_dirs_keywords or 'segmentation_functional' in str.lower():
            type = 'func_segmentation'
        else:
            type = 'func'
    
    elif extension == '.feat' or 'thresh_zstat1_reg' in filename or 'acompcor' in filename or 'rmsctp0fmri' in filename:
        type = 'func_derivatives'
    
    
    elif 'structural' in keywords or 'structural' in root_dirs_keywords or 'mri' in keywords or 'mri' in root_dirs_keywords:
        if 'seg' in keywords or 'mask' in keywords or 'tissues' in root_dirs_keywords or 'seg' in root_dirs_keywords or 'segmentations' in root_dirs_keywords:
            type = 'anat_segmentation'
        elif 'betted' in filename or 'transf' in filename or 'template' in filename:
            if debug:
                print(filename)
            type = 'anat_derivatives'
        else:
            type = 'anat'

    #special to T2G, rules may not apply to later dirs
    elif extension in ['.stl', '.blend', '.obj', '.mtl','.glb'] or filename in ['3d_generation', '_all_stls', 'blender']:
        type = 'modelling'
    elif 'spinal_level' in dirs or sum([word in filename for word in ['roots_out','roots_rootlets', 'roots_seg_to_centerline']])>=1 or ('intersections' in filename) :
        type = 'anat_segmentation'

    

    elif extension=='.nii.gz':
        type = 'anat'
    
    else:
        type = 'misc'
    
    return type

def get_category(input_path):
    """
    Returns additional information on the data

    Possible categories (so far):
     - ssl_tissues_post_pro_step_02
     - ssl_tissues_post_pro_step_01
     - ssl_tissues
     - axobl_sacrum_deepseg
     - axobl_sacrum
     - ax_lspine_deepseg
     - ax_lspine
     - deepseg
     - for_making_levels
     - lumbar
     - ax_lspine
     - ax_obl_sacrum
     - bladder
     - individual_spinal_levels
     - resting_state
     - total_spineseg
     - lumbar
    
    Parameters
    --------
        str : str,
            a path/filename string
    
    Returns
    --------
        category: str,
            the category of the specified file
    """

    category = get_path_info(
        path= input_path,
        data_path='utils/category.json'
    )
    return category



def get_seg_info(input_path):
    """
    Returns additional information about a segmentation (if it is a mask, which part was targeted, which tools were used to segment, ...)
    
    
    Parameters
    --------
        str : str,
            a path/filename string
    
    Returns
    --------
        seg_info: str,
    
    Example seg_info (so far)
    --------
     - segmentator_tissues
     - seg_model_9_roots_as_one_entity_small
     - seg_model_9_roots_as_one_entity
     - seg_model_9
     - seg_Model_10_roots_by_spinal_levels_small
     - seg_Model_10_roots_by_spinal_levels
     - seg_Model_10
    """
    seg_info = get_path_info(
        path= input_path,
        data_path='utils/seg_info.json'
    )
    
    return seg_info



def get_func_task(input_path, debug=False):
    """
    Returns the task performed for fMRI
    
    
    Parameters
    --------
        str : str,
            a path/filename string
    
    Returns
    --------
        func_task: str,
    
    Possible func_tasks 
    --------
    'right_ankle'
    'left_angle'
    'right_knee'
    'left_knee'
    'right_hip'
    'left_hip'
    'right_grasp'
    'left_grasp'
    
    """
    
    func_task = get_path_info(
        path= input_path,
        data_path='utils/func_task.json'
    )
    return func_task


def get_func_info(input_path):
    """
    Returns additional information about fMRI 
    
    
    Parameters
    --------
        input_path : str,
            a path/filename string
    
    Returns
    --------
        func_info: str,
    
    Possible func_info (so far)
    --------
    'brain_wm_gm',
    'left_cerebellum_gm',
    'left_cerebellum_wm',
    'right_cerebellum_gm',
    'right_cerebellum_wm',
    'cerebellum_gm',
    'cerebellum_wm',
    'csf',
    'full_wm_gm',
    'full_gm',
    'full_wm',
    'left_gm',
    'left_wm',
    'right_gm',
    'right_wm',
    'gm',
    'wm'
    """

    seg_info = get_path_info(
        path= input_path,
        data_path='utils/func_info.json'
    )
    return seg_info


def get_suffix(string, debug=False):
    """
    Returns the suffix for the new path, should contain information about the imaging sequance and/or the type of signal

    Possible suffixes:
     - ct
     - physiolog
     - interoperability
     - bold
     - t2_spc_zoomit
     - t2_space
     - t2_tse
     - t2_trufi3d
     - t2_gre
     - t1_tfe
     - b_ffe
     - t2_3d_tra_vista
     - t2w_ffe
     - ffe
    
    Parameters
    --------
        string : str,
            a path/filename string
    
    Returns
    --------
        suffix: str,
    """
    

    type = extract_type(string)

    with open('utils/suffix.json', 'r') as f:
        data = json.load(f)

    # curate filename to avoid confusions
    strings_to_ignore = data["to_ignore"]
    
    

    filename = remove_extension(string.split('/')[-1]).lower()

    for s in strings_to_ignore:
        filename = filename.replace(s, '')

    
    keywords = [keyword.lower() for keyword in filename.split('_')]
    extension = extract_extension(string)

    if 'func' in type and type != 'func_derivatives':
        if 'physiolog' in filename:
            suffix = 'physiolog'
        elif 'interoperability' in filename:
            suffix = 'interoperability'
        elif 'timings' in filename:
            suffix = 'timings'
        elif 'acompcor' in filename:
            suffix = 'acompcor'
        else:
            suffix = 'bold'
    
    elif type == 'dti':
        suffix = 'dti'


    elif 't2' in keywords and 'spc' in keywords and 'zoomit' in keywords:
        suffix = 't2_spc_zoomit'
    
    else:
        suffix = ''

    expressions_to_search_in_filename = data['to_search_in_filename']

    if debug:
        print(filename)
    
    for filename_expression in expressions_to_search_in_filename:
        if debug:
            print('expression',filename_expression)
        if filename_expression in filename and filename_expression not in suffix:
            if suffix == '':
                suffix = filename_expression
            else:
                suffix = suffix + '_' + filename_expression

    extras = [
        'corrected',
        'preprocessed',
        'version-2024',
        'fixed',
        'new_inference'
    ]

    extras += ['v0' + str(i) for i in range(10)]

    for extra in extras:
        if extra in string.lower():
            if suffix == '':
                suffix = extra
            else:
                suffix = suffix + '_' + extra

    return suffix.strip('_')
    
##################################################################################################################################################
################################ Booleans ########################################################################################################

def is_date(str):
    """
    Returns True if the input string is a date (with the common typo 2025 -> 205 taken into account)

    Returns False otherwise

    Parameters
    --------
        str : str,
            a string supposedly containing a date (between 2000 and 2025)
    
    Returns
    --------
        is_date_bool: bool,
    """
    if str.isdecimal():   
        if len(str)==14: #correctly formatted date
            year = int(str[:4])
            month = int(str[4:6])
            day = int(str[6:8])
            return 2000 <= year and year <= 2025 and month <= 12 and day <= 31


        elif len(str)==13: #typo
            year = int(str[:3])
            month = int(str[3:5])
            day = int(str[5:7])
            return 200 <= year and year <= 205 and month <= 12 and day <= 31
        else:
            return False
    else: 
        return False

def is_derivative(type):
    """
    Parameters
    --------
        type : str,
            a type, like 'anat' or 'modelling'
    
    Returns
    --------
        is_derivative_bool: bool,
    """
    return 'segmentation' in type or (type in ['modelling', 'simulation', 'misc']) or 'derivative' in type

def is_localizer(str):
    """
    Parameters
    --------
        str : str,
            a path/filename string
    
    Returns
    --------
        is_localizer_bool: bool,
            True iff the file is in a localizer subdirectory
    
    Errors for json files will be handled thanks to functions in utils.save_logs
    """
    try:
        last_dir = str.split('/')[-2].lower()
        return 'localizer' in last_dir
    except:
        return False

def is_other(str, debug=False):
    """
    Parameters
    --------
        str : str,
            a path/filename string
    
    Returns
    --------
        is_other_bool: bool,
            True iff the file is in an "other" subdirectory
    """
    try:
        last_dir = str.split('/')[-2].lower()
        if debug:
            print(last_dir)
            print('other' in last_dir)
            print((not 'localizer_other' in last_dir))
            print((not 'localizers_other' in last_dir))
        return 'other' in last_dir and (not 'localizer_other' in last_dir) and (not 'localizers_other' in last_dir)
    except:
        return False
    
def is_a_previous_version(str):
    """
    Parameters
    --------
        str : str,
            a path/filename string
    
    Returns
    --------
        is_a_previous_version_bool: bool,
            True iff the file is a previous version
    """
    return 'previous_version' in str.lower() or 'version_2024' in str.lower()

def is_tmp(str):
    """
    Parameters
    --------
        str : str,
            a path/filename string
    
    Returns
    --------
        is_tmp_bool: bool,
            True iff the file is suspected to be a temporary file (contains 'tmp' in its path)
    """
    is_tmp_bool = 'tmp' in str.lower()
    return is_tmp_bool





#########################################################################################################################
################### INFO DICT ###########################################################################################

def generate_new_path(old_path, sub, id, type, category, seg_info, func_task, func_info, suffix, extension, is_tmp_bool, is_derivative_bool, is_localizer_bool, is_other_bool, is_a_previous_version_bool):
    """
    Returns a new_path string given all the information in the arguments

    Parameters
    --------
        old_path : str,
        sub : str,
        id : str,
        type : str,
        category : str,
        seg_info : str,
        func_task : str,
        func_info : str,
        suffix : str,
        extension : str,
        is_tmp_bool : bool,
        is_derivative_bool : bool,
        is_localizer_bool : bool,
        is_other_bool : bool,
        is_a_previous_version_bool : bool,
    
    Returns
    --------
        new_path : str,
            new path for the original file
    """
    new_path = ''

    if is_tmp_bool:
        new_path = 'tmp' + old_path

    elif type in ['code','misc']:
        new_path = type + old_path
    
    elif type == 'modelling':
        if sub =='':
            new_path = 'derivatives/modelling' + old_path
        else:
            new_path = 'derivatives/modelling/' + sub + old_path
    else:
        if is_derivative_bool:
            new_path += 'derivatives/'
            if 'segmentation' in type:
                new_path += 'segmentation/' + sub + '/' + type.split('_')[0] + '/'
            elif 'derivatives' in type:
                new_path += type.split('_')[0] + '/' + sub +'/'
            else:
                new_path += type +'/' + sub + '/'
        else:
            new_path += sub + '/' + type + '/'

        if is_localizer_bool:
            new_path+= '_localizer/'
        elif is_other_bool:
            new_path += '_other/'
        elif is_a_previous_version_bool:
            new_path += '_previous_version/'
        
        if id != '':
            id_element = 'id-' +id
        else:
            id_element = ''
        
        if 'func' in type:
            if func_task != '':
                task_elt = 'task-' + func_task
            else:
                task_elt = ''
            if seg_info in func_info:
                seg_info= ''
            elif func_info in seg_info:
                func_info= ''
            elements = [sub, category, id_element, task_elt, func_info, seg_info, suffix]  
        else:
            elements = [sub, category, id_element, seg_info, suffix]

        new_path += '_'.join([element for element in elements if element!= '']) + extension
    
    return new_path


def create_filename_dict(str, participants_dict, **kwargs):
    """
    Returns a dict containing information and sorting instructions ("new_path") given a path string and the participants dict.
    Handles suspected tmp files (contain 'tmp' in their path)

    Parameters
    --------
        str : str,
            a path/filename string
        participants_dict : dict,
            new sub name given to the former one (e.g. participants_dict['REEVOID_PILOT_01'] = 'sub-pilot')
    
    Returns
    --------
        out : dict,
            information and new path for the original file
    
    Kwargs
    --------
        sub : str,
            precises the sub name
        type : str,
            precises if it is 'anat', 'func', etc.
        category : str,
            additional information
        seg_info : str,
            possible information if it is segmentation (zone targeted, mask, ...)
        is_localizer : Bool,
        is_other : Bool,
        is_a_previous_version : Bool,
        is_derivative : Bool,
    """
    out = {}
    out["old_path"] = str
    id = extract_id(str)
    out["id"] = id

    if 'sub' not in kwargs.keys():
        try:
            sub = extract_sub(str, participants_dict)
        except AssertionError:
            sub= 'sub'
    else:
        sub = kwargs['sub']
    out["sub"] = sub
    
    if 'type' not in kwargs.keys():
        type = extract_type(str)
    else:
        type = kwargs['type']
    out['type'] = type

    extension = extract_extension(str)
    out['extension'] = extension
    
    if 'category' not in kwargs.keys():
        category = get_category(str)
    else:
        category = kwargs['category']
    out['category'] = category

    if 'seg_info' not in kwargs.keys():
        if 'segmentation' in type:
            seg_info = get_seg_info(str)
            out['seg_info'] = seg_info
        else :
            seg_info = ''
    else:
        seg_info = kwargs['seg_info']
        out['seg_info'] = seg_info
    
    if 'func_task' not in kwargs.keys():
        func_task = get_func_task(str)
    else:
        func_task = kwargs['func_task']        
    
    if 'func_info' not in kwargs.keys():
        func_info = get_func_info(str)
    else:
        func_info = kwargs['func_info']
    
    if 'func' in type:
        out['func_task'] = func_task
        out['func_info'] = func_info
    
    is_tmp_bool = is_tmp(str)
    out['is_tmp'] = is_tmp_bool

    if 'is_localizer' not in kwargs.keys():
        is_localizer_bool = is_localizer(str)
    else:
        is_localizer_bool = kwargs['is_localizer']
    out['is_localizer'] = is_localizer_bool

    if 'is_other' not in kwargs.keys():
        is_other_bool = is_other(str)
    else:
        is_other_bool = kwargs['is_other']
    out['is_other'] = is_other_bool

    if 'is_a_previous_version' not in kwargs.keys():
        is_a_previous_version_bool = is_a_previous_version(str)
    else:
        is_a_previous_version_bool = kwargs['is_a_previous_version']
    out['is_a_previous_version'] = is_a_previous_version_bool

    suffix = get_suffix(str)
    out['suffix'] = suffix


    if 'is_derivative' not in kwargs.keys():
        is_derivative_bool = is_derivative(type)
    else:
        is_derivative_bool = kwargs['is_derivative']
    out['is_derivative'] = is_derivative_bool
    


    new_path = generate_new_path(
        str,
        sub,
        id,
        type,
        category,
        seg_info,
        func_task,
        func_info,
        suffix,
        extension,
        is_tmp_bool,
        is_derivative_bool,
        is_localizer_bool,
        is_other_bool,
        is_a_previous_version_bool
    )
    
    out['new_path'] = new_path

    return out
