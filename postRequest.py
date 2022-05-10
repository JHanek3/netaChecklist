import uuid
import requests
from requests.structures import CaseInsensitiveDict
import json
from datetime import date, datetime
import os

class postRequest:
    def __init__(self, ticket, projectID, checklist, id, name, description, company, location, date, qaqc, inspec, path):
        self.ticket = ticket
        self.projectID = projectID
        self.checklist = checklist
        self.id = id
        self.name = name
        self.description = description
        self.company = company
        self.location = location
        self.date = date
        self.qaqc = qaqc
        self.inspec = inspec
        self.path = path
        self.GUID = self.checklistGUID()
        self.data = None
    
    def checklistGUID(self):
        return str(uuid.uuid4())
    
    def getChecklistItems(self):
        checklistItems = []
        for item in self.checklist["template_items"]:
            data = {
                    "location_detail": None,
                    "company_id": None,
                    "spec_ref": "",
                    "updated_at": "",
                    "response_type_id": item["response_type_id"],
                    "more_info": "",
                    "area_id": None,
                    "checklist_id": self.GUID,
                    "comment": None,
                    "touched": True,
                    "uploaded_at": None,
                    "position": item["position"],
                    "template_item_id": item["template_item_id"]
                }
            if item["is_section"] == True:
                data["is_section"] = True
                data["item_text"] = item["item_text"]
            else:
                data["is_section"] = False
                
                if item["response_type"]["display_type"] == "date":
                    data["response"] = str(self.date.date())
                
                # Person's Name
                elif item["position"] == 3:
                    data["response"] = self.qaqc
                
                # EEE, Company Name
                elif item["position"] == 4:
                    data["response"] = self.inspec
                
                else:
                    data["response"] = "Pass"
            checklistItems.append(data)
        # this is to replace None with Null
        jsonData = json.dumps(checklistItems)
        return jsonData
    
    def formatPost(self):
        checklistItems = self.getChecklistItems()
        data = {
            "project_id": self.projectID,
            "ticket": self.ticket,
            "application_version": "4.0",
            "checklists":
                """[{
                    \"id\":\"%(GUID)s\",\"template_id\":\"%(checklistTemplateID)s\",
                    \"identifier\":\"%(identifier)s\",\"name\":\"%(checklistTemplateName)s\",
                    \"responsible_company_id\":\"\", \"company_id\": \"%(companyID)s\",
                    \"company_name\": \"%(companyName)s\", \"status\":\"Closed\", 
                    \"checklist_type\":\"Commissioning\",\"priority\":\"Medium\",\"tags\":\"\",
                    \"project_id\":\"%(projectID)s\",\"created_by\":\"jhanek@cecco.com\",
                    \"created_at\":\"\",\"updated_at\":\"\",
                    \"description\":\"\",\"deleted_at\":\"\",\"area_id\":\"%(areaID)s\",
                    \"source_id\":\"%(sourceID)s\",\"source_type\":\"Equipment\",\"uploaded_at\":\"\",
                    \"checklist_items\":%(checklistItems)s
                }]""" % {"GUID": self.GUID, "checklistTemplateID": self.checklist["template_id"], "identifier": self.name, "checklistTemplateName": self.checklist["name"],
                        "companyID": self.company[0], "companyName":self.company[1], "projectID": self.projectID, "areaID": self.location, "sourceID": self.id, 
                        "checklistItems": checklistItems
                }
        }
        data["checklists"] = data["checklists"].replace("\n", "")
        # data["checklists"] = data["checklists"].replace(" ", "")

        # Formats name
        currentFormat = self.checklist["name"].replace(" ", "")
        data["checklists"] = data["checklists"].replace(currentFormat, self.checklist["name"])
        jsonData = json.dumps(data)
        return jsonData
    
    def formatAttachment(self):
        now = datetime.now()

        dateTimeStr = now.strftime("%Y-%m-%d %H:%M:%S") + " -6:00"
        createdStr = datetime.fromtimestamp(os.path.getctime(self.path)).strftime("%Y-%m-%d %H:%M:%S") + " -6:00"
        modStr = datetime.fromtimestamp(os.path.getmtime(self.path)).strftime("%Y-%m-%d %H:%M:%S") + " -6:00"

        data = {
            "ticket": self.ticket,
            "project_id": self.projectID,
            "fcreate_date": createdStr,
            "created_at": dateTimeStr,  
            "fmod_date": modStr,
            "updated_at": dateTimeStr, 
            "size": str(os.path.getsize(self.path)), 
            "content_type": "application/pdf", 
            "filename": os.path.basename(self.path), 
            "container_id": self.GUID, 
            "container_type": "CompletedChecklist"
        }

        return data

    def post(self):
        url = "https://bim360field.autodesk.com/api/checklists"
        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/json"
        headers["cache-control"] = "no-cache"
        data = self.formatPost()
        
        response = requests.post(url, headers=headers, data=data)
        
        if response.status_code == 200:
            return f"{self.name} uploaded..."
        else:
            today = date.today()
            file = open(f"{today} Failed Imports.txt", "a")
            file.write(f"Failed to import: {self.name}\n")
            file.close()
            return f"Error: {self.name}"
    
    def postAttachment(self):
        url = "https://bim360field.autodesk.com/api/attachments"

        payload = self.formatAttachment()
        files = {
                'attachment': (None, json.dumps(payload), 'application/json'),
                "original": (os.path.basename(self.path), open(self.path, "rb"), "application/pdf")
            }
        
        response = requests.post(url, data=payload, files=files)
        
        # Want to close the file
        files["original"][1].close()
        
        if response.status_code == 200:
            return f"{self.name} attachment uploaded..."
        
        else:
            today = date.today()
            file = open(f"{today} Failed Imports.txt", "a")
            file.write(f"Failed to import: {self.name}\n")
            file.close()
            return f"Error: {self.name}"

    def movePDF(self, currentPath, destinationPath):
        correctCurrentPath = currentPath.replace("\\", "/")
        fileName = correctCurrentPath.split("/")[-1]
        correctDestinationPath = f"{destinationPath}/{fileName}"
        os.rename(correctCurrentPath, correctDestinationPath)

        
    def __str__(self):
        return f"""Ticket: {self.ticket}\nProject ID: {self.projectID} ID: {self.id}\nEquipment Name: {self.name}\nDescription: {self.description}\nCompany: {self.company}\nStatus: "Closed"\nLocation: {self.location}\nSource: {self.id}"""
    