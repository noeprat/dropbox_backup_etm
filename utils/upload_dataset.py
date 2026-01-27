import dropbox
import json
import os
import re
from tqdm import tqdm

from utils.globals import STOP_FLAGS_UPLOAD, EXACT_STOP_FLAGS_UPLOAD, TO_UPLOAD_REGEXPS
from utils.misc import my_ls, input_with_default

"""
Upload specific files of lumbar_healthy_fmri to Dropbox
"""


def upload(
    access_token,
    file_path,
    target_path,
    timeout=900,
    chunk_size=4 * 1024 * 1024,
):
    """
    uploads a potentially large file to dropbox

    Package
    ----
    `utils.upload_dataset.py`

    Parameters
    --------
        access_token : str,
            access token for the Dropbox API
        file_path : str,
            path to local file
        target_path : str,
            path in the dropbox (since the app scope is restricted, it will be within `/Applications/NR_backup_test/`)
        timeout=900 : int,
            timeout limit in seconds
        chunk_size=4MB : int,
            whunk size, should not exceed 150 MB

    Saves
    --------
        target_path
            file uploaded in dropbox
    """
    # Source - https://stackoverflow.com/a
    # Posted by Greg, modified by community. See post 'Timeline' for change history
    # Retrieved 2026-01-26, License - CC BY-SA 4.0
    dbx = dropbox.Dropbox(access_token, timeout=timeout)
    with open(file_path, "rb") as f:
        file_size = os.path.getsize(file_path)
        if file_size <= chunk_size:
            print(dbx.files_upload(f.read(), target_path))
        else:
            with tqdm(total=file_size, desc="Uploaded") as pbar:
                upload_session_start_result = dbx.files_upload_session_start(
                    f.read(chunk_size)
                )
                pbar.update(chunk_size)
                cursor = dropbox.files.UploadSessionCursor(
                    session_id=upload_session_start_result.session_id,
                    offset=f.tell(),
                )
                commit = dropbox.files.CommitInfo(path=target_path)
                while f.tell() < file_size:
                    if (file_size - f.tell()) <= chunk_size:
                        print(
                            dbx.files_upload_session_finish(
                                f.read(chunk_size), cursor, commit
                            )
                        )
                    else:
                        dbx.files_upload_session_append(
                            f.read(chunk_size),
                            cursor.session_id,
                            cursor.offset,
                        )
                        cursor.offset = f.tell()
                    pbar.update(chunk_size)

def get_local_paths(dir, recursive = True, exceptions=True, force_abspath=False):
    """
    Returns all file paths within a specified local directory

    Package
    ----
    `utils.upload_dataset.py`
    
    Parameters
    --------
        dir : str, 
            path to the specified directory
            dir='/dir' and dir='/dir/' will return the same result
        recursive=True : bool, 
            allows recursive calls to explore all the subdirectories, 
            will only show subdirs otherwise
        exceptions=True : bool,
            does not explore directories containing stop flags if set to True
        verbose=True : bool,
            prints infos on Dropbox authentication if set to True
        
    Returns
    --------
        all_paths : list(str),
            a list of all file paths in the specified Dropbox directory
    """           
    all_paths = []

    for entry in my_ls(dir, force_abspath):
        last_folder = entry.split('\\')[-1].lower()
        if recursive:
            if os.path.isdir(entry):
                if exceptions and (sum([stop_flag in entry.lower() for stop_flag in STOP_FLAGS_UPLOAD])>=1 or last_folder in EXACT_STOP_FLAGS_UPLOAD ):
                    all_paths.append(entry)
                else:
                    all_paths += get_local_paths(
                        dir=entry, 
                        recursive=recursive,
                        exceptions=exceptions,
                        force_abspath = force_abspath
                        )

            else:
                all_paths.append(entry)
        else:
            all_paths.append(entry)
    return all_paths

def curate_paths_list(all_paths, file_list_path, root):
    """
    TODO
    """
    relative_paths = []
    absolute_paths = []
    for entry in all_paths:
        new_entry = entry.replace("\\", "/")
        if new_entry.startswith(root.replace("\\", "/")):
            new_entry = new_entry[len(root):]
        else:
            print("root error")
        for regexp in TO_UPLOAD_REGEXPS:
            pattern = re.compile(regexp)
            match = re.search(pattern,new_entry)
            if match and (new_entry not in relative_paths):
                relative_paths.append(new_entry)
                absolute_paths.append(entry)
    out_dict = {
        "relative_paths": relative_paths,
        "absolute_paths": absolute_paths
    }
    
    dirs = '/'.join(file_list_path.split('/')[:-1])
    os.makedirs(dirs, exist_ok=True)
    with open(file_list_path, 'w') as f:
        json.dump(out_dict, f, indent=4)

def upload_file_list(file_list_path, access_token):
    with open(file_list_path, 'r') as f:
        paths = json.load(f)
    relative_paths = paths["relative_paths"]
    absolute_paths = paths["absolute_paths"]

    for idx, abspath in tqdm(enumerate(absolute_paths)):
        target = "/uploaded" + relative_paths[idx]
        upload(
            access_token,
            abspath,
            target
        )


if __name__ == "__main__":
    dir = "E:\\vita_linux_20230829\\data\\fMRI\\Healthy\\Local_Server_COPY\\Local_NR_COPY\\Server_Structure"
    subdir = input_with_default('subdir')
    n = input_with_default('n')
    access_token = input_with_default('access token')


    
    file_list_path = 'upload_file_list/' + subdir + '/file_list-' + n + '.json'
    all_paths = get_local_paths(dir)

    curate_paths_list(all_paths, file_list_path, dir)

    print("check files to be uploaded in " + file_list_path)
    input("press enter to continue")
    
    upload_file_list(file_list_path, )