import json
import re

from utils.globals import STRS_TO_IGNORE_FOR_RUN, STRS_TO_REMOVE_FOR_MODELLING_NEW_PATH
from utils.misc import get_path_info, remove_extension, extract_extension

    
def extract_run(input_path, debug=False):
    """
    Returns the run of a filename (SeriesNumber with sometimes additional characters) as a string

    Package
    ----
    `utils.filename_reader.py`

    Parameters
    --------
        input_path : str,
            a path/filename string
        debug : bool, default = False
            allows prints for debugging purposes
    
    Returns
    --------
        run_elt: str,
            the run corresponding to the specified filename
    """
    filename = remove_extension(input_path).split('/')[-1].lower()
    curated_input_path = input_path.lower()
    run_index = None

    # curate filename to avoid confusions
    
    for s in STRS_TO_IGNORE_FOR_RUN:
        filename = filename.replace(s, '')
        curated_input_path = curated_input_path.replace(s, '')
    

    split = filename.split("_")
    for i,elt in enumerate(split[:-1]):
        #if is_date(elt) or (elt=='ct' and split[i+1].isnumeric()):
        if is_date(elt):
            run_index = i+1
            break
    run_elt = ''

    if run_index is not None:
        for split_elt in split[run_index:]:
            if (not split_elt.isalpha()) and (not split_elt in ['s4l']):
                run_elt = run_elt + split_elt.lower()

    pattern1 = re.compile(r'CT_\D*_([\d_]*)_bin')
    match1 = re.search(pattern1,input_path)
    if match1:
        run_elt += match1.group(1)
    pattern2 = re.compile(r'Pre_Op_CT_([\d_]*)_bin')
    match2 = re.search(pattern2, input_path)
    if match2:
        run_elt += match2.group(1)
    pattern3 = re.compile(r'ct_post_op_(\d+)')
    match3 = re.search(pattern3, curated_input_path)
    if match3:
        run_elt += match3.group(1)
    pattern = re.compile(r'SPL008_Post_Op_([\d]+)_')
    match = re.search(pattern, input_path)
    if match:
        run_elt += match.group(1)
    pattern = re.compile(r'SPL008_Post_Op_CT_77_([\d]+)_')
    match = re.search(pattern, input_path)
    if match:
        run_elt += match.group(1)
    return run_elt


