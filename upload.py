from utils.misc import input_with_default

from utils.upload_dataset import upload_file_list, curate_paths_list, get_local_paths

if __name__ == "__main__":
    print("upload dataset")
    dir = input_with_default("dir")
    root = input_with_default("root")
    subdir = input_with_default("subdir")
    n = input_with_default("n")
    access_token = input_with_default("access token")
    file_list_path = "upload_file_list/" + subdir + "/file_list-" + n + ".json"
    uploaded_file_list_path = (
        "upload_file_list/" + subdir + "/uploaded_files-" + n + ".json"
    )

    s = input("create file list? (y/n) ")
    if s.lower() == "y":
        all_paths = get_local_paths(dir)
        curate_paths_list(all_paths, file_list_path, root)

    print("check files to be uploaded in " + file_list_path)
    input("press enter to continue")

    upload_file_list(file_list_path, access_token, uploaded_file_list_path)
