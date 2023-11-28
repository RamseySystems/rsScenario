import openpyxl


def allowed_file(filename: str, allowed_extentions):
    '''
    A function to check if a file has an allowed extension

    :param filename: The name of the file to check
    :param allowed_extentions: A list of allowed file extensions
    :return: True if the file has an allowed extension, False otherwise
    '''
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in allowed_extentions


def extract_paths(path_list, plain: bool) -> list:
    '''
    Extract paths from the path/value list and optionally remove indexes.

    :param path_list: The path + value list.
    :param plain: A boolean value that determines whether to remove the indexes.
    :return: A list of extracted paths.
    '''
    new_path_list = [remove_indexing(arr[0]) if plain else arr[0] for arr in path_list]
    return new_path_list


def remove_indexing(path: str):
    '''
    A function to remove the indexes from a FHIR shorthand path

    :param path: the FHIR path to process
    :return: :str:
    '''
    path_arr = path.split('.')
    return '.'.join([path.split('[')[0] if '[' in path else path for path in path_arr])




