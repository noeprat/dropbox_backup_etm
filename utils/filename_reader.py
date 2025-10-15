


def extract_extension(str):
    """
    Returns the extension of the filename / path string, dot included,
    returns an empty string if there is no extension (folders or specific files)

    Parameters
    --------
        str : str,
            a path/filename string
            
            Prerequisites: extension is either '.nii.gz' or '.[extension]' with less than 10 characters

    Returns
    --------
        ext: str,
            the extension extracted in str, dot included
    Examples
    --------
    ext = extract_extension('folder/file.nii.gz')
    >>> ext
    '.nii.gz'
    """
    if str[-7:]==".nii.gz":
        ext = ".nii.gz"
    else:
        ext =  str.split(".")[-1]
        if len(ext) < len(str) and len(ext)<10:
            ext = "." + ext
        else:
            ext=''
    return ext

def remove_extension(str):
    """
    Removes the extension of a path string

    Parameters
    --------
        str : str,
            a path/filename string
            
            Prerequisites: extension is either '.nii.gz' or '.[extension]' with less than 10 characters

    Returns
    --------
        new_str: str,
            the new path without the extension
    """
    ext = extract_extension(str)
    if len(ext)>0:
        return str[:-len(ext)]
    else:
        return str
    
def extract_id(str):
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
    filename = remove_extension(str).split('/')[-1]
    split = filename.split("_")
    id_index = None
    for i,elt in enumerate(split):
        if is_date(elt):
            id_index = i+1
            break
    id_elt = ''
    if id_index is not None:
        for split_elt in split[id_index:]:
            if not split_elt.isalpha():
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
        raise AssertionError
    else:
        return participants_dict[old_name]

def extract_type(str):
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
    filename = remove_extension(str.split('/')[-1])
    extension = extract_extension(str)
    keywords = [keyword.lower() for keyword in filename.split('_')]
    root_dirs_keywords = []
    for dir in str.split('/')[:-1:]:
        root_dirs_keywords+= [keyword.lower() for keyword in dir.split('_')]
    if 'ct' in keywords:
        if 'seg' in keywords:
            type = 'ct_segmentation'
        else:
            type = 'ct'
    elif extension == '.smash':
        type = 'simulation'
    elif 'restingstate' in keywords or 'fmri' in keywords:
        type = 'func'
    elif 'mri' in keywords:
        if 'seg' in keywords or 'mask' in keywords or 'tissues' in root_dirs_keywords:
            type = 'anat_segmentation'
        else:
            type = 'anat'
    else:
        type = ''
    
    return type