def extract_sub(str, participants_dict):
    """
    Returns the participant code of a string, raises an assertion error if it cannot find it in the filename

    Package
    ----
    `utils.filename_reader.py`

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
    #filename = str.split("/")[-1]
    #split = filename.split("_")
    #old_name = split[0]
    #i=1


    #   specific to lumbar_healthy_fmri
    if str.split('/')[1] == "Vibrations":
        old_sub = str.split('/')[2]
    else:
        old_sub = str.split('/')[1]
    if old_sub in participants_dict.keys():
        sub = participants_dict[old_sub]
    else:
        sub=''
    if str.split('/')[1] == "_Others":
        pattern1 = re.compile(r'/(sub-[\d]*)/')
        match1 = re.search(pattern1,str)
        if match1:
            sub = match1.group(1).lower()
        else:
            sub=''
    return sub

    #while (old_name not in participants_dict.keys()) and i <len(split):
    #    old_name += '_' + split[i]
    #    i+=1
    #if old_name not in participants_dict.keys():
    #    return ''
    #else:
    #    return participants_dict[old_name]

def extract_type(input_path, debug=False):
    """
    Returns the suspected type of the specified file.

    Package
    ----
    `utils.filename_reader.py`

    Parameters
    --------
        input_path : str,
            a path/filename string
        debug : bool, default = False
            prints variables if set to True
    
    Returns
    --------
        type: str,
            the type of the specified file
    """
    filename = remove_extension(input_path.split('/')[-1]).lower()
    dirs = '/'.join(input_path.split('/')[:-1]).lower()
    extension = extract_extension(input_path)
    keywords = [keyword.lower() for keyword in filename.split('_')]
    root_dirs_keywords = [keyword.lower() 
                      for dir in input_path.split('/')[:-1:]
                      for keyword in dir.split('_') ]
    if debug:
        print(root_dirs_keywords)
    
    
    if extension in ['.py', '.ipynb', '.pyc', '.sh', '.fsf' ] or 'scripts' in root_dirs_keywords or 'scripts' in filename :
        type = 'code'
    elif extension in ['.avi', '.png', '.pdf', '.mp4', '.pptx', '.docx', '.ai', '.jpg'] or filename == 'screenshots':
        type = 'misc_derivative'
    elif 'dti' in keywords or extension in ['.bval', '.bvec']:
        type = 'dti'
    
    elif extension == '.smash' or 'selectivity' in filename or 'simulations_result' in filename:
        type = 'simulation'
    
    elif ('rx' in root_dirs_keywords or 'rx' in keywords or 'x_ray' in input_path.lower()) and (not 'ct_rx' in input_path.lower()):
        type = 'xray'


    elif extension in ['.stl', '.blend', '.blend1', '.obj', '.mtl','.glb', '.vdb', '.ply', '.step', '.3ds', '.iges', '.model', '.sab'] or filename in ['3d_generation', '_all_stls', 'blender'] or '3d_generation' in input_path.lower():
        type = 'modelling'

    elif ('ct' in keywords or 'ct' in root_dirs_keywords) and extension in ['.nii.gz', '.zip', '.json']:
        if 'seg' in keywords or 'seg' in root_dirs_keywords or 'tissues' in root_dirs_keywords or 'voxelized' in filename or 'segmentation' in input_path.lower() or get_seg_info(input_path) != "":
            type = 'ct_segmentation'
        elif 'bin' in keywords or 'metal' in keywords: 
            ### this case might be specific to t2g_sub02 !!
            type= 'ct_segmentation' 
        else:
            type = 'ct'
    
    #specific to up2003
    elif "bold_moco_p2" in filename or "iso_tr2_pat2_on_wip_advphysio" in filename or "_bold_" in filename:
        type = "func"
    
    elif filename in ['order_runs', 'notes'] or 'timings' in root_dirs_keywords or 'physiological' in filename or 'physiological' in root_dirs_keywords:
        type = "func"

    elif ('structural' in keywords or 'structural' in root_dirs_keywords or 'mri' in keywords or 'mri' in root_dirs_keywords) and (not 'functional' in root_dirs_keywords):
        pattern = re.compile(r'dilate_\d*')
        if re.search(pattern, filename) or "wimagine_covers_center" in filename or "visualization" in root_dirs_keywords or "/straighten_with_seg/" in input_path.lower():
            type = "anat_derivatives"
        elif 'seg' in keywords or 'mask' in keywords or 'tissues' in root_dirs_keywords or 'seg' in root_dirs_keywords or 'segmentations' in root_dirs_keywords or ('segmentation' in root_dirs_keywords and (not 'im' in root_dirs_keywords ) and (not 'im_straight' in root_dirs_keywords))or 'voxelized' in filename:
            type = 'anat_segmentation'
        elif "spinal_levels" in dirs:
            type = 'anat_segmentation'
        elif 'betted' in filename or 'transf' in filename or 'template' in filename or 'preprocessed' in input_path.lower() or 'pre_processed' in input_path.lower() or extension in ['.mat'] or 'im_straight' in root_dirs_keywords:
            if debug:
                print(filename)
            type = 'anat_derivatives'
        elif filename in ['straight_ref', 'warp_straight2curve', "warp_curve2straight"]:
            type = "anat_derivatives"
        elif "straightening" in root_dirs_keywords or "straighten" in root_dirs_keywords:
            type = "anat_derivatives"
        else:
            type = 'anat'


    elif 'restingstate' in keywords or 'fmri' in input_path.lower() or 'functional' in input_path.lower() or 'physiolog' in filename or get_func_task(input_path) != '' or 'bold_moco_p2' in filename:
        if filename in ["fmri", "timings", "order_runs"] or 'bold_moco_p2' in filename:
            type = 'func'
        elif ('seg' in root_dirs_keywords or 'segmentation' in root_dirs_keywords or 'segmentation_functional' in input_path.lower() or get_seg_info(input_path) != '') and extension != ".feat":
            type = 'func_segmentation'
        elif 'thresh_zscores' in input_path.lower() or "zstat1" in input_path.lower():
            type = 'func_derivatives'
        elif extension == '.feat' or 'thresh_zstat1_reg' in filename or 'acompcor' in filename or 'rmsctp0fmri' in filename:
            type = 'func_derivatives'
        else:
            type = 'func'
    
    elif extension == '.feat' or 'thresh_zstat1_reg' in filename or 'acompcor' in filename or 'rmsctp0fmri' in filename:
        type = 'func_derivatives'
    
    

    
    elif 'spinal_level' in dirs or sum([word in filename for word in ['roots_out','roots_rootlets', 'roots_seg_to_centerline', 'centerline']])>=1 or ('intersections' in filename) or ('segmentation' in input_path.lower()) :
        type = 'anat_segmentation'

    

    elif extension in ['.nii.gz', '.nii']:
        if get_seg_info(input_path) != '':
            type = 'anat_segmentation'
        else:
            type = 'anat'
    elif 'model' in root_dirs_keywords:
        type = 'modelling'
    else:
        type = 'misc'
    
    return type

def get_ses(input_path, debug=False):
    """
    Returns the session identifier (specific to lumbar_healthy_fmri)

    Package
    ----
    `utils.filename_reader.py`
    
    Parameters
    --------
        input_path : str,
            a path/filename string
        debug : bool, default = False
            prints variables if set to True
    
    Returns
    --------
        ses: str,
            the session of the specified file
    """
    ses = ''
    regexps = [
        r'/(Ankle|Hip|Knee|ankle|hip|knee)_(Ext|Flex|ext|flex)',
        r'/Structural_([^/]*)',
        r'/(Vibrations)/',
        r'/(Ankle|Hip|Knee)_\d'
    ]
    for regexp in regexps:
        pattern = re.compile(regexp)
        match = re.search(pattern,input_path)
        if match and ses == '':
            ses = match.group(1).lower()

    if ses == 'vibrations':
        ses = 'vibration'
    if input_path.split('/')[1] == "_Others":
        pattern1 = re.compile(r'/ses-([\d]*)/')
        match1 = re.search(pattern1,input_path)
        if match1:
            ses = match1.group(1).lower()
        else:
            ses=''
    return ses


def get_category(input_path, debug=False):
    """
    Returns additional information on the data

    see `utils/category.json` for the searched expressions

    Package
    ----
    `utils.filename_reader.py`
    
    Parameters
    --------
        input_path : str,
            a path/filename string
        debug : bool, default = False
            prints variables if set to True
    
    Returns
    --------
        category: str,
            the category of the specified file
    """

    category = get_path_info(
        path= input_path,
        data_path='utils/category.json',
        debug=debug
    )
    return category



def get_seg_info(input_path, debug=False):
    """
    Returns additional information about a segmentation (if it is a mask, which part was targeted, which tools were used to segment, ...)
    
    see `utils/seg_info.json` for the searched expressions

    Package
    ----
    `utils.filename_reader.py`
    
    Parameters
    --------
        input_path : str,
            a path/filename string
    
    Returns
    --------
        seg_info: str,
    """
    seg_info = get_path_info(
        path= input_path,
        data_path='utils/seg_info.json',
        debug=debug
    )
    
    return seg_info



def get_func_task(input_path, debug=False):
    """
    Returns the task performed for fMRI

    Package
    ----
    `utils.filename_reader.py`
    
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
    func_task = ''
    if len(input_path.split('/')[1]) >= 2:
        if input_path.split('/')[1] == "_Others":
            pattern1 = re.compile(r'task-([^_]*)_')
            match1 = re.search(pattern1,input_path)
            if match1:
                func_task = match1.group(1).lower()
    
    func_task += get_path_info(
        path= input_path,
        data_path='utils/func_task.json'
    )

    pattern = re.compile(r'/Vibrations/.*/(Ankle|Hip|Knee)_\d_(ext|flex)')
    match = re.search(pattern,input_path)
    if match:
        func_task = match.group(1).lower() + '_' + match.group(2) + '_' + 'vibration'

    pattern = re.compile(r'/Vibrations/.*/(Ankle|Hip|Knee)_\d/')
    match = re.search(pattern,input_path)
    if match:
        func_task = match.group(1).lower() + '_' + 'vibration'

    pattern = re.compile(r'task-VibStim_seq(Ankle|Hip|Knee)')
    match = re.search(pattern,input_path)
    if match:
        func_task = match.group(1).lower() + '_' + 'vibration'
    
    pattern = re.compile(r'-(ankle|knee|hip)-(flex|ext)-(A|P)-(1|2)\.')
    match = re.search(pattern,input_path)
    if match:
        func_task = match.group(1).lower() + '_' + match.group(2).lower() +'_' + match.group(3).lower()

    pattern = re.compile(r'/Vibrations/.*/(Ankle|Knee|Hip)_(1|2)\.')
    match = re.search(pattern,input_path)
    if match:
        func_task = match.group(1).lower() + '_' "vibration"

    #specific to lumbar_health_fmri
    to_replace = ["_flex_", "_ext_", "_p", "_a"]
    replacements = ["_flexion_", "_extension_", "_passive", "_active"]
    for idx, string in enumerate(to_replace):
        func_task = func_task.replace(string, replacements[idx])
    return func_task


