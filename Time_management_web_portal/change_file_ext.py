import os

def change_file_ext(file_path, new_ext):
    """ 
    Change the file extension of a given file.
    
    Args:
        file_path (str): Path to the file whose extension is to be changed
        new_ext (str): New file extension to be applied
    
    Returns:
        str: New file path with updated extension
    """

    if '.env' in file_path or '.txt6' in file_path:
        new_file_path = f"{new_ext}"
    else:
        file_name=file_path.split("\\")[-1]
        file_path=file_path.replace(file_name, new_ext)
        new_file_path = file_path
    return new_file_path

def in_file_name(file_name, ext_mapping):
    for key in ext_mapping:
        a=len(key)
        if key in file_name[-a:] and 'change_file_ext.py' != file_name:
            # print(f"File name {file_name} change to -> {file_name.replace(key, ext_mapping[key])}" )
            return True, file_name.replace(key, ext_mapping[key])
    return False,"error"


def batch_change_extensions(folder_path, ext_mapping):
    """ 
    Change file extensions for all files in a given folder according to predefined rules.
    
    Args:
        folder_path (str): Path to the folder containing files to be processed
    """

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            name_of_file, ext = os.path.splitext(filename)
            is_found, new_file_name = in_file_name(filename, ext_mapping)
            if is_found:
                new_path = change_file_ext(file_path, new_file_name)
                os.rename(file_path, new_path)
                print(f"Renamed: {file_path} -> {new_path}")


if __name__ == "__main__":
    folders = ['./', './templates', './static','./routes', './__pycache__']  # Replace with your folder paths

    ext_mapping_forward = {
        '.html': '_text_1.txt',
        '.py': '_text_2.txt',
        '.css': '_text_3.txt',
        '.pyc': '_text_4.txt',
        '.db' : '_text_5.txt',
        '.md' : '_text_7.txt',
        '.env': '_text_6.txt',
    }
    
    ext_mapping_rollback = {
            '_text_1.txt': '.html',
            '_text_2.txt': '.py',
            '_text_3.txt': '.css',
            '_text_4.txt': '.pyc',
            '_text_5.txt': '.db',
            '_text_7.txt': '.md',
            '_text_6.txt': '.env',
    }

    k=2
    if k == 1:
        print("Changing file extensions to .txt1, .txt2, etc.")
        for folder in folders:
            batch_change_extensions(folder, ext_mapping_forward)
        print("File extensions changed successfully.")
    else:
        print("Rolling back file extensions to original formats.")
        for folder in folders:
           batch_change_extensions(folder, ext_mapping_rollback)
        print("File extensions rolled back successfully.")
