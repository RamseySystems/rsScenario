import datetime
import sys
sys.path.append('../rsScenario')

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
        test_scenario = rsScenario("test2", "sites.ramseysystems.co.uk")
        self.assertEqual(test_scenario.project_name, "test2")
        self.assertEqual(test_scenario.gcp_project, "sites.ramseysystems.co.uk")
        self.assertEqual(test_scenario.validated, False)
        self.assertEqual(test_scenario.standard_dir, "sites.ramseysystems.co.uk/test2/standards")
        self.assertEqual(test_scenario.personae_dir, "sites.ramseysystems.co.uk/test2/personae")
        self.assertEqual(test_scenario.continuous_data_dir, "sites.ramseysystems.co.uk/test2/continuous_data")
        #self.assertIsInstance(test_scenario.storage_client, storage.Client())
        self.assertEqual(test_scenario.provenance, [])
        #self.assertIsInstance(test_scenario.template_env, jinja2.Environment)
        #self.assertIsInstance(test_scenario.bucket, test_scenario.storage_client.get_bucket("sites.ramseysystems.co.uk"))

    def test_copy_project(self):

        # test that the copy_project function works
        test_scenario = rsScenario("test", "sites.ramseysystems.co.uk")
        test_scenario.copy_project("test", "new_test")
        
        # go on to the GCP bucket and check that the new project has been created
        new_dir_blob = test_scenario.bucket.blob("new_test/standards/")
        self.assertEqual(new_dir_blob.exists(), True)
        
        # check the contents of the new project
        original_blobs = test_scenario.bucket.list_blobs(prefix="test/")
        new_blobs = test_scenario.bucket.list_blobs(prefix="new_test/")
        
        # check they are the same length
        self.assertEqual(len(list(original_blobs)), len(list(new_blobs)))
        
        original_files = {blob.name: blob.size for blob in original_blobs}
        new_files = {blob.name: blob.size for blob in new_blobs}

        # Ckeck the content and their sizes are the same
        for filename in original_files:
            new_filename = filename.replace("test", "new_test")
            self.assertTrue(new_filename in new_files)
            self.assertEqual(original_files[filename], new_files[new_filename])
            
    def test_list_projects(self):

        # test that the list_projects function works
        test_scenario = rsScenario("test", "sites.ramseysystems.co.uk")
        projects = test_scenario.list_projects()
        self.assertEqual(projects, ["test"])
        
    def test_set_project(self):

        # test that the set_project function works
        test_scenario = rsScenario("test", "sites.ramseysystems")
        test_scenario.set_project("new_test")
        self.assertEqual(test_scenario.project_name, "new_test")
        
    def test_del_project(self):
        
        # test that the del_project function works
        test_scenario = rsScenario("test", "sites.ramseysystems")
        test_scenario.del_project("new_test")
        
        # check the project has been deleted
        blob = test_scenario.bucket.blob("new_test/")
        self.assertEqual(blob.exists(), False) 
    
    def test_upload_provenance(self):
        
        # test that the upload_provenance function works
        test_scenario = rsScenario("test", "sites.ramseysystems")
        test_scenario.upload_provenance("./upload_provenance/Provenance.xlsx")
        
        # check the provenance list is not empty
        self.assertNotEqual(test_scenario.provenance, [])
        
    
    def test_upload_continuous_data(self):
        
        # test that the upload_continuous_data function works
        test_scenario = rsScenario("test", "sites.ramseysystems")
        test_scenario.upload_continuous_data("./upload_continuous_data/data.csv")
        
        # check the continuous data has been uploaded
        blob = test_scenario.bucket.blob("test/continuous_data/data.csv")
        self.assertEqual(blob.exists(), True)
    
    def test_upload_patient(self):
        
        ## make test file
        # test that the upload_patient function works
        test_scenario = rsScenario("test", "sites.ramseysystems")
        test_scenario.upload_patient("./upload_patient/patient.json")
        
        # check the patient has been uploaded
        blob = test_scenario.bucket.blob("test/personae/patient.json")
        self.assertEqual(blob.exists(), True)
    
    def test_upload_standard(self):
        
        ## make test file
        # test that the upload_standard function works
        test_scenario = rsScenario("test", "sites.ramseysystems")
        test_scenario.upload_standard("./upload_standard/standard.json")
        
        # check the standard has been uploaded
        blob = test_scenario.bucket.blob("test/standards/standard.json")
        self.assertEqual(blob.exists(), True)
    
    def test_del_standard(self):
        
        ## make test file
        # test that the del_standard function works
        test_scenario = rsScenario("test", "sites.ramseysystems")
        test_scenario.del_standard("standard.json")
        
        # check the standard has been deleted
        blob = test_scenario.bucket.blob("test/standards/standard.json")
        self.assertEqual(blob.exists(), False)
    
    def test_standard_path_list(self):
        pass
    
    def test_standards_list(self):
        
        # test that the standards_list function works
        test_scenario = rsScenario("test", "sites.ramseysystems")
        standards = test_scenario.standards_list()
        self.assertEqual(standards, ["standard.json"])
    
    def test_patient_list(self):
        
        # test that the patient_list function works
        test_scenario = rsScenario("test", "sites.ramseysystems")
        patients = test_scenario.patient_list()
        self.assertEqual(patients, ["patient.json"])
    
    def test_get_patient(self):
        pass
    
    def test_save_patient(self):
        
        # check the timestamp is updated
        test_scenario = rsScenario("test", "sites.ramseysystems")
        test_scenario.save_patient("save_patient/patient.json")
        
        # check the patient has been uploaded
        blob = test_scenario.bucket.blob("test/personae/patient.json")
        self.assertEqual(blob.exists(), True)
        
        # check the timestamp has been updated
        blob = test_scenario.bucket.blob("test/personae/patient.json")
        self.assertNotEqual(blob.updated, "2021-01-01T00:00:00.000Z")
        
    
    def test_del_patient(self):
        
        # test that the del_patient function works
        test_scenario = rsScenario("test", "sites.ramseysystems")
        test_scenario.del_patient("patient.json")
        
        # check the patient has been deleted
        blob = test_scenario.bucket.blob("test/personae/patient.json")
        self.assertEqual(blob.exists(), False)
    
    def test_validate_personae(self):
        
        ## check that the personae is valid. Make failing case
        # test that the validate_personae function works
        test_scenario = rsScenario("test", "sites.ramseysystems")
        test_scenario.validate_personae()
        self.assertEqual(test_scenario.validated, True)
    
    def test_render_story(self):
        pass
    
    def test_render_log(self):
        pass
    
    def test_render_data(self):
        pass
    
    def test_compile_website(self):
        
        # get current last modified date of the website folder
        test_scenario = rsScenario("test", "sites.ramseysystems")
        blob = test_scenario.bucket.blob("test/")
        last_modified = blob.updated
        
        # compile the website
        test_scenario.compile_website()
        
        # check the last modified date has been updated
        blob = test_scenario.bucket.blob("test/")
        self.assertNotEqual(blob.updated, last_modified)



if __name__ == '__main__':
    unittest.main()