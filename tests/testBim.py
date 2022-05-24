import unittest
import functions.bim as bim
import pandas as pd
from postRequest import postRequest
import json

import os
from dotenv import load_dotenv

load_dotenv()
username = os.getenv("BIM_USERNAME")
password = os.getenv("BIM_PASSWORD")

# python -m unittest discover -s tests -t tests
class TestIntegration(unittest.TestCase):

    def testLoadBanks(self):
        
        # Test api integration
        
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

        customField = bim.getCustomFields(ticket, projectID)
        self.assertEqual(customField[0], os.getenv("LOAD_CUSTOM_FIELD"), "Should return a succesful api call to retrieve custom field id for NETA Checklist")
        self.assertEqual(customField[1], "Submitted", "Should return a succesful api call to retrieve custom field possible value for NETA Checklist")
        print(f"Custom Fields: {customField[0]}, {customField[1]}")
        
        testPath = os.path.join(os.getcwd(), "tests\\testLoadBanks.xlsx")
        workbook = pd.read_excel(testPath)
        
        equipmentJSON = bim.getEquipment(ticket, projectID, workbook["B3F ID"][0])
        areaID = equipmentJSON["area_id"]

        self.assertEqual(areaID, os.getenv("DKL_LOCATION"), "API call returns matching area IDS")
        print(f"Area ID of First Equipment: {areaID}")

        # Try to make it all one post request
        data = {
            "project_id": projectID,
            "ticket": ticket,
            "application_version": "4.0",
            "checklists": []
        }

        attachmentData = []
        for id, name, date, qaqc, inspec, path in zip(workbook["B3F ID"], workbook["Name"], workbook["Inspection Date"], 
            workbook["QAQC Authority"], workbook["Inspection Attendees"], workbook["File Path"]):
            
            newPost = postRequest(ticket, projectID, checklistTemplate[os.getenv("CHECKLIST_NAME")], id, name, "OK_TO_DELETE", company, areaID, date, qaqc, inspec, path)

            checklistData = newPost.formatPost()
            data["checklists"].append(checklistData)
            attachmentData.append([newPost.getGUID(), newPost.getPath(), equipmentJSON])
            
        data["checklists"] = json.dumps(data["checklists"])
        jsonData = json.dumps(data)
        postResponse = bim.post(jsonData)

        self.assertEqual(postResponse, True, "If batch succesfully posted to BIM 360 Field, call returns True")

        if postResponse:
            print("Batch Uploaded")
            
            for attachment in attachmentData:
                guid = attachment[0]
                filePath = attachment[1]
                equipmentJSON = attachment[2]
                
                data = bim.formatAttachment(ticket, projectID, guid, filePath)
                postAttachmentResponse = bim.till200(ticket, projectID, guid, data, filePath, "./", customField, equipmentJSON)

        self.assertEqual(postAttachmentResponse, True, "If attachment succesfully posted to BIM 360 Field, call returns True")
        
        print(f"Posted Completed Checklist 'OK_TO_DELETE' to Load Banks sort by Date Created to find.")
        self.assertEqual(bim.bimLogout(ticket), 200, "Should return a succesful logout of load banks")

    """
    def testDKL1(self):

         # Test api integration
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

        customField = bim.getCustomFields(ticket, projectID)
        self.assertEqual(customField[0], os.getenv("DKL1_CUSTOM_FIELD"), "Should return a succesful api call to retrieve custom field id for NETA Checklist")
        self.assertEqual(customField[1], "Submitted", "Should return a succesful api call to retrieve custom field possible value for NETA Checklist")
        print(f"Custom Fields: {customField[0]}, {customField[1]}")
    
        testPath = os.path.join(os.getcwd(), "tests\\testDKL1.xlsx")
        workbook = pd.read_excel(testPath)
        
        equipmentJSON = bim.getEquipment(ticket, projectID, workbook["B3F ID"][0])
        areaID = equipmentJSON["area_id"]

        self.assertEqual(areaID, os.getenv("DKL1_LOCATION"), "API call returns matching area IDS")
        print(f"Area ID of First Equipment: {areaID}")

        data = {
            "project_id": projectID,
            "ticket": ticket,
            "application_version": "4.0",
            "checklists": []
        }

        attachmentData = []
        for id, date, qaqc, inspec, path in zip(workbook["B3F ID"], workbook["Inspection Date"], 
                workbook["QAQC Authority"], workbook["Inspection Attendees"], workbook["File Path"]):
            
            
            newPost = postRequest(ticket, projectID, checklistTemplate[os.getenv("CHECKLIST_NAME")], id, "OK_TO_DELETE", "OK_TO_DELETE", company, areaID, date, qaqc, inspec, path)

            checklistData = newPost.formatPost()
            data["checklists"].append(checklistData)
            attachmentData.append([newPost.getGUID(), newPost.getPath(), equipmentJSON])
            
        data["checklists"] = json.dumps(data["checklists"])
        jsonData = json.dumps(data)
        postResponse = bim.post(jsonData)

        self.assertEqual(postResponse, True, "If batch succesfully posted to BIM 360 Field, call returns true")
        
        if postResponse:
            print("Batch uploaded")

            for attachment in attachmentData:
                guid = attachment[0]
                filePath = attachment[1]
                equipmentJSON = attachment[2]
                
                data = bim.formatAttachment(ticket, projectID, guid, filePath)
                postAttachmentResponse = bim.till200(ticket, projectID, guid, data, filePath, "./", customField, equipmentJSON)

        self.assertEqual(postAttachmentResponse, True, "If attachment succesfully posted to BIM 360 Field, call returns True")
        
        print(f"Posted Completed Checklist 'OK_TO_DELETE' to DKL1 sort by Date Created to find.")
        self.assertEqual(bim.bimLogout(ticket), 200, "Should return a succesful logout of load banks")
    """
    """
    def testDKL2(self):
         # Test api integration on DKL2

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

        customField = bim.getCustomFields(ticket, projectID)
        self.assertEqual(customField[0], os.getenv("DKL2_CUSTOM_FIELD"), "Should return a succesful api call to retrieve custom field id for NETA Checklist")
        self.assertEqual(customField[1], "Submitted", "Should return a succesful api call to retrieve custom field possible value for NETA Checklist")
        print(f"Custom Fields: {customField[0]}, {customField[1]}")

        testPath = os.path.join(os.getcwd(), "tests\\testDKL2.xlsx")
        workbook = pd.read_excel(testPath)

        equipmentJSON = bim.getEquipment(ticket, projectID, workbook["B3F ID"][0])
        areaID = equipmentJSON["area_id"]
        
        self.assertEqual(areaID, os.getenv("DKL2_LOCATION"), "API call returns matching area IDS")
        print(f"Area ID of First Equipment: {areaID}")

        data = {
            "project_id": projectID,
            "ticket": ticket,
            "application_version": "4.0",
            "checklists": []
        }

        attachmentData = []
        for id, date, qaqc, inspec, path in zip(workbook["B3F ID"], workbook["Inspection Date"], 
                workbook["QAQC Authority"], workbook["Inspection Attendees"], workbook["File Path"]):
            
            newPost = postRequest(ticket, projectID, checklistTemplate[os.getenv("CHECKLIST_NAME")], id, "OK_TO_DELETE", "OK_TO_DELETE", company, areaID, date, qaqc, inspec, path)

            checklistData = newPost.formatPost()
            data["checklists"].append(checklistData)
            attachmentData.append([newPost.getGUID(), newPost.getPath(), equipmentJSON])
            
        data["checklists"] = json.dumps(data["checklists"])
        jsonData = json.dumps(data)
        postResponse = bim.post(jsonData)

        self.assertEqual(postResponse, True, "If batch succesfully posted to BIM 360 Field, call returns true")

        if postResponse:
            print("Batch uploaded")

            for attachment in attachmentData:
                guid = attachment[0]
                filePath = attachment[1]
                equipmentJSON = attachment[2]
                
                data = bim.formatAttachment(ticket, projectID, guid, filePath)
                postAttachmentResponse = bim.till200(ticket, projectID, guid, data, filePath, "./", customField, equipmentJSON)

        self.assertEqual(postAttachmentResponse, True, "If attachment succesfully posted to BIM 360 Field, call returns True")

        print(f"Posted Completed Checklist 'OK_TO_DELETE' to DKL2 sort by Date Created to find.")
        
        self.assertEqual(bim.bimLogout(ticket), 200, "Should return a succesful logout of load banks")
    """
if __name__ == "__main__":
    unittest.main()