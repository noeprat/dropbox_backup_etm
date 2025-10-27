from .filename_reader import remove_extension, extract_extension
import json
import os

import nibabel as nib
import numpy as np
import sys

import json
import dropbox
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError
from tqdm import tqdm

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
    
def compare_potential_duplicates(flagged_path, actual_duplicates_path, TOKEN, verbose=True, debug=False):
    verbose = True
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

    for file in os.listdir('tmp_dir/'):
        if debug:
            print(file)
        os.remove('tmp_dir/' + file)
        
    actual_duplicates = {}

    with open(flagged_path, 'r') as f:
        flagged_duplicates = json.load(f)

    for key in tqdm(flagged_duplicates.keys()):
        n = len(flagged_duplicates[key])
        if debug:
            print('comparing potential duplicates for ' + key)
        for file1_idx in range(n-1):
            from_path1 = '/source' + flagged_duplicates[key][file1_idx]
            from_path1_without_source = flagged_duplicates[key][file1_idx]
            to_path1 = 'tmp_dir/file1.nii.gz'

            actual_duplicates[from_path1_without_source] = [from_path1_without_source]
            
            dbx.files_download_to_file(to_path1, from_path1)

            for file2_idx in range(file1_idx+1, n):
                from_path2 = '/source' + flagged_duplicates[key][file2_idx]
                from_path2_without_source = flagged_duplicates[key][file2_idx]
                to_path2 = 'tmp_dir/file2.nii.gz'

                if debug:    
                    print(from_path1)
                    print(from_path2)

                
                dbx.files_download_to_file(to_path2, from_path2)

                if extract_extension(from_path1) == '.nii.gz' and extract_extension(from_path2) == '.nii.gz':

                    img1 = nib.load(to_path1)
                    img2 = nib.load(to_path2)

                    data1 = img1.get_fdata()
                    data2 = img2.get_fdata()

                    if data1.shape == data2.shape:
                        if (data1==data2).all():
                            if debug:
                                print(from_path1 + '\n    is the same as: \n' + from_path2)
                            actual_duplicates[from_path1_without_source].append(from_path2_without_source)
                os.remove(to_path2)
            os.remove(to_path1)

    with open(actual_duplicates_path, 'w') as f:
        json.dump(actual_duplicates, f, indent=4)

def handle_duplicates_in_file_infos(actual_duplicates_path, file_infos_path, new_file_infos_path):             
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
                new_file_infos[file_to_discard]['new_path'] = 'duplicates' + old_path
                new_file_infos[file_to_discard]['is_duplicate'] = True
        
    with open(new_file_infos_path, 'w') as f:
        json.dump(new_file_infos, f, indent=4)
