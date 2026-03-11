import json
import os

def extract_extension(str):
    """
    Returns the extension of the filename / path string, dot included,
    returns an empty string if there is no extension (folders or specific files)

    Package
    ----
    `utils.misc.py`

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
    
    Package
    ----
    `utils.misc.py`

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

def pick_largest_str_in_list(str_list):
    """
    Returns the longest string in a list of strings (or any object from which `len` can be applied)

    Package
    ----
    `utils.misc.py`

    Parameters
    --------
        str_list : list(str),

    Returns
    --------
        res: str,
            longest element in str_list
    """
    res = ''
    for s in str_list:
        if len(s) > len(res):
            res = s
    return res

def get_path_info(path, data_path, debug=False):
    """
    Returns the infos contained in `path` by searching matching expressions from the json in `data_path`

    Package
    ----
    `utils.misc.py`

    Parameters
    --------
        path : str,
            path to dropbox file
        data_path : str,
            path to a json containing the strings to search in `path`
            
            *required structure:*
            ```
            {
                "to_ignore": [
                    "exp1",
                    "exp2",
                    ...
                ],
                "to_search_in_dirs": [
                    "dir_exp1",
                    "dir_exp2",
                    ...
                ],
                "to_search_in_filename": [
                    "filename_exp1",
                    "filename_exp2",
                    ...
                ],
                "to_search_at_end_of_filename": [
                    "end_of_filename_exp1",
                    "end_of_filename_exp2",
                    ...
                ]
            }
            ```
    
    Returns
    --------
        path_info, str
            path_info (e.g. func_info, seg_info, func_task, category)
    """
    with open(data_path, 'r') as f:
        data = json.load(f)

    curated_path = path.replace(' ', '_').lower()

    strs_to_ignore = data["to_ignore"]

    for s in strs_to_ignore:
        curated_path = curated_path.replace(s,'')
    
    if debug:
        print('curated path', curated_path)

    filename = remove_extension(curated_path.split('/')[-1])
    dir_path = '/'.join(curated_path.split('/')[:-1])
    END_OF_FILENAME_LENGTH = 8
    if len(filename.split('_'))>END_OF_FILENAME_LENGTH:
        end_of_filename = '_'.join(filename.split('_')[-END_OF_FILENAME_LENGTH:])
    else:
        end_of_filename= filename

    if debug:
        print('curated filename: ', filename)
        print('curated eof', end_of_filename)
    
    expressions_to_search_in_dirs = data["to_search_in_dirs"]
    expressions_to_search_in_filename = data["to_search_in_filename"]
    expressions_to_search_at_end_of_filename = data["to_search_at_end_of_filename"]
    
    path_infos = []

    for dir in dir_path.split('/'):

        dir_expressions = [dir_expression 
                           for dir_expression in expressions_to_search_in_dirs 
                           if dir_expression in dir and (dir_expression not in '_'.join(path_infos))]
        if debug:
            print('dir expressions: ',dir_expressions)
        chosen_dir_expression = pick_largest_str_in_list(dir_expressions)
        path_infos.append(chosen_dir_expression)
        filename.replace(chosen_dir_expression, '')
        end_of_filename.replace(chosen_dir_expression, '')
    

    filename_expressions = [filename_expression 
                            for filename_expression in expressions_to_search_in_filename 
                            if filename_expression in filename and (filename_expression not in '_'.join(path_infos))]
    chosen_filename_expression = pick_largest_str_in_list(filename_expressions)
    if debug:
        print('filename expressions: ',filename_expressions)
    path_infos.append(chosen_filename_expression)
    filename.replace(chosen_filename_expression, '')
    end_of_filename.replace(chosen_filename_expression, '')

    end_of_filename_expressions = [filename_expression 
                            for filename_expression in expressions_to_search_at_end_of_filename 
                            if filename_expression in end_of_filename and (filename_expression not in '_'.join(path_infos))]
    path_infos.append(pick_largest_str_in_list(end_of_filename_expressions))
    if debug:
        print('end_of_filename expressions: ',end_of_filename_expressions)

    path_info = '_'.join([elt.strip('_') for elt in path_infos if elt !=''])
    path_info = path_info.replace('__','_')
    path_info = path_info.strip('_')
    return path_info

def clean_up_tmpdir(debug=False):
    """
    Removes any file in `tmp_dir/`

    Package
    ----
    `utils.misc.py`
    """
    for file in os.listdir('tmp_dir/'):
        if debug:
            print(file)
        os.remove('tmp_dir/' + file)

def my_ls(dir, force_abspath=False):
    """
    Lists complete paths (files or subdirs) under `dir`
    
    Should be robust to posix or windows paths

    Package
    ----
    `utils.misc.py`
    
    Parameters
    ---
        dir : str,
            path to a directory

    Returns
    ---
        ls : list(str)
            list of paths under `dir`
    """
    l = os.listdir(dir)
    ls = []
    for entry in l:
        if force_abspath:
            ls.append(os.path.normpath(os.path.join(os.path.abspath(dir), entry)))
        else:
            ls.append(os.path.normpath(os.path.join(dir, entry)))
    return ls

def input_with_default(input_name):
    """
    Works similarly as the `input` function, but proposes a default value stored in `inputs.json`.
    An empty input will return the default value

    Updates `inputs.json` if the input is different than the default value

    Package
    ----
    `utils.misc.py`
    
    Parameters
    ---
        input_name : str,
            key under which the default value is going to be stored in inputs.json

    Returns
    ---
        to_return : str
            the effective input value
    """
    try:
        with open('inputs.json', 'r') as f:
            default_inputs = json.load(f)
    except:
        default_inputs = {}
    new_inputs = default_inputs.copy()

    if input_name in default_inputs.keys():
        if len(default_inputs[input_name]) < 100:
            res = input(input_name + ': (default: ' + default_inputs[input_name] +') \n')
        else:
            res = input(input_name + ': (default: ' + default_inputs[input_name][:100] +'...) \n')
        if res == '':
            to_return = default_inputs[input_name]
        else:
            to_return = res
            new_inputs[input_name] = res
    else:
        to_return = input(input_name + ': \n')
        new_inputs[input_name] = to_return
    try:
        with open('inputs.json', 'w')as f:
            json.dump(new_inputs, f, indent=4)
    except:
        print('could not update inputs.json')
    return to_return

