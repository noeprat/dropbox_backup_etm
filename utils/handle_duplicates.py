from .filename_reader import remove_extension, extract_extension
import json
import os

def flag_potential_duplicates(file_infos_path, flagged_path):
    """
    Saves a json in `flagged_path` flagging different files that may have the same name after sorting

    **Overwrites any existing file in `flagged_path`**


    Parameters
    --------
        file_infos_path : str,
            path to fileinfos
        flagged_path : str,
            the path where the flags will be saved (usually of the type `/file_infos/subdir/potential_duplicates-[n].json`)
    
    Saves
    --------
        flagged_path, json file
            flagged files can be found as follows: flagged_dict[file1] = list(possible duplicate files, file1 included)

    """
    with open(file_infos_path, 'r') as f:
        file_infos = json.load(f)
    
    visited = []

    out_dict = {}

    for file1 in file_infos.keys():
        file1_duplicates_list = []
        if file1 not in visited:
            

            for file2 in file_infos.keys():
                if file2 not in visited:
                    if file_infos[file1]['new_path']==file_infos[file2]['new_path']:
                        file1_duplicates_list.append(file2)
                        visited.append(file2)
            visited.append(file1)
        if len(file1_duplicates_list)>1:
            out_dict[file1] = file1_duplicates_list
        del file1_duplicates_list

    out_dirs = '/'.join(flagged_path.split('/')[:-1])
    os.makedirs(out_dirs, exist_ok=True)
    with open(flagged_path, 'w') as f:
        json.dump(out_dict, f, indent=4)


def rename_duplicates(file_infos_path, flagged_path, new_file_infos_path):
    """
    Saves a json in `new_file_infos_path` with information and sorting instructions, without two files having the same new_path

    **Overwrites any existing file in `new_file_infos_path`**


    Parameters
    --------
        file_infos_path : str,
            path to fileinfos
        flagged_path : str,
            path to a file listing potential duplicates 
        new_file_infos_path : str,
            path where the corrected file infos will be saved (usually of the type `/file_infos/subdir/file_infos-[n]_renamed_duplicates.json`)
    
    Saves
    --------
        new_file_infos_path, json file
    """
    with open(file_infos_path, 'r') as f:
        file_infos = json.load(f)
    new_file_infos = file_infos.copy()
    
    with open(flagged_path, 'r') as f:
        flagged_dict = json.load(f)
    
    for key in flagged_dict.keys():
        #print('key',key)
        for i, file in enumerate(flagged_dict[key]):
            #print('file',file)

            original_new_path = file_infos[file]['new_path']
            final_new_path = remove_extension(original_new_path) + '_duplicate-' + str(i) + extract_extension(original_new_path)
            #print('original', original_new_path)
            #print('final', final_new_path)
            new_file_infos[file]['new_path'] = final_new_path
    
    with open(new_file_infos_path, 'w') as f:
        json.dump(file_infos, f, indent=4)