def get_func_info(input_path):
    """
    Returns additional information about fMRI 

    Package
    ----
    `utils.filename_reader.py`    
    
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
    Returns the suffix for the new path, should contain information about the imaging sequence and/or the type of signal, or anything supplementary

    Package
    ----
    `utils.filename_reader.py`
    
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
        string = string.replace(s,'')

    
    keywords = [keyword.lower() for keyword in filename.split('_')]
    extension = extract_extension(string)

    if type == 'func' and extension in ['.json', '.nii.gz']:
            suffix = 'bold'
    
    elif type == 'dti':
        suffix = 'dti'
    
    elif 'ct' in type and 'pre_op_ct' not in filename:
        suffix = 'ct'


    elif 't2' in keywords and 'spc' in keywords and 'zoomit' in keywords:
        suffix = 't2_spc_zoomit'
    
    elif 't2' in keywords and 'space' in keywords and 'zoomit' in keywords:
        suffix = 't2_space_zoomit'
        if debug:
            print('uçzefuhieui',keywords[-1])
        if keywords[-2] == 'zoomit':
            suffix += '_' + keywords[-1]
    
    else:
        suffix = ''

    if debug:
        print(filename)
    
    additional = get_path_info(string, 'utils/suffix.json')
    if suffix=='':
        suffix = additional
    else:
        if additional not in suffix:
            suffix = suffix + '_' + additional

    extras = data['extra']
    extras += ['v0' + str(i) for i in range(10)]
    extras += ['v' + str(i) for i in range(10)]

    for extra in extras:
        if extra in string.lower():
            if suffix == '':
                suffix = extra
            else:
                if extra not in suffix:
                    suffix = suffix + '_' + extra
    suffix = suffix.strip('_')
    suffix = suffix.replace('__', '_')
    return suffix
    
##################################################################################################################################################
################################ Booleans ########################################################################################################

def is_date(str):
    """
    Returns True if the input string is a date (with the common typo 2025 -> 205 taken into account)

    Returns False otherwise

    Package
    ----
    `utils.filename_reader.py`

    Parameters
    --------
        str : str,
            a string supposedly containing a date (between 2000 and 2025)
    
    Returns
    --------
        is_date_bool: bool,
    """
    if str.isdecimal():   
        if len(str)==14 or len(str) == 8: #correctly formatted date (long or short)
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
    Package
    ----
    `utils.filename_reader.py`

    Parameters
    --------
        type : str,
            a type, like 'anat' or 'modelling'
    
    Returns
    --------
        is_derivative_bool: bool,
    """
    return 'segmentation' in type or (type in ['modelling', 'simulation']) or 'derivative' in type

