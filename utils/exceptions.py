import json

def handle_exceptions(exceptions_path, file_infos_path, new_file_infos_path, debug=False):
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
    
    with open(new_file_infos_path, "w") as f3:
        json.dump(new_file_infos, f3,  indent=4)

        