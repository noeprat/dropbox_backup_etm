import dropbox
import json
import filecmp
import os
import sys

from dropbox.exceptions import AuthError
from tqdm import tqdm

from utils.globals import MAX_FILE_SIZE_FOR_COMPARISON
from utils.misc import remove_extension, extract_extension, clean_up_tmpdir

def flag_same_new_paths(file_infos_path, flagged_path):
    """
    Saves a json in `flagged_path` flagging different files that may have the same new path

    **Overwrites any existing file in `flagged_path`**
    
    Package
    ----
    `utils.handle_duplicates.py`

    Parameters
    --------
        file_infos_path : str,
            path to fileinfos
        flagged_path : str,
            the path where the flags will be saved (usually of the type `/file_infos/subdir/same_new_paths-[n].json`)
    
    Saves
    --------
        flagged_path, json file
            flagged files can be found as follows: flagged_dict[file1] = list(possible duplicate files, file1 included ; file1 appears only if possible duplicates were found)

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
                    condition1 = file_infos[file1]['new_path']==file_infos[file2]['new_path']
                    if condition1:
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

def flag_potential_duplicates(file_infos_path, flagged_path):
    """
    Saves a json in `flagged_path` flagging different files that may be duplicates (with broader criteria than having the same new path)

    **Overwrites any existing file in `flagged_path`**
    
    Package
    ----
    `utils.handle_duplicates.py`

    Parameters
    --------
        file_infos_path : str,
            path to fileinfos
        flagged_path : str,
            the path where the flags will be saved (usually of the type `/file_infos/subdir/potential_duplicates-[n].json`)
    
    Saves
    --------
        flagged_path, json file
            flagged files can be found as follows: flagged_dict[file1] = list(possible duplicate files, file1 included, only if one or several potential duplicates for file1 were found)

    """
    with open(file_infos_path, 'r') as f:
        file_infos = json.load(f)
    
    visited = []

    out_dict = {}

    for file1 in file_infos.keys():
        file1_duplicates_list = []
        filename1 = file_infos[file1]['old_path'].split('/')[-1]
        type1 = file_infos[file1]['type']
        id1 = file_infos[file1]['id']

        extension1 = extract_extension(filename1)
        try:
            is_tmp1 = file_infos[file1]['is_tmp']
        except:
            is_tmp1 = False
        try:
            seg_info1 = file_infos[file1]['seg_info']
        except:
            seg_info1 = ''
        try:
            func_task1 = file_infos[file1]['func_task']
        except:
            func_task1 = ''
        try:
            func_info1 = file_infos[file1]['func_info']
        except:
            func_info1 = ''

        if file1 not in visited and (not is_tmp1):
            for file2 in file_infos.keys():
                filename2 = file_infos[file2]['old_path'].split('/')[-1]
                type2 = file_infos[file2]['type']
                id2 = file_infos[file2]['id']
                extension2 = extract_extension(filename2)
                try:
                    is_tmp2 = file_infos[file2]['is_tmp']
                except:
                    is_tmp2 = False
                try:
                    seg_info2 = file_infos[file2]['seg_info']
                except:
                    seg_info2 = ''
                try:
                    func_task2 = file_infos[file2]['func_task']
                except:
                    func_task2 = ''
                try:
                    func_info2 = file_infos[file2]['func_info']
                except:
                    func_info2 = ''

                if file2 not in visited and (not is_tmp2):
                    condition1 = file_infos[file1]['new_path']==file_infos[file2]['new_path']
                    condition2 = filename1 == filename2 and func_task1 == func_task2
                    condition3 = (type1==type2) and (id1==id2) and (seg_info1==seg_info2) and (func_task1==func_task2) and (func_info1==func_info2)

                    if (condition1 or condition2 or condition3) and (extension1==extension2) and (type1 not in ['code', 'misc', 'modelling']):
                        file1_duplicates_list.append(file2)
                        #visited.append(file2)
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

    Package
    ----
    `utils.handle_duplicates.py`

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
    
def compare_potential_duplicates(flagged_path, actual_duplicates_path, not_downloaded_path, TOKEN, verbose=True, debug=False):
    """
    Compares potential duplicates in `flagged_path` and saves a json in `actual_duplicates_path` showing all the actual duplicates it has found, 
    and one in `not_downloaded_path` for the files it couldn't download (and that were not compared consequentially)

    **Requires a Dropbox access token**
    
    Package
    ----
    `utils.handle_duplicates.py`

    Parameters
    --------
        flagged_path : str,
            path to the flagged potential duplicates
        actual_duplicates_path : str,
            path to the actual duplicates found
        not_downloaded_path : str,
            path to the json containing the files that could not be downloaded (contains the maximal file size set in utils.handle_duplicates and the size of the files)
        TOKEN : str,
            access token for the Dropbox API
        verbose : bool, default: True,
            prints info on the dropbox authentication if set to True
        debug : bool, default: False
            set to True to print steps while debugging
    
    Saves
    --------
        actual_duplicates_path : str,
            path to the actual duplicates found
        not_downloaded_path : str,
            path to the json containing the files that could not be downloaded (contains the maximal file size set in utils.handle_duplicates and the size of the files)
    """
    if (len(TOKEN) == 0):
        sys.exit("ERROR: Looks like you didn't add your access token.")
        # Create an instance of a Dropbox class, which can make requests to the API.
    if verbose: 
        print("Creating a Dropbox object...")
    with dropbox.Dropbox(TOKEN) as dbx:
        # Check that the access token is valid
        try:
            dbx.users_get_current_account()
            if verbose:
                print('Access token is valid')
        except AuthError:
            sys.exit("ERROR: Invalid access token; try re-generating an "
                "access token from the app console on the web.")
    
    os.makedirs('tmp_dir', exist_ok=True)
    
    if os.path.exists(actual_duplicates_path):
        with open(actual_duplicates_path, 'r') as f:
            actual_duplicates = json.load(f)
    else:
        actual_duplicates = {}
    if os.path.exists(not_downloaded_path):
        with open(not_downloaded_path, 'r') as f:
            not_downloaded = json.load(f)
    else:
        not_downloaded = {
            "max_size (in octets)": MAX_FILE_SIZE_FOR_COMPARISON
        }

    with open(flagged_path, 'r') as f:
        flagged_duplicates = json.load(f)

    for key in tqdm(flagged_duplicates.keys()):
        n = len(flagged_duplicates[key])
        if debug:
            print('comparing potential duplicates for ' + key)

        from_path1 = '/source' + flagged_duplicates[key][0]
        from_path1_without_source = flagged_duplicates[key][0]
        to_path1 = 'tmp_dir/file1' + extract_extension(from_path1)

        clean_up_tmpdir(debug)

        if key not in actual_duplicates.keys():
            to_skip = False
            try:
                file1_size = dbx.files_get_metadata(from_path1).size
                assert file1_size <= MAX_FILE_SIZE_FOR_COMPARISON
                dbx.files_download_to_file(to_path1, from_path1)
                downloaded1 = True
            except:
                downloaded1 = False
                not_downloaded[from_path1_without_source] = {
                    'old_path': from_path1_without_source,
                    'size': file1_size
                }
        else:
            to_skip = True

        if downloaded1 and (not to_skip):
            actual_duplicates[from_path1_without_source] = [from_path1_without_source]
            for file2_idx in range(1, n):
                from_path2 = '/source' + flagged_duplicates[key][file2_idx]
                from_path2_without_source = flagged_duplicates[key][file2_idx]
                to_path2 = 'tmp_dir/file2' + extract_extension(from_path2)
                if debug:    
                    print(from_path1)
                    print(from_path2)
                
                try:
                    file2_size = dbx.files_get_metadata(from_path2).size
                    assert file2_size <= MAX_FILE_SIZE_FOR_COMPARISON
                    dbx.files_download_to_file(to_path2, from_path2)
                    downloaded2 = True
                except:
                    downloaded2 = False
                    not_downloaded[from_path2_without_source] = {
                            'old_path': from_path2_without_source,
                            'size': file2_size
                        }
                
                if downloaded2 and file1_size == file2_size:
                    try:
                        comp = filecmp.cmp(to_path1, to_path2, shallow=False)
                    except:
                        comp=False
                        print(from_path1 + ' not compared')
                    if comp:
                        if debug:
                            print(from_path1 + '\n    is the same as: \n' + from_path2)
                        actual_duplicates[from_path1_without_source].append(from_path2_without_source)
            with open(actual_duplicates_path, 'w') as f:
                json.dump(actual_duplicates, f, indent=4)
            
            with open(not_downloaded_path, 'w') as f:
                json.dump(not_downloaded, f, indent=4)
            os.remove(to_path1)

    with open(actual_duplicates_path, 'w') as f:
        json.dump(actual_duplicates, f, indent=4)
    
    with open(not_downloaded_path, 'w') as f:
        json.dump(not_downloaded, f, indent=4)

def regroup_actual_duplicates(actual_duplicates_path, new_duplicates_path, debug=False):
    """
    Removes redundancy in the flagged duplicates

    **Overwrites file infos in `new_duplicates_path`**
    
    Package
    ----
    `utils.handle_duplicates.py`

    Parameters
    --------
        actual_duplicates_path : str,
            path to the actual duplicates found
        new_duplicates_path : str,
            path to the new file
        debug : bool,
            set to true for debugging
    
    Saves
    --------
        new_duplicates_path, json file
            updated duplicates file
    """
    with open(actual_duplicates_path, 'r') as f:
        actual_duplicates = json.load(f)
    
    for file1 in actual_duplicates.keys():
        if len(actual_duplicates[file1]) > 1 :
            for subfile1 in actual_duplicates[file1][1:]:
                if subfile1 in actual_duplicates.keys():
                    for subfile1_duplicate in actual_duplicates[subfile1]:
                        if subfile1_duplicate not in actual_duplicates[file1]:
                            actual_duplicates[file1].append(subfile1_duplicate)
                        actual_duplicates[subfile1] = 'to_remove'
    new_duplicates = {}
    for key in actual_duplicates.keys():
        if actual_duplicates[key] != 'to_remove':
            new_duplicates[key] = actual_duplicates[key]
    with open(new_duplicates_path, 'w') as f:
        json.dump(new_duplicates, f, indent=4)

def handle_duplicates_in_file_infos(actual_duplicates_path, file_infos_path, new_file_infos_path):
    """
    Modifies the file infos after the actual duplicates have been flagged

    **Overwrites file infos in `new_file_infos_path`**

    Package
    ----
    `utils.handle_duplicates.py`

    Parameters
    --------
        actual_duplicates_path : str,
            path to the actual duplicates found
        file_infos_path : str,
            path to fileinfos
        new_file_infos_path : str,
            path to updated fileinfos (can be the same as the original fileinfos, which will update it)
    
    Saves
    --------
        new_file_infos_path, json file
            updated fileinfos
    """           
    with open(file_infos_path, 'r') as f1:
        file_infos = json.load(f1)
    
    with open(actual_duplicates_path, 'r') as f2:
        actual_duplicates = json.load(f2)

    new_file_infos = file_infos.copy()
    
    for key in actual_duplicates.keys():
        duplicate_files = actual_duplicates[key]
        if len(duplicate_files) >1:
            for file_to_discard in duplicate_files[1:]:
                old_path = file_infos[file_to_discard]['old_path']
                new_file_infos[file_to_discard]['new_path'] = 'confirmed_duplicates' + old_path
                new_file_infos[file_to_discard]['confirmed_duplicate'] = True
        
    with open(new_file_infos_path, 'w') as f:
        json.dump(new_file_infos, f, indent=4)