def get_category(str):
    """
    Returns additional information on the data

    Possible categories (so far):
     - ssl_tissues_post_pro_step_02
     - ssl_tissues_post_pro_step_01
     - ssl_tissues
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
    if is_localizer(str):
        return 'localizer'
    filename = remove_extension(str.split('/')[-1])
    
    dirs = [dir.lower() for dir in str.split('/')[:-1:]]
    dir_path = ''
    if len(dirs) >1:
        for dir in dirs:
            dir_path = '/' + dir
    categories = []
    
    # make sure to have the expressions containing the ones before first
    expressions_to_search_in_dirs = [
        'ssl_tissues_post_pro_step_02',
        'ssl_tissues_post_pro_step_01',
        'ssl_tissues',  # must be after "ssl_tissues_post_pro_01"
        'deepseg',
        'for_making_levels',
        'lumbar',
        'ax_lspine',
        'ax_obl_sacrum',
        'bladder',
        'individual_spinal_levels',
        'resting_state'
    ]

    expressions_to_search_in_filename = [
        'total_spineseg',
        'lumbar',

    ]

    for dir_expression in expressions_to_search_in_dirs:
        if dir_expression in dir_path:
            categories.append(dir_expression)
            break

    

    for filename_expression in expressions_to_search_in_filename:
        if filename_expression in filename.lower() and (filename_expression not in categories):
            categories.append(filename_expression)
            break
    category = '_'.join(categories)
    return category



def get_seg_info(str):
    """
    Returns additional information about a segmentation (if it is a mask, which part was targeted, which tools were used to segment, ...)
    
    
    Parameters
    --------
        str : str,
            a path/filename string
    
    Returns
    --------
        seg_info: str,
    
    Possible seg_info (so far)
    --------
     - segmentator_tissues
     - seg_model_9_roots_as_one_entity_small
     - seg_model_9_roots_as_one_entity
     - seg_model_9
     - seg_Model_10_roots_by_spinal_levels_small
     - seg_Model_10_roots_by_spinal_levels
     - seg_Model_10
     - csf_s4l_mask
     - csf_s4l
     - roots_mask
     - roots
     - wm_mask
     - wm
     - step1_canal
     - step1_cord
     - step1_levels
     - step1_output
     - step2_output
     - l2
     - l3
     - l4
     - l5
     - more_caudal
     - more_rostral
     - s1
     - s2
     - s3
     - s4
     - aorta
     - autochthon_left
     - autochthon_right
     - colon
     - gluteus_maximus_left
     - gluteus_maximus_right
     - gluteus_medius_left
     - gluteus_medius_right
     - hip_left
     - hip_right
     - iliac_vena_left
     - iliac_vena_right
     - iliopsoas_left
     - iliopsoas_right
     - inferior_vena_cava
     - intervertebral_discs
     - kidney_left
     - kidney_right
     - liver
     - lung_left
     - lung_right
     - portal_vein_and_splenic_vein
     - sacrum
     - small_bowel
     - spinal_cord
     - spleen
     - stomach
     - vertebrae
    """
    filename = remove_extension(str.split('/')[-1])
    dirs = [dir.lower() for dir in str.split('/')[:-1:]]
    dir_path = ''
    if len(dirs) >1:
        for dir in dirs:
            dir_path = '/' + dir
    
    expressions_to_search_in_dirs = [
        'segmentator_tissues'
    ]

    expressions_to_search_in_filename = [ # the largest expressions first
        'seg_model_9_roots_as_one_entity_small',
        'seg_model_9_roots_as_one_entity',
        'seg_model_9',
        'seg_Model_10_roots_by_spinal_levels_small',
        'seg_Model_10_roots_by_spinal_levels',
        'seg_Model_10',
        "csf_s4l_mask",
        "csf_s4l",
        "roots_mask",
        "roots",
        "wm_mask",
        'wm',
        "step1_canal",
        "step1_cord",
        "step1_levels",
        "step1_output",
        "step2_output",
        'l2',
        'l3',
        'l4',
        'l5',
        'more_caudal',
        'more_rostral',
        's1',
        's2',
        's3',
        's4',
        'aorta',
        'autochthon_left',
        'autochthon_right',
        'colon',
        'gluteus_maximus_left',
        'gluteus_maximus_right',
        'gluteus_medius_left',
        'gluteus_medius_right',
        'hip_left',
        'hip_right',
        'iliac_vena_left',
        'iliac_vena_right',
        'iliopsoas_left',
        'iliopsoas_right',
        'inferior_vena_cava',
        'intervertebral_discs',
        'kidney_left',
        'kidney_right',
        'liver',
        'lung_left',
        'lung_right',
        'portal_vein_and_splenic_vein',
        'sacrum',
        'small_bowel',
        'spinal_cord',
        'spleen',
        'stomach',
        'vertebrae'
    ]

    seg_infos = []
    for dir_expression in expressions_to_search_in_dirs:
        if dir_expression in dir_path:
            seg_infos.append(dir_expression)
            break

    

    for filename_expression in expressions_to_search_in_filename:
        if filename_expression in filename.lower():
            seg_infos.append(filename_expression)
            break

    seg_info = '_'.join(seg_infos)
    return seg_info

def get_suffix(str):
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
        str : str,
            a path/filename string
    
    Returns
    --------
        suffix: str,
    """
    filename = remove_extension(str.split('/')[-1]).lower()
    keywords = [keyword.lower() for keyword in filename.split('_')]
    extension = extract_extension(str)

    type = extract_type(str)

    if 'ct' in type:
        return 'ct'
    
    elif 'func' in type:
        if 'physiolog' in filename:
            return 'physiolog'
        elif 'interoperability' in filename:
            return 'interoperability'
        else:
            return 'bold'


    elif 't2' in keywords and 'spc' in keywords and 'zoomit' in keywords:
        return 't2_spc_zoomit'

    expressions_to_search_in_filename = [
        't2_space',
        't2_tse',
        't2_trufi3d',
        't2_gre',
        't1_tfe',
        'b_ffe',
        't2_3d_tra_vista',
        't2w_ffe',
        'ffe'  # must be after 'b_ffe' etc.
    ]

    for filename_expression in expressions_to_search_in_filename:
        if filename_expression in filename:
            return filename_expression

    return ''
    
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
    return 'segmentation' in type or (type in ['modelling', 'simulation', 'misc'])

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

def is_other(str):
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
        return 'other' in last_dir and (not 'localizer_other' in last_dir)
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
            True iff the file is in a 'previous_version' subdirectory
    """
    i = -2
    try:
        last_dir = str.split('/')[i].lower()
        while 'previous_version' not in last_dir:
            i-=1
            last_dir = str.split('/')[i].lower()
        return True
    except:
        return False

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
    

    ############### creates the new path

    new_path = ''

    if is_tmp_bool:
        new_path = 'tmp' + str
    else:
        if is_derivative_bool:
            new_path += 'derivatives/'
            if 'segmentation' in type:
                new_path += 'segmentation/' + sub + '/' + type.split('_')[0] + '/'
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
        
        

        elements = [sub, category, id_element, seg_info, suffix]

        new_path += '_'.join([element for element in elements if element!= '']) + extension
    
    out['new_path'] = new_path

    return out
