from rsScenario import rsScenario
from google.cloud import storage

import pytest
import unittest
import jinja2

class TestScenarioTool(unittest.TestCase):
    def test_init(self):

        # test that the init function works
        test_scenario = rsScenario("Diabetes", "sites.ramseysystems")
        self.assertEqual(test_scenario.project_name, "diabetes")
        self.assertEqual(test_scenario.gcp_project, "sites.ramseysystems")
        self.assertEqual(test_scenario.validated, False)
        self.assertEqual(test_scenario.standard_dir, "sites.ramseysystems/diabetes/standards")
        self.assertEqual(test_scenario.personae_dir, "sites.ramseysystems/diabetes/personae")
        self.assertEqual(test_scenario.continuous_data_dir, "sites.ramseysystems/diabetes/continuous_data")
        self.assertEqual(test_scenario.storage_client, storage.Client())
        self.assertEqual(test_scenario.provenance, [])
        self.assertIsInstance(test_scenario.template_env, jinja2.Environment) # how do i test this is right. Do i check the class type?
        self.assertEqual(test_scenario.bucket, test_scenario.storage_client.get_bucket("sites.ramseysystems"))
        
    def test_copy_project(self):

        # test that the copy_project function works
        test_scenario = rsScenario("Diabetes", "sites.ramseysystems")
        test_scenario.copy_project("Diabetes", "new_diabetes")
        
        # go on to the GCP bucket and check that the new project has been created
        new_dir_blob = test_scenario.bucket.blob("new_diabetes/standards/")
        self.assertEqual(new_dir_blob.exists(), True)
        
        # check the contents of the new project
        original_blobs = test_scenario.bucket.list_blobs(prefix="diabetes/")
        new_blobs = test_scenario.bucket.list_blobs(prefix="new_diabetes/")
        
        # check they are the same length
        self.assertEqual(len(list(original_blobs)), len(list(new_blobs)))
        
        original_files = {blob.name: blob.size for blob in original_blobs}
        new_files = {blob.name: blob.size for blob in new_blobs}

        # Ckeck the content and their sizes are the same
        for filename in original_files:
            new_filename = filename.replace("Diabetes", "new_diabetes")
            self.assertTrue(new_filename in new_files)
            self.assertEqual(original_files[filename], new_files[new_filename])
            
    def test_list_projects(self):

        # test that the list_projects function works
        test_scenario = rsScenario("Diabetes", "sites.ramseysystems")
        projects = test_scenario.list_projects()
        self.assertEqual(projects, ["diabetes"])
        
    def test_set_project(self):

        # test that the set_project function works
        test_scenario = rsScenario("Diabetes", "sites.ramseysystems")
        test_scenario.set_project("new_diabetes")
        self.assertEqual(test_scenario.project_name, "new_diabetes")
        
    def test_del_project(self):
        pass
    
    def test_upload_provenance(self):
        pass
    
    def test_upload_continuous_data(self):
        pass
    
    def test_upload_patient(self):
        pass
    
    def test_upload_standard(self):
        pass
    
    def test_del_standard(self):
        pass
    
    def test_standard_path_list(self):
        pass
    
    def test_standards_list(self):
        pass
    
    def test_patient_list(self):
        pass
    
    def test_get_patient(self):
        pass
    
    def test_save_patient(self):
        pass
    
    def test_del_patient(self):
        pass
    
    def test_validate_personae(self):
        pass
    
    def test_render_story(self):
        pass
    
    def test_render_log(self):
        pass
    
    def test_render_data(self):
        pass
    
    def test_compile_website(self):
        pass
    
