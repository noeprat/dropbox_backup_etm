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
    elif 'ct' in keywords:
        if 'seg' in keywords:
            type = 'ct_segmentation'
        else:
            type = 'ct'
    elif extension == '.smash':
        type = 'simulation'
    elif extension == '.feat' or 'normalization' in  root_dirs_keywords or 'thresh_zstat1_reg' in filename or 'acompcor' in filename or 'rmsctp0fmri' in filename:
        type = 'func_derivatives'
    elif 'segmentation_functional' in str.lower() or ('functional' in root_dirs_keywords and 'seg' in filename):
        type = "func_segmentation"
    elif 'restingstate' in keywords or 'fmri' in keywords or 'functional' in str.lower():
        type = 'func'
    elif 'structural' in keywords or 'structural' in root_dirs_keywords or 'mri' in keywords or 'mri' in root_dirs_keywords:
        if 'seg' in keywords or 'mask' in keywords or 'tissues' in root_dirs_keywords:
            type = 'anat_segmentation'
        else:
            type = 'anat'

    #special to T2G, rules may not apply to later dirs
    elif extension in ['.stl', '.blend', '.obj', '.mtl','.glb'] or filename in ['3d_generation', '_all_stls']:
        type = 'modelling'
    elif 'spinal_level' in dirs or filename in ['roots_out','roots_rootlets', 'roots_seg_to_centerline'] or ('intersections' in filename):
        type = 'anat_segmentation'

    

    elif extension=='.nii.gz':
        type = 'anat'
    
    else:
        type = 'misc'
    
    return type

