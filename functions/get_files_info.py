import os 

def get_files_info(working_directory, directory=None):
    
    if directory == None:
        directory = ""
    
    abs_working_directory = os.path.abspath(working_directory)
    joined_path = os.path.join(working_directory, directory)
    abs_joined_path = os.path.abspath(joined_path)

    if not abs_joined_path.startswith(abs_working_directory):
        return (f'Error: Cannot list "{directory}" as it is outside the permitted working directory')
    
    if not os.path.isdir(abs_joined_path):
        return (f'Error: "{directory}" is not a directory')
    try:
        contents = os.listdir(abs_joined_path)
    except OSError:
        return (f'Error: Could not list contents of "{abs_joined_path}"')

    item_info = []

    for item in contents:
        try:
            full_path = os.path.join(abs_joined_path, item)
            file_size = os.path.getsize(full_path)
            is_dir = os.path.isdir(full_path)
            formatted = (f'- {item}: {file_size} bytes, is_dir={is_dir}')
            item_info.append(formatted)
        except OSError:
            return (f'Error: Could not get information for "{item}"')

    final = '\n'.join(item_info)
    return final