# NR_data_sort

Scripts to help sorting imaging data from Dropbox, in an organization resembling BIDS. Requires [creating a registered Dropbox API app](https://www.dropbox.com/developers/apps/create) (I chose one with scoped access to a single folder).

# Code organization

 - `main.py`: main script
 - `upload.py`: script that was used to upload data from a hard drive to dropbox

## Utils directory

Scripts:
 - `dropbox_filesystem.py`: interactions with the Dropbox API
 - `exceptions.py`: handling the exceptions in `exceptions.json`
 - `filename_reader.py`: getting informations from a file's original path and writing its new path
 - `globals.py`: global variables used in different scripts
 - `handle_duplicates.py`: finding files that are likely to be identical and comparing them
 - `misc.py`: miscellaneous elementary functions, including `get_path_info` which is used to recognize in a given path the expressions in one of the jsons described below
 - `save_logs.py`: producing and reading the different logs / jsons / txts
 - `upload_dataset.py`: listing files in a local directory and uploading the ones matching the regular expressions in `TO_UPLOAD_REGEXPS` (see `globals.py`) to Dropbox.

Jsons:
 - `exceptions.json`: dictionary to add exceptions (see step 3.7)
 - `category.json`, `func_info.json`, `func_task.json`, `seg_info.json`, `suffix.json`: dictionaries to identify relevant expressions for the `file_infos` files (see `get_category`, `get_func_info`, etc. in `utils/filename_reader.py`)

# Step 1 - Dropbox app folder organization

Your app folder should be located on Dropbox at `All files/[your name]/Applications/[app name]`.

The main script requires two subdirectories:
 - `All files/[your name]/Applications/[app name]/source`, where you can copy an unsorted participant folder
 - `All files/[your name]/Applications/[app name]/target`, where you will find the sorted files after running the whole script

The uploading script (used to import local data to dropbox) will add files to a third subdirectory - `All files/[your name]/Applications/[app name]/target/uploaded`

# Step 2 - Python environment

Worked on Python 3.12.8

Needed packages are listed in `requirements.txt` (it is possible that some are missing). `pip install -r requirements.txt` should suffice.

The docker implementation has not been tested yet.

# Step 3 - Running main.py

Make sure the files you want to sort are in the `source` subdirectory on Dropbox (cf step 1).

After running the command `py main.py`, you will be asked to give a few inputs in the command line. To facilitate the next runs, the latest inputs are memorized in `inputs.json` and are chosen as default values. This means that if the command line prompts `sub: (default: sub-15)`, just pressing enter will set `sub` to `sub-15`.

**Do not add `inputs.json` to the git since it may contain your access token.**

## Step 3.1 - First inputs

The command line will ask for different prompts:
 - `subdir`: the local subdirectory where useful lists/dicts will be stored. Usually `[study name]_sub-[n]`
 - `n`: if you run main.py several times, it can be useful to differentiate each run
 - `old_prefix`: the path from which you copied the unsorted files; used to have a consistent `paths.txt` file
 - `new_prefix`: if the sorted files should be in a subdirectory (e.g. `~/pre_study_analysis/sub-01/...`), used to have consistent `paths.txt` and `recap.json` files
 - `sub`: to specify the participant, usually something like `sub-01`, `sub-02`, or `sub-pilot`. If an empty string is prompted, it will try to guess the participants code using the local file `~/utils/participants.csv`: you may need to write this new file with each line like `[old_participant_code],[new_participant_code]`.

## Step 3.2 - Access token

The next prompts should appear: \
`Need an access token for Dropbox` \
`access token: (default: )`

The access token can be found following the instructions [here](https://dropbox.tech/developers/generate-an-access-token-for-your-own-account), i.e. in your [Dropbox app console](https://www.dropbox.com/developers/apps) -> [app_name] -> 'settings' tab -> scroll down to OAuth 2 - Generated access token -> Generate

You can then copy-paste the access token to the command line. A token lasts for 6 hours if I remember correctly; refresh the app console page and generate a new one when it is obsolete.

## Step 3.3 - Preexisting file infos

The next prompt should be: \
`Use a preexisting file_infos.json ? [y/n]`

If you have already run the script, but couldn't proceed to the final part because of an obsolete access token, you may press `y`, and fill the `file_infos_path` + `tmpfile_infos_path` prompts.

Otherwise, press `n` to follow the standard pipeline.

## Step 3.4 - Reading files from Dropbox

The next prompt is: \
`Should the files in Dropbox be read ? (can be a time-consuming step, and requires a dbx access token)` \
`[y/n]`

Pressing `y` will start listing all the files/folders in the `source` subdirectory. Depending on the number of elements inside, this step might take a while. Then the file list is saved locally in `file_list/[subdir]/file_list-[n].json`.

Pressing `n` will read the saved list in the path above (after a first run).

If you change the variables `STOP_FLAGS` or `EXACT_STOP_FLAGS` in `utils/globals.py`, or if you modify the function `get_all_flags` in `utils/dropbox_filesystem.py`, you'll need to read again the files in Dropbox in order to see the effect.

## Step 3.5 - Comparing duplicates

The next prompt is: \
`Compare the potential duplicates (possibly a time-consuming step, requires a dropbox access token)? [y/n/u(se previous)]`

`y` will first ask you to check `file_infos/[subdir]/potential_duplicates-[n].json`, which is a preview to all the comparisons it is about to make. Its structure is as follows:
```
{
    "file1": [
        "file1",
        "file2",
        "file3"
    ],
    ...
}
```
This means the script will compare `file1` with `file2`, `file1` with `file3`, **but not** `file2` with `file3` (unless specified in another entry). You can modify this file to add / remove comparisons. I would recommend saving a copy of the manually modified version. Then pressing enter will let the comparisons begin (which requires a valid Dropbox access token), which might take a while (it's possible to break it into several runs, and then merge the results). it will result in a file `file_infos/[subdir]/actual_duplicates-[n].json` with a similar structure as above. The confirmed duplicates will not be treated in the rest of the pipeline.

`n` will skip this step.

`u` will ask you for `actual_duplicates_path`, and then this file is going to be used as if it was `file_infos/[subdir]/actual_duplicates-[n].json`.

If you make modification with an effect on how the potential duplicates are listed (modifying one of the json files in utils, or `utils/handle_duplicates.py`), you'll need to delete `file_infos/[subdir]/potential_duplicates-[n].json` so that the file will be remade.

## Step 3.6 - Metadata files

Usually the datasets contain json files with MRI metadata. The goal of this step is to pair such files to the right imaging files.

You'll be asked: \
`Match files with their metadata (possibly a time-consuming step)? [y/n/u(se previous)]`

`y` will ask you to manually correct `file_infos/[subdir]/jsons_to_data-[n].json`, which should have the following structure:
```
{
    "metadata_file.json": [
        "data_file"
    ],
    ...
}
```

`u` will ask you to input `jsons_to_data_path`, the path to a saved file with the structure above.

`n` will skip this step.

## Step 3.7 - Final verifications

You will be asked to verify the file in `file_infos/[subdir]/file_infos-[n].json`. This file shows all the informations the script gathered in order to properly sort them, structured as follows:
```
{
    "path/to/a/file": {
        "old_path": "path_to_a_file",
        "run": ...,
        "sub": ...,
        ...
        "new_path": "path/in/the/sorted/dataset"
    },
    "path/to/another/file": {
        ...
    }
    ...
}
```
You can make sure that infos are correct, and that the `new_path` complies with the desired organization. Temporary files are listed in `file_infos/[subdir]/tmp_file_infos-[n].json`; they will not be copied to the `target` directory.

If two files have the same `new_path`, they have the suffix `_duplicate-[k]` and are listed in `file_infos/[subdir]/same_new_paths-[n].json`. I wouldn't recommend going on with the pipeline if there are still such files. To avoid this, you can:
 - check that they are not actual duplicates that were not identified in step 3.5
 - identify the incorrect / incomplete sections in the `file_infos`, and correct the jsons / scripts in the local directory `utils`
 - add exceptions in `utils/exceptions.json`, to modify any section **except** `new_path` or `old_path`. It works as follows: all old paths in `file_infos.json` matching `exp_to_recognize` (can be a path to a precise file or just a string to recognize; it isn't case-specific), are going to have the specified sections (`"type"` and `"suffix"` in the example below) modified. The exceptions are treated sequentially.
```
{
    "exp_to_recognize": {
        "type": "anat",
        "suffix": ""
    },
    ...
}
```
>*For the options above, you will need to run the script again to see the effects, hence the numerous "use_previous" options*
 - directly modify the `file_infos.json`, but then you should save it in another path if you run the script again with the same config (otherwise it may be overwritten).

If you are satisfied with the file infos, you can press enter and begin the effective sorting in the `target` directory. This step can take several minutes, which gives you time to check the overview in `recaps/[subdir]/recap-[n].json`, and the logs in `paths/[subdir]/paths-[n].txt` and in `paths/[subdir]/tmpfiles_paths-[n].txt`. Once this step is complete, files that might have not been copied are logged locally in `transfer_errors.json`, you might need to manually transfer them.

# Step 4 - Merging recaps

You may end up with several json recaps for a single study, especially if you ran the script for each participant. To merge them into one study-wide recap, you can use the function `merge_general_recaps` in `utils/save_logs.py` in a distinct script / notebook; see the example below:
```
from utils.save_logs import merge_general_recaps

input_files = ['recaps/restore_sub-0' + str(i) + '/recap-01_saved.json' for i in range(1,10)]
input_files += ['recaps/restore_sub-' + str(i) + '/recap-01_saved.json' for i in range(10,16)]

merge_general_recaps(
        input_files=input_files,
        out_path='recaps/recap_restore.json'
    )
```