import unittest
import functions.bim as bim
import pandas as pd
from postRequest import postRequest

import os
from dotenv import load_dotenv

load_dotenv()
username = os.getenv("BIM_USERNAME")
password = os.getenv("BIM_PASSWORD")

# python -m unittest discover -s tests -t tests
class TestIntegration(unittest.TestCase):
    
    def testLoadBanks(self):
        """
        Test api integration
        """
        print("-"* 30)
        print("Load Banks")

        ticket = bim.bimLogin(username, password)
        print(f"Ticket: {ticket}")
        self.assertTrue(ticket, "Should return a succesful api call to login")
        
        projectIDs = bim.getProjectID(ticket)
        self.assertTrue(projectIDs, "Should return a succesful api call to retrieve projectIDS")
        projectID = os.getenv("LOAD_BANKS")
        print(f"Project ID for Load Banks: {projectID}")

        checklistTemplate = bim.getChecklistTemplateIDName(ticket, projectID)
        self.assertEqual(list(checklistTemplate.keys())[0], os.getenv("CHECKLIST_NAME"), "API call to retrieve checklist name")
        print(f"Checklist Template Name: {list(checklistTemplate.keys())[0]}")

        company = bim.getCompanyIDName(ticket, projectID)
        self.assertEqual(company[1], os.getenv("COMPANY_NAME"), "Should return a succesful api call to retrieve company credentials")
        print(f"Company Name: {company[1]}")
    
        testPath = os.path.join(os.getcwd(), "tests\\testLoadBanks.xlsx")
        workbook = pd.read_excel(testPath)
        
        areaID = bim.getEquipmentLocation(ticket, projectID, workbook["B3F ID"][0])
        areaID = os.getenv("DKL_LOCATION")
        print(f"Area ID of First Equipment: {areaID}")

        newPost = postRequest(ticket, projectID, checklistTemplate[os.getenv("CHECKLIST_NAME")], workbook["B3F ID"][0], "OK_TO_DELETE", "", 
            company, areaID, workbook["Inspection Date"][0], workbook["QAQC Authority"][0], workbook["Inspection Attendees"][0], workbook["File Path"][0])

        newPost.formatPost()
        newPost.formatAttachment()
        post = newPost.post()
        attachment = newPost.postAttachment()
        
        self.assertEqual(post, "OK_TO_DELETE uploaded...", "If succesfully posted to BIM 360 Field, the name of the equipment should be returned")
        self.assertEqual(attachment, "OK_TO_DELETE attachment uploaded...", "If succesfully posted to BIM 360 Field, the name of the equipment should be returned")
        
        print(f"Posted Completed Checklist 'OK_TO_DELETE' to Load Banks sort by Date Created to find.")
        
        self.assertEqual(bim.bimLogout(ticket), 200, "Should return a succesful logout of load banks")
    
    def testDKL1(self):
         """
         Test api integration
         """
         print("-"* 30)
         print("DKL1")

         ticket = bim.bimLogin(username, password)
         print(f"Ticket: {ticket}")
         self.assertTrue(ticket, "Should return a succesful api call to login")
        
         projectIDs = bim.getProjectID(ticket)
         self.assertTrue(projectIDs, "Should return a succesful api call to retrieve projectIDS")
         projectID = os.getenv("DKL1")
         print(f"Project ID for DKL1: {projectID}")

         checklistTemplate = bim.getChecklistTemplateIDName(ticket, projectID)
         self.assertEqual(list(checklistTemplate.keys())[0], os.getenv("CHECKLIST_NAME"), "API call to retrieve Checklist name")
         print(f"Checklist Template Name: {list(checklistTemplate.keys())[0]}")

         company = bim.getCompanyIDName(ticket, projectID)
         self.assertEqual(company[1], os.getenv("COMPANY_NAME"), "Should return a succesful api call to retrieve company credentials")
         print(f"Company Name: {company[1]}")
    
         testPath = os.path.join(os.getcwd(), "tests\\testDKL1.xlsx")
         workbook = pd.read_excel(testPath)
        
         areaID = bim.getEquipmentLocation(ticket, projectID, workbook["B3F ID"][0])
         self.assertEqual(areaID, os.getenv("DKL1_LOCATION"), "API call returns matching area IDS")
         print(f"Area ID of First Equipment: {areaID}")

         newPost = postRequest(ticket, projectID, checklistTemplate[os.getenv("CHECKLIST_NAME")], workbook["B3F ID"][0], "OK_TO_DELETE", "", 
            company, areaID, workbook["Inspection Date"][0], workbook["QAQC Authority"][0], workbook["Inspection Attendees"][0], workbook["File Path"][0])

         newPost.formatPost()
         newPost.formatAttachment()

         post = newPost.post()
         attachment = newPost.postAttachment()
         
         self.assertEqual(post, "OK_TO_DELETE uploaded...", "If succesfully posted to BIM 360 Field, the name of the equipment should be returned")
         self.assertEqual(attachment, "OK_TO_DELETE attachment uploaded...", "If succesfully posted to BIM 360 Field, the name of the equipment should be returned")
         
         print(f"Posted Completed Checklist 'OK_TO_DELETE' to DKL1 sort by Date Created to find.")
        
         self.assertEqual(bim.bimLogout(ticket), 200, "Should return a succesful logout of load banks")
         
    def testDKL2(self):
         """
         Test api integration on DKL2
         """
         print("-"* 30)
         print("DKL2")

         ticket = bim.bimLogin(username, password)
         print(f"Ticket: {ticket}")
         self.assertTrue(ticket, "Should return a succesful api call to login")

         projectIDs = bim.getProjectID(ticket)
         self.assertTrue(projectIDs, "Should return a succesful api call to retrieve projectIDS")
         projectID = os.getenv("DKL2")
         print(f"Project ID for DKL2: {projectID}")

         checklistTemplate = bim.getChecklistTemplateIDName(ticket, projectID)
         self.assertEqual(list(checklistTemplate.keys())[0], os.getenv("CHECKLIST_NAME"), "API call to retrieve Checklist name")
         print(f"Checklist Template Name: {list(checklistTemplate.keys())[0]}")

         company = bim.getCompanyIDName(ticket, projectID)
         self.assertEqual(company[1], os.getenv("COMPANY_NAME"), "Should return a succesful api call to retrieve company credentials")
         print(f"Company Name: {company[1]}")

         testPath = os.path.join(os.getcwd(), "tests\\testDKL2.xlsx")
         workbook = pd.read_excel(testPath)

         areaID = bim.getEquipmentLocation(ticket, projectID, workbook["B3F ID"][0])
         self.assertEqual(areaID, os.getenv("DKL2_LOCATION"), "API call returns matching area IDS")
         print(f"Area ID of First Equipment: {areaID}")
        
         newPost = postRequest(ticket, projectID, checklistTemplate[os.getenv("CHECKLIST_NAME")], workbook["B3F ID"][0], "OK_TO_DELETE", "", 
            company, areaID, workbook["Inspection Date"][0], workbook["QAQC Authority"][0], workbook["Inspection Attendees"][0], workbook["File Path"][0])

         newPost.formatPost()
         newPost.formatAttachment()

         post = newPost.post()
         attachment = newPost.postAttachment()
         
         self.assertEqual(post, "OK_TO_DELETE uploaded...", "If succesfully posted to BIM 360 Field, the name of the equipment should be returned")
         self.assertEqual(attachment, "OK_TO_DELETE attachment uploaded...", "If succesfully posted to BIM 360 Field, the name of the equipment should be returned")
        
         print(f"Posted Completed Checklist 'OK_TO_DELETE' to DKL2 sort by Date Created to find.")

         self.assertEqual(bim.bimLogout(ticket), 200, "Should return a succesful logout of DKL2")

if __name__ == "__main__":
    unittest.main()