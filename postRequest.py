import uuid
class postRequest:
    def __init__(self, ticket, projectID, checklist, id, name, description, company, location, date, qaqc, inspec, path):
        self.ticket = ticket
        self.projectID = projectID
        self.checklist = checklist
        self.id = id.strip()
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
        # jsonData = json.dumps(checklistItems)
        # return jsonData
        return checklistItems
    def formatPost(self):
        checklistItems = self.getChecklistItems()

        # Goofy is not a number from pandas
        if str(self.description) == "nan":
            self.description = ""
        
        data = {
            "id": self.GUID, "template_id": self.checklist["template_id"], "identifier": self.name,
            "name": self.checklist["name"], "responsible_company_id": "", "company_id": self.company[0],
            "company_name": self.company[1], "status": "Closed", "checklist_type": "Commissioning", 
            "priority": "Medium", "tags": "", "project_id": self.projectID, "created_by": "jhanek@cecco.com",
            "created_at": "", "updated_at": "", "description": self.description, "deleted_at": "", "area_id": self.location,
            "source_id": self.id, "source_type": "Equipment", "uploaded_at": "", "checklist_items": checklistItems
        }
        
        return data

        # data = {
        #     "project_id": self.projectID,
        #     "ticket": self.ticket,
        #     "application_version": "4.0",
        #     "checklists":
        #         """[{
        #             \"id\":\"%(GUID)s\",\"template_id\":\"%(checklistTemplateID)s\",
        #             \"identifier\":\"%(identifier)s\",\"name\":\"%(checklistTemplateName)s\",
        #             \"responsible_company_id\":\"\", \"company_id\": \"%(companyID)s\",
        #             \"company_name\": \"%(companyName)s\", \"status\":\"Closed\", 
        #             \"checklist_type\":\"Commissioning\",\"priority\":\"Medium\",\"tags\":\"\",
        #             \"project_id\":\"%(projectID)s\",\"created_by\":\"jhanek@cecco.com\",
        #             \"created_at\":\"\",\"updated_at\":\"\",
        #             \"description\":\"%(description)s\",\"deleted_at\":\"\",\"area_id\":\"%(areaID)s\",
        #             \"source_id\":\"%(sourceID)s\",\"source_type\":\"Equipment\",\"uploaded_at\":\"\",
        #             \"checklist_items\":%(checklistItems)s
        #         }]""" % {"GUID": self.GUID, "checklistTemplateID": self.checklist["template_id"], "identifier": self.name, "checklistTemplateName": self.checklist["name"],
        #                 "companyID": self.company[0], "companyName":self.company[1], "projectID": self.projectID, "description": self.description, "areaID": self.location, 
        #                 "sourceID": self.id, "checklistItems": checklistItems
        #         }
        # }
        # data["checklists"] = data["checklists"].replace("\n", "")
        # data["checklists"] = data["checklists"].replace(" ", "")
        # # Formats name
        # currentFormat = self.checklist["name"].replace(" ", "")
        # data["checklists"] = data["checklists"].replace(currentFormat, self.checklist["name"])
        # jsonData = json.dumps(data)
        # print(jsonData)
        # return jsonData

    def getGUID(self):
        return self.GUID
    
    def getPath(self):
        return self.path
    def __str__(self):
        return f"""Ticket: {self.ticket}\nProject ID: {self.projectID} ID: {self.id}\nEquipment Name: {self.name}\nDescription: {self.description}\nCompany: {self.company}\nStatus: "Closed"\nLocation: {self.location}\nSource: {self.id}"""
    