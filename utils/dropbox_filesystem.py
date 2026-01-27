import dropbox
import json
import numpy as np
import sys

from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError

from tqdm import tqdm

from utils.globals import STOP_FLAGS, EXACT_STOP_FLAGS


    
    
def get_all_paths(TOKEN, dir='/source', recursive = True, remove_source = True, exceptions=True, verbose = True):
    """
    Returns all file paths within a specified directory in dropbox

    Package
    ----
    `utils.dropbox_filesystem.py`
    
    Parameters
    --------
        TOKEN : str, 
            access token for the Dropbox API
        dir='/source' : str, 
            path to the specified directory (should start with '/source'), 
            dir='/source/dir' and dir='/source/dir/' will return the same result
        recursive=True : bool, 
            allows recursive calls to explore all the subdirectories, 
            will only show subdirs otherwise
        remove_source=True: bool, 
            will remove '/source' in the returned paths iff True,
            must be set to True for the other functions to work
        exceptions=True : bool,
            does not explore directories containing stop flags if set to True
        verbose=True : bool,
            prints infos on Dropbox authentication if set to True
        
    
    Returns
    --------
        all_paths : list(str),
            a list of all file paths in the specified Dropbox directory
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
            
    all_paths = []

    for entry in dbx.files_list_folder(dir).entries:
        last_folder = (entry.path_display).split('/')[-1].lower()
        if recursive:  
            if type(entry) == dropbox.files.FolderMetadata:
                if exceptions and (np.array([stop_flag in entry.path_display.lower() for stop_flag in STOP_FLAGS]).any() or last_folder in EXACT_STOP_FLAGS ):
                    if remove_source:
                        new_path = entry.path_display[len('/source'):]
                        if new_path[0] != '/':
                            new_path = '/' + new_path
                        all_paths.append(new_path)
                    else:
                        all_paths.append(entry.path_display)
                else:
                    all_paths += get_all_paths(TOKEN, entry.path_display, recursive, remove_source, exceptions, verbose=False)

            else:
                if remove_source:
                    new_path = entry.path_display[len('/source'):]
                    if new_path[0] != '/':
                        new_path = '/' + new_path
                    all_paths.append(new_path)
                else:
                    all_paths.append(entry.path_display)
        else:
            if remove_source:
                new_path = entry.path_display[len('/source'):]
                if new_path[0] != '/':
                    new_path = '/' + new_path
                all_paths.append(new_path)
            else:
                all_paths.append(entry.path_display)
    return all_paths

def sort_source_to_target(file_infos_path, TOKEN, source_dir='/source', target_dir='/target/'):
    """
    Sorts the files from `source_dir` and copies them to `target_dir` in the DropBox, 
    following the instructions in `file_infos_path`
    
    Package
    ----
    `utils.dropbox_filesystem.py`
    
    Prerequisites
    ----
     - source directory is consistent with used file infos
     - target directory is empty
    
    Parameters
    ----
        file_infos_path: str, 
            where to find the instructions (should lead to a .json file)
        TOKEN: str, 
            access token for the DropBox API
        source_dir='/source': str, 
            path to the specified source directory (should start with '/source'), 
            source_dir='/source/dir' and source_dir='/source/dir/' will return the same result
        target_dir='/target/': str, 
            path to the specified target directory (should start with '/target'), 
            target_dir='/target/dir' and target_dir='/target/dir/' will return the same result
    
    Modifies the target directory in Dropbox
    ----
    """
    if (len(TOKEN) == 0):
        sys.exit("ERROR: Looks like you didn't add your access token.")

        # Create an instance of a Dropbox class, which can make requests to the API.
    print("Creating a Dropbox object...")
    with dropbox.Dropbox(TOKEN) as dbx:
        # Check that the access token is valid
        try:
            dbx.users_get_current_account()
            print("Access token is valid")
        except AuthError:
            sys.exit("ERROR: Invalid access token; try re-generating an "
                "access token from the app console on the web.")
            
    with open(file_infos_path, 'r') as f:
        file_infos = json.load(f)

    errors = {}

    for file in tqdm(file_infos.keys()):
        if source_dir[-1] == '/' and file_infos[file]["old_path"][0] =='/':
            correct_source_dir = source_dir[:-1]
        elif source_dir[-1] != '/' and file_infos[file]["old_path"][0] =='/':
            correct_source_dir = source_dir
        elif source_dir[-1] == '/' and file_infos[file]["old_path"][0]!='/':
            correct_source_dir = source_dir
        elif source_dir[-1] != '/' and file_infos[file]["old_path"][0]!='/':
            correct_source_dir = source_dir + '/'
        
        if target_dir[-1] == '/' and file_infos[file]["new_path"]=='/':
            correct_target_dir = target_dir[:-1]
        elif target_dir[-1] != '/' and file_infos[file]["new_path"]=='/':
            correct_target_dir = target_dir
        elif target_dir[-1] == '/' and file_infos[file]["new_path"]!='/':
            correct_target_dir = target_dir
        elif target_dir[-1] != '/' and file_infos[file]["new_path"]!='/':
            correct_target_dir = target_dir + '/'
        
        from_path = correct_source_dir + file_infos[file]["old_path"]
        to_path = correct_target_dir + file_infos[file]["new_path"]
        #print('Copying from: \n', from_path)
        #print('to: \n', to_path)
        try:
            confirmed_duplicate = file_infos[file]["confirmed_duplicate"]
        except:
            confirmed_duplicate = False
        if not confirmed_duplicate:

            try:
                dbx.files_copy(
                    from_path= from_path,
                    to_path= to_path
                )
            except:
                errors[from_path] = to_path
    with open('transfer_errors.json', 'w') as f:
        json.dump(errors, f, indent=4)
    
    print('Files successfully copied in target directory, except for the ones in transfer_errors.json')
