import json
import sys
import dropbox
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError


    
    
def get_all_paths(dir, TOKEN, recursive = True, remove_source = True):
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
            
    all_paths = []
    for entry in dbx.files_list_folder(dir).entries:
        if recursive:    
            if type(entry) == dropbox.files.FolderMetadata:
                all_paths += get_all_paths(entry.path_display, TOKEN)
            else:
                if remove_source:
                    new_path = entry.path_display[len(dir):]
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

def sort_source_to_target(file_infos_path, TOKEN):
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
        dbx.files_copy(
        from_path= file_infos[file]["old_path"],
        to_path= '/target/' + file_infos[file]["new_path"]
    )
