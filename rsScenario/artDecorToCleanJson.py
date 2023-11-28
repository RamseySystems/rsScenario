import html
import json
import re
import os
from functions import usefulFunctions as fn


def generate_schema(instance: dict):
    '''
    A function that will create a schema from a given JSON instance

    :instance dict: the JSON you want the schema to be based off
    :return dict:
    '''

    this_file_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = this_file_dir[:this_file_dir.rfind('/')]
    tempalte_path = os.path.join(parent_dir, 'templates')
    template = fn.template_env(tempalte_path).get_template('schema.jinja')
    schema = template.render(dataset=instance['dataset'])

    return schema

def rem_new_line(text: str):
    '''
    A function to remove new line charictors from within the middle of text

    :param text: the text to remove it from
    :return: :str:
    '''
    pattern = re.compile(r'(?<=[a-zA-Z0-9.])\s*\n\s*(?=[a-zA-Z0-9.])')
    new_str = re.sub(pattern, ' ', text)

    return new_str

def art_decor_to_json(node, implementationGuidance: bool):
    '''
    A function to convert an art-decor structure to a JSON representation

    :param node: The node to convert
    :param implementationGuidance: A boolean to indicate if the file should contain implementation guidance
    :return: The converted node
    '''
    if isinstance(node, dict):
        retVal = {}
        for key in node:
            if key == 'desc':
                if '#text' in node[key][0]:
                    retVal['description'] = html.unescape(
                        node[key][0]['#text'])
            elif key == 'conformance':
                retVal['mro'] = node[key]
            elif key == 'shortName':
                retVal['name'] = node[key]
            elif key == 'operationalization':
                retVal['valueSets'] = re.sub(
                    r'(?<=release=)[a-z][0-9]*', '', html.unescape(node[key][0]['#text'])).replace('&amp;', '&')
            elif key == 'minimumMultiplicity':
                retVal[key] = node[key]
            elif key == 'maximumMultiplicity':
                retVal[key] = node[key]
            elif key == 'type':
                retVal['type'] = node[key]
            elif key == 'valueDomain':
                if node[key][0]['type'] != 'code':
                    if node[key][0]['type'] != 'ordinal':
                        retVal[key] = node[key].copy()
            elif key == 'context':
                if implementationGuidance:
                    retVal['implementationGuidance'] = rem_new_line(re.sub(
                        r'(?<=release=)[a-z][0-9]*', '', html.unescape(node[key][0]['#text'])).replace('&amp;', '&'))
            elif isinstance(node[key], dict) or isinstance(node[key], list):
                if key not in ['relationship', 'implementation']:
                    child = art_decor_to_json(node[key], implementationGuidance)
                    if child:
                        retVal[key] = child

        if retVal:
            return retVal
        else:
            return None

    elif isinstance(node, list):
        retVal = []
        for entry in node:
            if isinstance(entry, str):
                retVal.append(entry)
            elif isinstance(entry, dict) or isinstance(entry, list):
                child = art_decor_to_json(entry, implementationGuidance)
                if child:
                    retVal.append(child)
        if retVal:
            return retVal
        else:
            return None
        

# a function to wrap together the json processing functions
def process_json(file_path: dict, save_dir: str):
    '''
    A function to process a JSON file and return the results
    :param file_path: The JSON file to process
    :param save_dir: The directory to save the results to
    :return: :dict:
    '''
    # get the file name and open the file
    file_name = file_path.split('/')[-1].split('.')[0]
    with open(file_path, 'r') as f:
        file = json.load(f)

    # generate the reformatted json
    prsb_json_no_implamentation = art_decor_to_json(file, False)
    prsb_json_with_implamentation = art_decor_to_json(file, True)

    # generate the schema
    schema_no_implamentation = generate_schema(prsb_json_no_implamentation)
    schema_with_implamentation = generate_schema(prsb_json_with_implamentation)

    # save the results
    fn.save_obj_to_file(prsb_json_no_implamentation, f'{save_dir}/{file_name}_no_implementation.json')
    fn.save_obj_to_file(prsb_json_with_implamentation, f'{save_dir}/{file_name}_with_implementation.json')
    fn.save_obj_to_file(schema_no_implamentation, f'{save_dir}/{file_name}_no_implementation_schema.json')
    fn.save_obj_to_file(schema_with_implamentation, f'{save_dir}/{file_name}_with_implementation_schema.json')

    return