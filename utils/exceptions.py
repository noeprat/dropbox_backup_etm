import json
from utils.filename_reader import is_derivative

def handle_exceptions(exceptions_path, file_infos_path, new_file_infos_path):
    """
    Applies the instructions in the exceptions file to create a new file_infos.json

    **Overwrites data in `new_file_infos_path`**

    Package
    ----
    `utils.handle_exceptions.py`

    Parameters
    ----
        exceptions_path: str,
            path to a json containing the exceptions, usually `utils/exceptions.json`
        file_infos_path: str,
            path to the original file_infos.json
        new_file_infos_path: str,
            path to the updated file_infos.json
    
    Saves
    ----
        new_file_infos_path, json file
            updated file_infos.json

    """
    with open(exceptions_path, 'r') as f1:
        exceptions = json.load(f1)
    with open(file_infos_path, 'r') as f2:
        file_infos = json.load(f2)
    
    new_file_infos = file_infos.copy()
    
    for except_string in exceptions.keys():
        for file in new_file_infos.keys():
            if except_string.lower() in file.lower():
                for key in exceptions[except_string].keys():
                    new_file_infos[file][key] = exceptions[except_string][key]
            if "type" in exceptions[except_string].keys():
                new_type = new_file_infos[file]["type"]
                if "is_derivative" not in exceptions[except_string].keys():
                    new_file_infos[file]["is_derivative"] = is_derivative(new_type)
    
    with open(new_file_infos_path, "w") as f3:
        json.dump(new_file_infos, f3,  indent=4)