def is_localizer(input_path):
    """
    Package
    ----
    `utils.filename_reader.py`

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
    filename = remove_extension(input_path).split('/')[-1].lower()
    try:
        last_dir = input_path.split('/')[-2].lower()
    except:
        last_dir = ''
    is_localizer_bool = 'localizer' in last_dir or 'localizer' in filename


    return is_localizer_bool

def is_other(str, debug=False):
    """
    Package
    ----
    `utils.filename_reader.py`

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
    
def is_a_previous_version(input_path):
    """
    Package
    ----
    `utils.filename_reader.py`
    
    Parameters
    --------
        input_path : str,
            a path/filename string
    
    Returns
    --------
        is_a_previous_version_bool: bool,
            True iff the file is a previous version
    """
    b1 = 'previous_version' in input_path.lower() 
    b2 = 'version_2024' in input_path.lower() 
    b3 = '_previous' in input_path.lower().split('/')
    is_a_previous_version_bool = b1 or b2 or b3
    return is_a_previous_version_bool

def is_tmp(input_path):
    """
    Package
    ----
    `utils.filename_reader.py`
    
    Parameters
    --------
        input_path : str,
            a path/filename string
    
    Returns
    --------
        is_tmp_bool: bool,
            True iff the file is suspected to be a temporary file (contains 'tmp' in its path)
    """
    is_tmp_bool = 'tmp' in input_path.lower() or 'test' in input_path.lower()
    return is_tmp_bool





#########################################################################################################################
################### INFO DICT ###########################################################################################

