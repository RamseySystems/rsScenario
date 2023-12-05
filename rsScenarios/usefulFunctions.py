import json
import os
import shutil
from google.cloud import storage

def clear_dir(folder_path: str):
    if not folder_path.startswith('/tmp'):
        raise ValueError(f"The folder '{folder_path}' does not start with /tmp.")
    
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"The folder '{folder_path}' was created.")
    else:
        print(f"The folder '{folder_path}' already exists.")
        # Delete the contents of the folder
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Error deleting {file_path}: {str(e)}")
        print(f"The contents of the folder '{folder_path}' were deleted.")


def clear_and_replace(src_dir, dest_dir):
    '''
    A function to clear the contents of a folder and replace them with the contents of another folder
    
    :param src_dir: The source folder
    :param dest_dir: The destination folder
    :return: None
    '''
    # Remove existing files and folders in dest_dir
    for filename in os.listdir(dest_dir):
        file_path = os.path.join(dest_dir, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
            
    # Copy files and folders from src_dir to dest_dir
    for filename in os.listdir(src_dir):
        src_path = os.path.join(src_dir, filename)
        dest_path = os.path.join(dest_dir, filename)
        if os.path.isdir(src_path):
            shutil.copytree(src_path, dest_path)
        else:
            shutil.copy2(src_path, dest_path)


def template_env(template_path):
    '''
    A function to create a jinja2 template environment
    
    :param template_path: The path to the template folder
    :return: The jinja2 template environment
    '''
    from jinja2 import Environment, FileSystemLoader
    return Environment(loader=FileSystemLoader(template_path))


def render_template(template_name: str, data: dict, save_dir: str, name: str = None) -> None:
    '''
    A function to render a template against given data and save it to a given directory

    :param template_name: The name of the template to render
    :param data: The data to render the template against
    :param save_dir: The directory to save the rendered template to
    :param name: The name of the personae for timeline rendering use
    '''
    
    ## test code
    this_file_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = this_file_dir[:this_file_dir.rfind('/')]
    tempalte_path = os.path.join(parent_dir, 'templates')
    full_save_dir = os.path.join(parent_dir, save_dir)
    
    template = template_env(tempalte_path).get_template(template_name)
    
    if name:
        output = template.render(data=data, name=name)
    else:
        output = template.render(data=data)

    if save_dir.endswith('.json'):
        # Handle JSON format
        with open(save_dir, 'w') as f:
            json.dump(data, f, indent=4)
        print(f'The JSON file {save_dir} was created.')
    elif save_dir.endswith('.html'):
        # Handle HTML format
        with open(full_save_dir, 'w') as f:
            f.write(output)
        print(f'The HTML file {save_dir} was created.')
    else:
        print(f'Unsupported file format for {save_dir}. No file was created.')
    
    return

def save_obj_to_file(obj, save_path):
    '''
    A function to save an object to a file

    :param obj: The object to save
    :param save_path: The path to save the object to
    :return: None
    '''
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=4, ensure_ascii=False)
    return

def load_obj_from_file(load_path):
    '''
    A function to load an object from a file

    :param load_path: The path to load the object from
    :return: The loaded object
    '''
    with open(load_path, "r", encoding="utf-8") as f:
        obj = json.load(f)
    return obj

def upload_tree_to_gcs(source_dir, destination_prefix=''):
    # Set up Google Cloud Storage client
    client = storage.Client()
    bucket = client.bucket('sites.ramseysystems.co.uk')
    
    # Walk through the source directory and upload files
    for root, dirs, files in os.walk(source_dir):
        # need to make this better
        if 'node_modules' in dirs:
            dirs.remove('node_modules')
        if 'venv' in dirs:
            dirs.remove('venv')
        if '.pytest_cache' in dirs:
            dirs.remove('.pytest_cache')
        if '.DS_Store' in files:
            files.remove('.DS_Store')
        if 'Icon_' in files:
            files.remove('Icon_')
        if 'package-lock.json' in files:
            files.remove('package-lock.json')
        if 'package.json' in files:
            files.remove('package.json')
        
        for file in files:
            local_path = os.path.join(root, file)
            remote_path = os.path.join(destination_prefix, os.path.relpath(local_path, source_dir))
            
            blob = bucket.blob(remote_path)
            blob.upload_from_filename(local_path)
            
            print(f'Uploaded: {local_path} -> gs://sites.ramseysystems.co.uk/{remote_path}')
            
        for dir in dirs:
            local_path = os.path.join(root, dir)
            remote_path = os.path.join(destination_prefix, os.path.relpath(local_path, source_dir))
            
            blob = bucket.blob(os.path.join(remote_path, ''))  # Create a "dummy" directory blob
            blob.upload_from_string('')
            
            print(f'Uploaded directory: {local_path} -> gs://sites.ramseysystems.co.uk/{remote_path}/')
            
def clear_storage_bucket(folder_path):
    # Initialize the GCS client
    client = storage.Client()

    # Get the bucket
    bucket = client.get_bucket('sites.ramseysystems.co.uk')

    # List objects in the specified folder
    objects_to_delete = bucket.list_blobs(prefix=folder_path)

    # Delete each object in the folder
    for blob in objects_to_delete:
        blob.delete()

    print(f"All objects in '{folder_path}' folder of 'sites.ramseysystems.co.uk' bucket have been deleted.")

    # Check if the folder is empty
    if not bucket.list_blobs(prefix=folder_path).max_results:
        # Create the folder blob
        folder_blob = bucket.blob(folder_path)
        folder_blob.upload_from_string("")  # Upload an empty string to create the folder

        print(f"Folder '{folder_path}' created in 'sites.ramseysystems.co.uk' bucket.")