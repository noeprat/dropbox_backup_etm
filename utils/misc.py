import json

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

def pick_largest_str_in_list(str_list):
    res = ''
    for s in str_list:
        if len(s) > len(res):
            res = s
    return res

def get_path_info(path, data_path, debug=False):
    """
    Returns the infos contained in `path` by searching matching expressions from `data_path`

    Parameters
    --------
        path : str,
            path to dropbox file
        data_path : str,
            path to a json containing the strings to search in `path`
    
    Returns
    --------
        path_info, str
            path_info (e.g. func_info, seg_info, func_task, category)
    """
    filename = remove_extension(path.split('/')[-1]).lower()
    dir_path = '/'.join(path.split('/')[:-1]).lower()
    if len(filename.split('_'))>6:
        end_of_filename = '_'.join(filename.split('_')[-6:])
    else:
        end_of_filename= filename

    with open(data_path, 'r') as f:
        data = json.load(f)

    strs_to_ignore = data["to_ignore"]
    for s in strs_to_ignore:
        filename = filename.replace(s, '')
        dir_path = dir_path.replace(s,'')
        end_of_filename = end_of_filename.replace(s,'')
    if debug:
        print('curated filename: ', filename)
    
    expressions_to_search_in_dirs = data["to_search_in_dirs"]
    expressions_to_search_in_filename = data["to_search_in_filename"]
    expressions_to_search_at_end_of_filename = data["to_search_at_end_of_filename"]
    
    path_infos = []

    dir_expressions = [dir_expression for dir_expression in expressions_to_search_in_dirs if dir_expression in dir_path]
    if debug:
        print('dir expressions: ',dir_expressions)
    path_infos.append(pick_largest_str_in_list(dir_expressions))
    

    filename_expressions = [filename_expression 
                            for filename_expression in expressions_to_search_in_filename 
                            if filename_expression in filename and (filename_expression not in path_infos)]
    path_infos.append(pick_largest_str_in_list(filename_expressions))
    if debug:
        print('filename expressions: ',filename_expressions)

    end_of_filename_expressions = [filename_expression 
                            for filename_expression in expressions_to_search_at_end_of_filename 
                            if filename_expression in end_of_filename and (filename_expression not in path_infos)]
    path_infos.append(pick_largest_str_in_list(end_of_filename_expressions))
    if debug:
        print('end_of_filename expressions: ',end_of_filename_expressions)

    path_info = '_'.join(path_infos)
    return path_info.strip('_')