def generate_new_path(old_path, sub, run, type, category, seg_info, func_task, func_info, suffix, extension, is_tmp_bool, is_derivative_bool, is_localizer_bool, is_other_bool, is_a_previous_version_bool):
    """
    Returns a new_path string given all the information in the arguments
    
    Package
    ----
    `utils.filename_reader.py`
    
    Parameters
    --------
        old_path : str,
        sub : str,
        ses : str,
        run : str,
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

    sub_ses_folder = sub
    sub_ses_file = sub


    # for lumbar_healthy below
    #if ses == '':
    #    sub_ses_folder = sub
    #    sub_ses_file = sub
    #else:
    #    sub_ses_folder = sub + '/' + 'ses-' + ses
    #    sub_ses_file = sub + '_' + 'ses-' + ses

    if is_tmp_bool:
        new_path = 'tmp' + old_path

    elif type =='code':
        try:
            if old_path.lower().split('/')[-1] != 'scripts':
                simplified_old_path = '/' + '_'.join(old_path.lower().split('/')[:-1]).strip('_') + '/' + old_path.lower().split('/')[-1]
            else:
                simplified_old_path = '/' + '_'.join(old_path.lower().split('/')[:-1]).strip('_')
        except:
            simplified_old_path = old_path.lower()
        try:
            if simplified_old_path.split('_')[0] in ['/up200' + str(i) for i in range(1,5) ]:
                simplified_old_path = '_'.join(simplified_old_path.split('_')[1:])
        except:
            simplified_old_path = old_path.lower()
        for i in range(1,5):
            sub_code = 'up200' + str(i)
            while sub_code in simplified_old_path:
                simplified_old_path = simplified_old_path.replace(sub_code, '')
        while '__' in simplified_old_path:
            simplified_old_path = simplified_old_path.replace('__', '_')
        if sub == '':
            new_path = 'code' + simplified_old_path
        else:
            new_path = 'code/' + sub_ses_folder + simplified_old_path
    
    elif type in ['misc','modelling']:
        new_path = 'derivatives/' + type

        if old_path.lower().split('/')[1] in ['up200' + str(i) for i in range(1,5) ]:
            simplified_old_path = '/'.join(old_path.split('/')[2:]).lower()
        else:
            simplified_old_path = old_path.lower()

        for string in STRS_TO_REMOVE_FOR_MODELLING_NEW_PATH:
            simplified_old_path = simplified_old_path.replace(string.lower(),'')
        
        if sub =='':
            new_path += simplified_old_path
        else:
            new_path += '/' + sub_ses_folder + '/' + simplified_old_path
    else:
        if is_derivative_bool:
            new_path += 'derivatives/'
            if 'segmentation' in type:
                new_path += 'segmentation/' + sub_ses_folder + '/' + type.split('_')[0] + '/'
            elif 'derivatives' in type:
                new_path += type.split('_')[0] + '/' + sub_ses_folder +'/'
            else:
                new_path += type +'/' + sub_ses_folder + '/'
        else:
            new_path += sub_ses_folder + '/' + type + '/'
            if ('dicom' in old_path.lower() or type in ['anat','func','ct']) and extension==".zip":
                new_path += 'dicom/'

        if is_localizer_bool:
            new_path+= '_localizer/'
        elif is_other_bool:
            new_path += '_other/'
        elif is_a_previous_version_bool:
            new_path += '_previous_version/'
        
        if run != '':
            run_element = 'run-' +run
        else:
            run_element = ''
        suffix_elt = suffix
        if 'segmentation' in type and suffix in seg_info:
            suffix_elt = ''
        if suffix in func_info:
            suffix_elt = ''
        if 'func' in type:
            if func_task != '':
                task_elt = 'task-' + func_task
            else:
                task_elt = ''
            if seg_info in func_info:
                seg_info= ''
            elif func_info in seg_info:
                func_info= ''
            elements = [sub_ses_file, category, run_element, task_elt, func_info, seg_info, suffix_elt]  
        elif type == 'simulation' and 'selectivity' in old_path.split('/')[-1].lower():
            end = old_path.split('/')[-1].lower().strip('_')
            elements = [sub_ses_file, category, end]
        else:
            elements = [sub_ses_file, category, run_element, seg_info, suffix_elt]

        new_path += '_'.join([element for element in elements if element!= '']) + extension
        new_path = new_path.replace('//', '/')
    
    return new_path.replace('//', '/')


def create_filename_dict(str, participants_dict, **kwargs):
    """
    Returns a dict containing information and sorting instructions ("new_path") given a path string and the participants dict.
    Handles suspected tmp files (contain 'tmp' in their path)

    Package
    ----
    `utils.filename_reader.py`
    
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
        ses : str,
            precises the session
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
    run = extract_run(str)
    out["run"] = run

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
        run,
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
