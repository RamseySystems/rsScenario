import datetime
import sys
sys.path.append('../rsScenario')

from collections import Counter
from rsScenarios.rsScenario import ScenarioTool as rsScenario
from google.cloud import storage

import pytest
import unittest
import jinja2
import os

'''
TODO
- finish tests
    - Run tests and get them passing
    - Make failing cases
'''

class TestScenarioTool(unittest.TestCase):
    def test_init(self):

        # test that the init function works
        test_scenario = rsScenario("_init", "sites.ramseysystems.co.uk")
        self.assertEqual(test_scenario.project_name, "_init")
        self.assertEqual(test_scenario.gcp_project, "sites.ramseysystems.co.uk")
        self.assertEqual(test_scenario.validated, False)
        self.assertEqual(test_scenario.standard_dir, "_init/standards")
        self.assertEqual(test_scenario.personae_dir, "_init/personae")
        self.assertEqual(test_scenario.continuous_data_dir, "_init/continuous_data")
        #self.assertIsInstance(test_scenario.storage_client, storage.Client())
        self.assertEqual(test_scenario.provenance, [])
        #self.assertIsInstance(test_scenario.template_env, jinja2.Environment)
        #self.assertIsInstance(test_scenario.bucket, test_scenario.storage_client.get_bucket("sites.ramseysystems.co.uk"))

    def test_copy_project(self):

        # test that the copy_project function works
        test_scenario = rsScenario("_copyproject", "sites.ramseysystems.co.uk")
        test_scenario.copy_project("_copyproject", "_copyproject2")
        
        # go on to the GCP bucket and check that the new project has been created
        new_dir_blob = test_scenario.bucket.blob("_copyproject2/standards/")
        self.assertEqual(new_dir_blob.exists(), True)
        
        # check the contents of the new project
        original_blobs = test_scenario.bucket.list_blobs(prefix="_copyproject/")
        new_blobs = test_scenario.bucket.list_blobs(prefix="_copyproject2/")
        
        original_files = []
        origional_file_sizes = {}
        while True:
            try:
                blob = next(original_blobs)
                blob_name = blob.name
                if blob_name != "_copyproject/":
                    origional_file_sizes[blob_name] = blob.size
                    original_files.append(blob_name)
            except StopIteration:
                break
            
        new_files = []
        new_file_sizes = {}
        while True:
            try:
                blob = next(new_blobs)
                blob_name = blob.name
                if blob_name != "_copyproject2/":
                    new_file_sizes[blob_name] = blob.size
                    new_files.append(blob_name)
            except StopIteration:
                break
        
        
        # check they are the same length
        self.assertEqual(len(original_files), len(list(new_files)))
        
        # Ckeck the content and their sizes are the same
        for filename in origional_file_sizes:
            new_filename = filename.replace("_copyproject", "_copyproject2")
            self.assertTrue(new_filename in new_file_sizes)
            self.assertEqual(origional_file_sizes[filename], new_file_sizes[new_filename])
            
    def test_list_projects(self):

        # test that the list_projects function works
        test_scenario = rsScenario("_listProjects", "sites.ramseysystems.co.uk")

        projects = test_scenario.list_projects()
        
        # check projects is a list
        self.assertIsInstance(projects, list)
        
        # check that if the project is not empty, that the elements are strings
        if projects != []:
            self.assertIsInstance(projects[0], str)
        
    def test_set_project(self):

        # test that the set_project function works
        test_scenario = rsScenario("_setproject", "sites.ramseysystems.co.uk")
        test_scenario.set_project("_listprojects")
        self.assertEqual(test_scenario.project_name, "_listprojects")
        
    def test_del_project(self):
        
        # test that the del_project function works
        test_scenario = rsScenario("_delproject", "sites.ramseysystems.co.uk")
        test_scenario.del_project("_delproject")
        
        # check the project has been deleted
        blob = test_scenario.bucket.blob("_delproject/")
        self.assertEqual(blob.exists(), False) 
    
    def test_upload_provenance(self):
        
        # test that the upload_provenance function works
        test_scenario = rsScenario("_uploadprovenance", "sites.ramseysystems.co.uk")
        test_scenario.upload_provenance("/Users/frankiehadwick/Documents/PRSB/rsScenario/tests copy/upload_provenance/Provenance.xlsx")
        
        # check the provenance list is not empty
        self.assertNotEqual(test_scenario.provenance, [])
        
    
    def test_upload_continuous_data(self):
        
        # test that the upload_continuous_data function works
        test_scenario = rsScenario("_uploadcontinuousdata", "sites.ramseysystems.co.uk")
        test_scenario.upload_continuous_data("/Users/frankiehadwick/Documents/PRSB/rsScenario/tests copy/upload_continuous_data/data.csv")
        
        # check the continuous data has been uploaded
        blob = test_scenario.bucket.blob("_uploadcontinuousdata/continuous_data/data.csv")
        self.assertEqual(blob.exists(), True)
    
    def test_upload_patient(self):
        
        ## make test file
        # test that the upload_patient function works
        test_scenario = rsScenario("_uploadpatient", "sites.ramseysystems.co.uk")
        test_scenario.upload_patient("/Users/frankiehadwick/Documents/PRSB/rsScenario/tests copy/upload_patient/Betty wound care.xlsx")
        
        # check the patient has been uploaded
        blob = test_scenario.bucket.blob("_uploadpatient/personae/Betty wound care.xlsx")
        self.assertEqual(blob.exists(), True)
    
    def test_upload_standard(self):
        
        ## make test file
        # test that the upload_standard function works
        test_scenario = rsScenario("_uploadstandard", "sites.ramseysystems.co.uk")
        test_scenario.upload_standard("/Users/frankiehadwick/Documents/PRSB/rsScenario/tests copy/upload_standard/Personal details.xlsx")
        
        # check the standard has been uploaded
        blob = test_scenario.bucket.blob("_uploadstandard/standards/Personal details.xlsx")
        self.assertEqual(blob.exists(), True)
    
    def test_del_standard(self):
        '''
        TODO
        - upload a standard first and delete
            - need to solve the problem with what comes first the provenance or the standard
        '''
        
        ## make test file
        # test that the del_standard function works
        test_scenario = rsScenario("_delstandard", "sites.ramseysystems.co.uk")
        test_scenario.upload_standard('/Users/frankiehadwick/Documents/PRSB/rsScenario/tests copy/upload_standard/Personal details.xlsx')
        test_scenario.del_standard("Personal details.xlsx")
        
        # check the standard has been deleted
        blob = test_scenario.bucket.blob("_delstandard/standards/standard.json")
        self.assertEqual(blob.exists(), False)
    
    def test_standard_path_list(self):
        pass
    
    def test_standards_list(self):
        
        # test that the standards_list function works
        test_scenario = rsScenario("_standardslist", "sites.ramseysystems.co.uk")
        test_scenario.upload_standard("/Users/frankiehadwick/Documents/PRSB/rsScenario/tests copy/upload_standard/Personal details.xlsx")
        standards = test_scenario.standards_list()
        self.assertEqual(standards, ["Personal details"])
    
    def test_patient_list(self):
        
        ## TODO
        ## Upload patient first
        
        # test that the patient_list function works
        test_scenario = rsScenario("_patientlist", "sites.ramseysystems.co.uk")
        patients = test_scenario.patient_list()
        self.assertEqual(patients, [])
    
    def test_get_patient(self):
        
        # test that the get_patient function works
        test_scenario = rsScenario("test", "sites.ramseysystems.co.uk")
        
        # upload patient storylog data
        test_scenario.upload_patient("/Users/frankiehadwick/Documents/PRSB/rsScenario/tests copy/get_patient/patient.json")
        
        patient = test_scenario.get_patient("patient")
        self.assertEqual(patient, {
            "name": "John Doe",
            "age": 30,
            "email": "johndoe@example.com",
            "address": {
                "street": "123 Main St",
                "city": "New York",
                "state": "NY",
                "zip": "10001"
            }
        })
    
    def test_save_patient(self):
        
        ## TODO
        ## Save patient first and get time stamp
        ## Then save again and check the time stamp has changed
        
        # check the timestamp is updated
        test_scenario = rsScenario("_savepatient", "sites.ramseysystems.co.uk")
        test_scenario.save_patient({
            "name": "John Doe",
            "age": 30,
            "email": "johndoe@example.com",
            "address": {
                "street": "123 Main St",
                "city": "New York",
                "state": "NY",
                "zip": "10001"
            }
        }, 'test_patient')
        
        # get curtrent timestamp
        blob = test_scenario.bucket.blob("_savepatient/personae/test_patient.json")
        blob.reload()
        last_modified = blob.updated
        
        # save patient again
        test_scenario.save_patient({
            "name": "John Doe",
            "age": 31,
            "email": "johndoe@example.com",
            "address": {
                "street": "123 Main St",
                "city": "New York",
                "state": "NY",
                "zip": "10001"
            }
        }, 'test_patient')
        
        # check the timestamp has been updated
        blob = test_scenario.bucket.blob("_savepatient/personae/test_patient.json")
        blob.reload()
        self.assertNotEqual(blob.updated, last_modified)

    def test_del_patient(self):
        
        # test that the del_patient function works
        test_scenario = rsScenario("_delpatient", "sites.ramseysystems.co.uk")
        test_scenario.save_patient({
            "name": "John Doe",
            "age": 31,
            "email": "johndoe@example.com",
            "address": {
                "street": "123 Main St",
                "city": "New York",
                "state": "NY",
                "zip": "10001"
            }
        }, 'test_patient')
        test_scenario.del_patient("test_patient.json")
        
        # check the patient has been deleted
        blob = test_scenario.bucket.blob("_delpatient/personae/test_patient.json")
        self.assertEqual(blob.exists(), False)
    
    def test_validate_personae(self):
        
        ## check that the personae is valid. Make failing case
        # test that the validate_personae function works
        test_scenario = rsScenario("_validatepersonae", "sites.ramseysystems.co.uk")
        test_scenario.validate_personae()
        self.assertEqual(test_scenario.validated, True)
    
    def test_render_story(self):
        assert False

    
    def test_render_log(self):
        assert False
    
    def test_render_data(self):
        assert False
    
    def test_compile_website(self):
        
        # get current last modified date of the website folder
        test_scenario = rsScenario("_compilewebsite", "sites.ramseysystems.co.uk")
        
        # get folder last modified data
        old_modified_times = get_files_and_last_modified("_compilewebsite/website/")
        test_scenario.compile_website()

        # get folder last modified data
        new_modified_times = get_files_and_last_modified("_compilewebsite/website/")
        
        # check the contents arnt the same
        self.assertNotEqual(old_modified_times, new_modified_times)

def get_files_and_last_modified(folder_path):
    # Initialize the client
    client = storage.Client()

    # Get the bucket
    bucket = client.get_bucket('sites.ramseysystems.co.uk')

    # Create an iterator for listing objects within the folder
    blobs_iterator = bucket.list_blobs(folder_path)

    # Create a dictionary to store file objects and their last modified dates
    file_info = {}

    while True:
        try:
            blob = next(blobs_iterator)
            # Remove the folder path prefix to get the relative file path
            relative_path = blob.name[len(folder_path):]
            file_info[relative_path] = blob.updated
        except StopIteration:
            break

    return file_info

if __name__ == '__main__':
    unittest.main()