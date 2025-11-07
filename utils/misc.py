from filename_reader import remove_extension
import json

def pick_largest_str_in_list(str_list):
    res = ''
    for s in str_list:
        if len(s) > len(res):
            res = s
    return res

def get_path_info(path, data_path):
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
    expressions_to_search_in_dirs = data["to_search_in_dirs"]
    expressions_to_search_in_filename = data["to_search_in_filename"]
    expressions_to_search_at_end_of_filename = data["to_search_at_end_of_filename"]
    
    path_infos = []

    dir_expressions = [dir_expression for dir_expression in expressions_to_search_in_dirs if dir_expression in dir_path]
    path_infos.append(pick_largest_str_in_list(dir_expressions))

    filename_expressions = [filename_expression 
                            for filename_expression in expressions_to_search_in_filename 
                            if filename_expression in filename and (filename_expression not in path_infos)]
    path_infos.append(pick_largest_str_in_list(filename_expressions))

    end_of_filename_expressions = [filename_expression 
                            for filename_expression in expressions_to_search_at_end_of_filename 
                            if filename_expression in end_of_filename and (filename_expression not in path_infos)]
    path_infos.append(pick_largest_str_in_list(end_of_filename_expressions))

    path_info = '_'.join(path_infos)
    return path_info.strip('_')