def get_category(str):
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
    if is_localizer(str):
        return 'localizer'
    filename = remove_extension(str.split('/')[-1]).lower()
    #print('filename: ', filename)
    
    dir_path = '/'.join(str.split('/')[:-1:]).lower()
    #print('dir_path',dir_path)
    
    categories = []
    
    # make sure to have the expressions containing the ones before first
    expressions_to_search_in_dirs = [
        'for_3d_import',
        'not_for_import',
        'for_import',
        'ssl_tissues_post_pro_step_02',
        'ssl_tissues_post_pro_step_01',
        'ssl_tissues_post_pro_02',
        'ssl_tissues_post_pro_01',
        'ssl_tissues',  # must be after "ssl_tissues_post_pro_01"
        'tissues_sct',
        'tissues'
        'axobl_sacrum_deepseg',
        'axobl_sacrum'
        'ax_lspine_deepseg'
        'ax_lspine',
        'deepseg',
        'for_making_levels',
        'lumbar',
        'ax_lspine',
        'ax_obl_sacrum',
        'bladder',
        'individual_spinal_levels',
        'resting_state',
        'mp2rage',
        'model_spine',
        'for_ilaria',
        'segmentation_sct_poly_0'
    ]

    expressions_to_search_in_filename = [
        'ssl_tissues_post_pro_step_02',
        'ssl_tissues_post_pro_step_01',
        'ssl_tissues_post_pro_02',
        'ssl_tissues_post_pro_01',
        'ssl_tissues',  # must be after "ssl_tissues_post_pro_01"
        'axobl_sacrum_deepseg',
        'axobl_sacrum',
        'ax_lspine_deepseg',
        'ax_lspine',
        'deepseg',
        'for_making_levels',
        'lumbar',
        'ax_lspine',
        'ax_obl_sacrum',
        'bladder',
        'individual_spinal_levels',
        'resting_state'
        'total_spineseg',
        'lumbar',
        'cs4p6',
        'wip19_mp2rage',
        'synthseg',
        "seg_post_pro",
        'post_pro',
        'structural_tissues'

    ]

    for dir_expression in expressions_to_search_in_dirs:
        if dir_expression in dir_path:
            categories.append(dir_expression)
            #print('found dir expression: ', dir_expression)
            break

    

    for filename_expression in expressions_to_search_in_filename:
        if (filename_expression in filename) and (filename_expression not in categories):
            categories.append(filename_expression)
            #print('found filename expression', filename_expression)
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
    filename = remove_extension(str.split('/')[-1]).lower()
    
    # curate filename to avoid confusions
    strs_to_ignore = [
        'root_segments'
    ]
    
    for s in strs_to_ignore:
        filename = filename.replace(s, '')
    
    
    dir_path = '/'.join(str.split('/')[:-1]).lower()

    
    if len(filename.split('_'))>6:
        end_of_filename = '_'.join(filename.split('_')[-6:])
    else:
        end_of_filename= filename
    
    expressions_to_search_in_dirs = [
        'segmentator_tissues',
        'seg_model_9_roots_as_one_entity_small',
        'seg_model_9_roots_as_one_entity',
        'seg_model_9',
        'seg_model_10_roots_by_spinal_levels_small',
        'seg_model_10_roots_by_spinal_levels',
        'seg_model_10',
        'seg_model_5',
        'seg_model_1'
    ]

    expressions_to_search_in_filename = [
         # the largest expressions first
        'seg_model_9_roots_as_one_entity_small',
        'seg_model_9_roots_as_one_entity',
        'seg_model_9',
        'seg_model_10_roots_by_spinal_levels_small',
        'seg_model_10_roots_by_spinal_levels',
        'seg_model_10',
        't8_l3',
        't12_s1',

    ]
    

    expressions_to_search_at_end_of_filename = [
        "seg_masked_fat_candidate_1",
        "seg_masked_fat_candidate_2",
        "seg_masked_fat_candidate_3",
        "seg_masked_fat",
        "seg_masked_wm",
        "seg_masked_roots",
        "seg_masked_csf_s4l",
        "seg_masked_csf",
        "seg_discs",
        "seg_masked",
        "seg",

        "csf_s4l_mask",
        "csf_s4l",
        "roots_mask",
        "roots",
        "wm_mask",
        "step1_canal",
        "step1_cord",
        "step1_levels",
        "step1_output",
        "step2_output",

        'spinal_level_t8l3_wm',
        'spinal_level_t8l3',
        'spinal_level_l1',
        'spinal_level_l2',
        'spinal_level_l3',
        'spinal_level_l4',
        'spinal_level_l5',
        'spinal_level_more_caudal',
        'spinal_level_more_rostral',
        'spinal_level_s1',
        'spinal_level_s2',
        'spinal_level_s3',
        'spinal_level_s4',
        'spinal_level_t11',
        'spinal_level_t12',

        't8l3_wm',
        't8l3',
        't8_l3',
        't12_s1',
        'l1',
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
        't11',
        't12',
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
        'vertebrae',
        
        "full_wm_gm",
        "full_gm",
        "full_wm",
        "left_gm",
        "right_gm",
        "left_wm",
        "right_wm",
        "brain_wm_gm_padded",
        "brain_wm_gm",
        "left_cerebellum_gm",
        "right_cerebellum_gm",
        "left_cerebellum_wm",
        "right_cerebellum_wm",
        "cerebellum_gm",
        "cerebellum_wm",
        "left_wm",
        "right_gm",
        "gm_padded",
        "wm_padded",
        "wm",
        "gm",
        "csf",
    ]

    seg_infos = []
    for dir_expression in expressions_to_search_in_dirs:
        if dir_expression in dir_path:
            
            seg_infos.append(dir_expression)
            break

    for filename_expression in expressions_to_search_in_filename:
        if filename_expression in filename:
            if filename_expression not in seg_infos:
                seg_infos.append(filename_expression)
                break
    
    for filename_expression in expressions_to_search_at_end_of_filename:
        if filename_expression in end_of_filename:
            if filename_expression not in seg_infos:
                seg_infos.append(filename_expression)
                break

    seg_info = '_'.join(seg_infos)
    return seg_info



