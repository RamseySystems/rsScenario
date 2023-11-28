from functions import usefulFunctions as uf
from functions import excelProcessing as ep
from google.cloud import storage

import json
import os

'''
TODO
- add validate_personae function
- add compile_website function
- add personae validation to upload_standard function
- add personae validation to delete_standard function
- add recompile to del_patient function
- add recompile to save_patient function
'''

class MissingProvenanceError(Exception):
    def __init__(self, message="Provenance data is missing. Please upload a provenance file."):
        self.message = message
        super().__init__(self.message)

class scenarioProject:
    def __init__(self, project_name, gcp_site):
        self.project_name = project_name
        self.gcp_project = gcp_site
        self.validated = False
        self.standard_dir = f'{gcp_site}/{project_name}/standards'
        self.personae_dir = f'{gcp_site}/{project_name}/personae'
        self.storage_client = storage.Client()
        self.provenance = []
        self.bucket = self.storage_client.bucket(self.gcp_project)
        
    def upload_provenance(self, file_path: str) -> None:
        '''
        A function to upload a provenance file to the personae directory
        Re-create all path lists
        Re-validate personae
        
        :param file_path: The path to the provenance file to upload
        :return: None
        '''
        # get path list
        provenance_paths = ep.get_standard_paths(file_path, [], False)
        provenance_paths_json_data = json.dumps(provenance_paths)
        self.provenance = provenance_paths
        
        # upload json string to provenance.json file
        blob = self.bucket.blob(f'{self.standard_dir}/provenance.json')
        blob.upload_from_string(provenance_paths_json_data)
        print(f"File {file_path} uploaded to {self.standard_dir}")
        
        return
    
    def upload_standard(self, file_path: str) -> None:
        '''
        A function to upload a standard to the standards directory
        Creates path list for standard
        Re-validate personae
        
        :param file_path: The path to the standard xlsx file to upload
        :return: None
        '''
        # upload file
        blob = self.bucket.blob(f'{self.standard_dir}/{file_path}')
        blob.upload_from_filename(file_path)
        print(f"File {file_path} uploaded to {self.standard_dir}")
        
        # recreate path list files
        if len(self.provenance) != 0:
            
            main_path_list = []
            
            # loop over the standards folder anbd create path lists
            for file in self.bucket.list_blobs(prefix=self.standard_dir):
                
                # avoid directories
                if not file.name.endswith('/'): 
                    if file.name.endswith('.xlsx'):
                        
                        # get file name, extention and save dir path
                        file_name = file.name.split('/')[-1]
                        file_extension = file_name.split('.')[-1]
                        tmp_dir_path = f'/tmp/{self.project_name}/{file.name}'
                        
                        # download file and save to tmp
                        file.download_to_filename(tmp_dir_path)
                        
                        # get path list
                        standard_paths = ep.get_standard_paths(tmp_dir_path, self.provenance, False)
                        main_path_list.append(standard_paths)
                        
                        # save path lists to JSON file on gcp
                        standard_paths_json_data = json.dumps(standard_paths)
                        blob = self.bucket.blob(f'{self.standard_dir}/{file_name}.json')
                        blob.upload_from_string(standard_paths_json_data)
                        print(f"File {file_name}.json uploaded to {self.standard_dir}")
                        
                        # delete tmp file
                        os.remove(tmp_dir_path)
        else:
            print('Missing personae file. Please upload persaonae file before standards.')
            raise MissingProvenanceError
        
        # re validate personae
        patient_list = self.patient_list()
        
        # loop over patient files
        for patient in patient_list:
            if patient.endswith('.json'):
                blob = self.bucket.blob(f'{self.personae_dir}/{patient}')
                personae_data_str = blob.download_as_string()
                personae_data = json.loads(personae_data_str)
                
                
                
                
                
            elif patient.endswith('.xlsx'):
                pass
            
        
        
        '''
        To do
        - only validate with the standard stated in the excel file or storylog json
        '''
        
        
        
        return
    
    def delete_standard(self, standard_file_name: str) -> None:
        '''
        A function to delete a standard from the standards directory
        Removes path list for standard
        
        :param standard_file_name: The name of the standard file to delete
        :return: None
        '''
        blob = self.bucket.blob(f'{self.standard_dir}/{standard_file_name}')
        blob.delete()
        print(f"File {standard_file_name} deleted from {self.standard_dir}")
        
        return
    
    def standard_path_list(self, standard_name: str) -> list:
        '''
        A function to return the path list for a given standard
        
        :param standard_name: The name of the standard to return the path list for without extention
        :return: The path list for the given standard
        '''
        # get path list
        blob = self.bucket.blob(f'{self.standard_dir}/{standard_name}.json')
        standard_data_str = blob.download_as_string()
        standard_list = json.loads(standard_data_str)
        
        return standard_list
        
        
    def standards_list(self) -> list:
        '''
        A function to return a list of standards in the standards directory
        
        :return: A list of standards in the standards directory
        '''
        standard_fles = [blob.name for blob in self.bucket.list_blobs(prefix=f'{self.project_name}/standards/') if blob.name.endswith('.xlsx')]
        
        return standard_fles
    
    def patient_list(self) -> list:
        '''
        A function to return a list of patients in the personae directory
        
        :return: A list of patients in the personae directory
        '''
        standard_fles = [blob.name for blob in self.bucket.list_blobs(prefix=f'{self.project_name}/personae/')]
        
        return standard_fles
    
    def patient(self, patient_name: str) -> dict:
        '''
        A function to return a patient storylog from the personae directory
        
        :param patient_name: The name of the patient to return the storylog for
        :return: The storylog for the given patient
        '''
        # get patient
        blob = self.bucket.blob(f'{self.personae_dir}/{patient_name}.json')
        patient_str = blob.download_as_string()
        patient_json = json.loads(patient_str)
        
        return patient_json
    
    def save_patient(self, patient_file: dict, patient_name: str) -> None:
        '''
        A function to save a patient storylog to the personae directory
        Re-compiles website
        
        :param patient_file: The patient storylog to save
        :param patient_name: The name of the patient storylog to save
        :return: None
        '''
        # upload patient file
        patient_string = json.dumps(patient_file)
        blob = self.bucket.blob(f'{self.personae_dir}/{patient_name}.json')
        blob.upload_from_string(patient_string)
        print(f"File {patient_name}.json uploaded to {self.personae_dir}")
        
        # re-compile website
        compile_website()
        return
    
    def del_patient(self, patient_name: str) -> None:
        '''
        A function to delete a patient storylog from the personae directory
        Re-compiles website
        
        :param patient_name: The name of the patient storylog to delete
        :return: None
        '''
        # delete patient file
        blob = self.bucket.blob(f'{self.personae_dir}/{patient_name}.json')
        blob.delete()
        print(f"File {patient_name}.json deleted from {self.personae_dir}")
        
        # recompile website
        compile_website()
        
        return
    
    
    
    


def validate_personae(personae_name: str) -> dict:
    '''
    A function to validate a personae against a given standard
    
    :param personae_name: The name of the personae to validate. Should include the extention
    :return: A dictionary of scenario sheets and their false paths
    '''
    # open personae file
    
    # loop over the sheets/time-line items, get the appropriate standard and validate
    
    # return the results
    
    return []

def compile_website():
    '''
    A function to compile the website
    Will re-render all templates and save them to the website directory
    
    :return: None
    '''
    pass