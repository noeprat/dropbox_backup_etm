import json
import sys
import dropbox
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError


    
    
def get_all_paths(TOKEN, dir='/source', recursive = True, remove_source = True):
    """
    Returns all file paths within a specified directory

    Inputs:
     - TOKEN: str, access token for the DropBox API
     - dir='/source: str, path to the specified directory (should start with '/source'), 
     dir='/source/dir' and dir='/source/dir/' will return the same result
     - recursive=True: bool, allows recursive calls to explore all the subdirectories, 
     will only show subdirs otherwise
     - remove_source=True: bool, 
     will remove '/source' in the returned paths iff True,
     must be set to True for the other functions to work
    
    Returns:
     - all_paths: list(str), a list of all file paths
    """
    if (len(TOKEN) == 0):
        sys.exit("ERROR: Looks like you didn't add your access token.")

        # Create an instance of a Dropbox class, which can make requests to the API.
    #print("Creating a Dropbox object...")
    with dropbox.Dropbox(TOKEN) as dbx:

        # Check that the access token is valid
        try:
            dbx.users_get_current_account()
            #print('Access token is valid')
        except AuthError:
            sys.exit("ERROR: Invalid access token; try re-generating an "
                "access token from the app console on the web.")
            
    all_paths = []
    for entry in dbx.files_list_folder(dir).entries:
        if recursive:    
            if type(entry) == dropbox.files.FolderMetadata:
                all_paths += get_all_paths(TOKEN, entry.path_display, recursive, remove_source)
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
                new_path = entry.path_display[len(dir):]
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
    
    Inputs:
     - file_infos_path: str, where to find the instructions (should lead to a .json file)
     - TOKEN: str, access token for the DropBox API
     - source_dir='/source': str, path to the specified source directory (should start with '/source'), 
     source_dir='/source/dir' and source_dir='/source/dir/' will return the same result
     - target_dir='/target/': str, path to the specified target directory (should start with '/target'), 
     target_dir='/target/dir' and target_dir='/target/dir/' will return the same result
    
    Returns nothing
    """
    if (len(TOKEN) == 0):
        sys.exit("ERROR: Looks like you didn't add your access token.")

        # Create an instance of a Dropbox class, which can make requests to the API.
    print("Creating a Dropbox object...")
    with dropbox.Dropbox(TOKEN) as dbx:

        # Check that the access token is valid
        try:
            dbx.users_get_current_account()
        except AuthError:
            sys.exit("ERROR: Invalid access token; try re-generating an "
                "access token from the app console on the web.")
            
    with open(file_infos_path, 'r') as f:
        file_infos = json.load(f)

    for file in file_infos.keys():
        if source_dir[-1] == '/' and file_infos[file]["old_path"]=='/':
            correct_source_dir = source_dir[:-1]
        elif source_dir[-1] != '/' and file_infos[file]["old_path"]=='/':
            correct_source_dir = source_dir
        elif source_dir[-1] == '/' and file_infos[file]["old_path"]!='/':
            correct_source_dir = source_dir
        elif source_dir[-1] != '/' and file_infos[file]["old_path"]!='/':
            correct_source_dir = source_dir + '/'
        
        if target_dir[-1] == '/' and file_infos[file]["new_path"]=='/':
            correct_target_dir = target_dir[:-1]
        elif target_dir[-1] != '/' and file_infos[file]["new_path"]=='/':
            correct_target_dir = target_dir
        elif target_dir[-1] == '/' and file_infos[file]["new_path"]!='/':
            correct_target_dir = target_dir
        elif target_dir[-1] != '/' and file_infos[file]["new_path"]!='/':
            correct_target_dir = target_dir + '/'
        
        
        dbx.files_copy(
            from_path= correct_source_dir + file_infos[file]["old_path"],
            to_path= correct_target_dir + file_infos[file]["new_path"]
        )