def get_func_task(str, debug=False):
    """
    Returns the task performed for fMRI
    
    
    Parameters
    --------
        str : str,
            a path/filename string
    
    Returns
    --------
        func_task: str,
    
    Possible func_task (so far)
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
    filename = remove_extension(str.split('/')[-1]).lower()
    
    dir_path = '/'.join(str.split('/')[:-1]).lower()
    if debug:
        print('filename, ', filename)
        print('dir_path', dir_path)


    
    if len(filename.split('_'))>6:
        end_of_filename = '_'.join(filename.split('_')[-6:])
    else:
        end_of_filename= filename
    
    if debug:
        print('end_of_filename, ', end_of_filename)
    
    expressions_to_search_in_dirs = [
        'right_ankle',
        'left_ankle',
        'right_knee',
        'left_knee',
        'right_hip',
        'left_hip',
        'right_grasp',
        'left_grasp',
        'functional_rest'
    ]

    expressions_to_search_in_filename = [
         # the largest expressions first
        'right_ankle',
        'left_ankle',
        'right_knee',
        'left_knee',
        'right_hip',
        'left_hip',
        'right_grasp',
        'left_grasp',
        'restingstate'
    ]
    
    if debug:
        print('left_ankle' in dir_path)
    expressions_to_search_at_end_of_filename = []

    seg_infos = []
    for dir_expression in expressions_to_search_in_dirs:
        if debug:
            print('dir_expression, ',dir_expression)
        if dir_expression in dir_path:
            
            seg_infos.append(dir_expression)
            
            break

    

    for filename_expression in expressions_to_search_in_filename:
        if filename_expression in filename:
            if filename_expression not in seg_infos:
                seg_infos.append(filename_expression)
                if debug:
                    print('filename_exp, ', filename_expression)
                break
    
    for filename_expression in expressions_to_search_at_end_of_filename:
        if filename_expression in end_of_filename:
            if filename_expression not in seg_infos:
                seg_infos.append(filename_expression)
                if debug:
                    print('eof_exp, ', filename_expression)
                break

    seg_info = '_'.join(seg_infos)
    return seg_info


def get_func_info(str):
    """
    Returns additional information about fMRI 
    
    
    Parameters
    --------
        str : str,
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
    filename = remove_extension(str.split('/')[-1]).lower()
    
    dir_path = '/'.join(str.split('/')[:-1]).lower()

    
    if len(filename.split('_'))>6:
        end_of_filename = '_'.join(filename.split('_')[-6:])
    else:
        end_of_filename= filename
    
    expressions_to_search_in_dirs = [
        
    ]

    expressions_to_search_in_filename = [
         # the largest expressions first
        'output_smooth_5mm_no_reg',
        'output_smooth_3mm',
        'thresh_zstat1_reg_03',
        'thresh_zstat1_reg_04',
        'thresh_zstat1_reg_05',
        'thresh_zstat1_reg_06',
        'thresh_zstat1_reg_07',
        'thresh_zstat1_reg',
        'func_mean_seg',
        'func_mean_reg',
        'func_mean',
        'warp_anat2fmri',
        'warp_fmri2anat',
        'lumbar',
        'mean_for_seg_seg',
        'mean_for_seg',
        'rmsctp0fmri_mean_all',
        'rmsctp0fmri'
    ]
    

    expressions_to_search_at_end_of_filename = [
        'brain_wm_gm_reg',
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
    ]

    seg_infos = []
    for dir_expression in expressions_to_search_in_dirs:
        if dir_expression in dir_path:
            
            seg_infos.append(dir_expression)
            break

    

    for filename_expression in expressions_to_search_in_filename:
        if filename_expression in filename:
            if filename_expression not in seg_infos:
                seg_infos.append(filename_expression)
                break
    
    for filename_expression in expressions_to_search_at_end_of_filename:
        if filename_expression in end_of_filename:
            if filename_expression not in seg_infos:
                seg_infos.append(filename_expression)
                break

    seg_info = '_'.join(seg_infos)
    return seg_info


def get_suffix(str, debug=False):
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
        suffix = 'ct'
    
    elif 'func' in type and type != 'func_derivatives':
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


    elif 't2' in keywords and 'spc' in keywords and 'zoomit' in keywords:
        suffix = 't2_spc_zoomit'

    expressions_to_search_in_filename = [
        't2_space',
        't2_tse',
        't2_trufi3d_comp',
        't2_trufi3d_t8',
        't2_trufi3d_t12',
        't2_trufi3d',
        't2_gre',
        't1_tfe',
        't1_spc3d',
        'b_ffe',
        't2_3d_tra_vista',
        't2w_ffe',
        'ffe',  # must be after 'b_ffe' etc.
        'brain_aahead_scout',
        'roots_out',
        'roots_rootlets', 
        'roots_seg_to_centerline',
        'trufi3d',
        'intersections_voxel_mod',
        'intersections_voxel',
        'intersections_world',
        'root_segments_mod',
        'root_segments',
        'dl',
        'dr',
    ]
    if debug:
        print(filename)
    
    suffix = ''
    for filename_expression in expressions_to_search_in_filename:
        if debug:
            print('expression',filename_expression)
        if filename_expression in filename and filename_expression not in suffix:
            if suffix == '':
                suffix = filename_expression
            else:
                suffix = suffix + '_' + filename_expression
    if 'corrected' in str.lower():
        if suffix == '':
            suffix = 'corrected'
        else:
            suffix = suffix + '_corrected'
    
    if 'version_2024' in str.lower():
        if suffix == '':
            suffix = 'version-2024'
        else:
            suffix = suffix + '_version-2024'

    return suffix
    
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
            elif type =='func_derivatives':
                new_path += 'func/' + sub +'/'
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
