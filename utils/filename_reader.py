


def extract_extension(str):
    """
    Returns the extension of the filename / path string, dot included
    Returns an empty string if there is no extension (folders or specific files)
    Prerequisites: extension is either '.nii.gz' or '.[extension]' with less than 10 characters
    Example:
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
    """
    ext = extract_extension(str)
    if len(ext)>0:
        return str[:-len(ext)]
    else:
        return str
    
def extract_id(str):
    """
    Returns the id of a filename (SeriesNumber with sometimes additional characters) as a string
    """
    str = remove_extension(str)
    split = str.split("_")
    id_index = None
    for i,elt in enumerate(split):
        if is_date(elt):
            id_index = i+1
    id_elt = ''
    for split_elt in split[id_index:]:
        if not split_elt.isalpha():
            id_elt = id_elt + split_elt.lower()
    return id_elt


def extract_sub(str, participants_dict):
    """
    Returns the participant code of a string, raises an assertion error if it cannot find it in the filename
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
    
    return type

def get_category(str):
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
        'individual_spinal_levels'
    ]

    expressions_to_search_in_filename = [
        'total_spineseg'
    ]

    for dir_expression in expressions_to_search_in_dirs:
        if dir_expression in dir_path:
            categories.append(dir_expression)
            break

    

    for filename_expression in expressions_to_search_in_filename:
        if filename_expression in filename.lower():
            categories.append(filename_expression)
            break
    category = '_'.join(categories)
    return category



def get_seg_info(str):
    filename = remove_extension(str.split('/')[-1])
    dirs = [dir.lower() for dir in str.split('/')[:-1:]]
    dir_path = ''
    if len(dirs) >1:
        for dir in dirs:
            dir_path = '/' + dir
    
    expressions_to_search_in_dirs = [
        'segmentator_tissues'
    ]

    expressions_to_search_in_filename = [
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
        'hip_right',
        'iliac_vena_left',
        'iliac_vena_right',
        'iliopsoas_left',
        'iliopsoas_right',
        'inferior_vena_cava',
        'intervertebral_discs',
        'lung_right',
        'portal_vein_and_splenic_vein',
        'sacrum',
        'small_bowel',
        'spinal_cord',
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
    filename = remove_extension(str.split('/')[-1])
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
        if filename_expression in filename.lower():
            return filename_expression

    return ''
    

################################ Booleans ###################################################################

def is_date(str):
    """
    Returns True if the input string is a date (with the common typo 2025 -> 205 taken into account)
    Returns False otherwise
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
    return 'segmentation' in type or (type in ['modelling', 'simulation', 'misc'])

def is_localizer(str):
    try:
        last_dir = str.split('/')[-2].lower()
        return 'localizer' in last_dir
    except:
        return False

def is_other(str):
    try:
        last_dir = str.split('/')[-2].lower()
        return 'other' in last_dir and (not 'localizer_other' in last_dir)
    except:
        return False
    
def is_a_previous_version(str):
    i = -2
    try:
        last_dir = str.split('/')[i].lower()
        while 'previous_version' not in last_dir:
            i-=1
            last_dir = str.split('/')[i].lower()
        return True
    except:
        return False




#########################################################################################################################
################### INFO DICT ###########################################################################################


def create_filename_dict(str, participants_dict):
    out = {}
    out["old_path"] = str
    id = extract_id(str)
    out["id"] = id
    try:
        sub = extract_sub(str, participants_dict)
    except AssertionError:
        sub= ''
    out["sub"] = sub
    
    type = extract_type(str)
    out['type'] = type

    extension = extract_extension(str)
    out['extension'] = extension

    category = get_category(str)
    out['category'] = category

    if 'segmentation' in type:
        seg_info = get_seg_info(str)
        out['seg_info'] = seg_info
    else :
        seg_info = ''
    
    is_localizer_bool = is_localizer(str)
    out['is_localizer'] = is_localizer_bool

    is_other_bool = is_other(str)
    out['is_other'] = is_other_bool

    is_a_previous_version_bool = is_a_previous_version(str)
    out['is_a_previous_version'] = is_a_previous_version_bool

    suffix = get_suffix(str)
    out['suffix'] = suffix

    ############### creates the new path

    new_path = ''

    if is_derivative(type):
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
    
    id_element = 'id-' +id

    elements = [sub, category, id_element, seg_info, suffix]

    new_path += '_'.join([element for element in elements if element!= '']) + extension
    out['new_path'] = new_path

    return out
