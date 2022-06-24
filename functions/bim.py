import logging
import datetime
import os
import requests
from hiddenHook import *
import re
import time
from requests.structures import CaseInsensitiveDict
from threading import Lock
from datetime import date
import json
import uuid

today = datetime.date.today()
today = today.strftime("%m/%d/%y").replace("/", "-")
logging.basicConfig(filename=os.path.join(os.getcwd() + f"\logs\{today}.txt"), encoding="utf-8", level=logging.DEBUG)

# Log in to Bim, has print statement
def bimLogin(username, password):
    url = "https://bim360field.autodesk.com/api/login"
    data = {"username": username, "password": password}
    
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("Logged In!")
            return response.json()["ticket"]
        else:
            logging.error("Failed API Call to Login")
            return None

    except:
        logging.error("Failure in Login Try Block")
        return None

# getProjectIDs, has print statement
def getProjectID(ticket):
    projects = {}
    url = "https://bim360field.autodesk.com/api/projects"
    data = {"ticket": ticket}
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            for x in response.json():
                projects[x["name"]] = x["project_id"]
            print("Projects Retrieved")
            return projects
        else:
            logging.error("Failed API Call to retrieve Project ID's")
            return None
    except:
        logging.error("Failure in getProjectID Try Block")
        return None

# Get Checklist template Name of L2C - ELEC - L2(5) NETA Checklist - Rev0
def getChecklistTemplateIDName(ticket, projectID):
    checklist = {}
    try:
        url = url = "https://bim360field.autodesk.com/api/templates"
        data = {
            "ticket": ticket, 
            "project_id": projectID,
            "application_version": "4.0"
        }

        if projectID == getLoadBanks():
            data["ids"] = getLoadBanksTemplate()
            
        elif projectID == getDKL1():
            data["ids"] = getDKL1Template()
        
        elif projectID == getDKL2():
            data["ids"] = getDKL2Template() 

        else:
            logging.error("Project IDs dont match up with hard coded ID's")
            return None

        response = requests.post(url, data=data).json()
        checklistName = response[0]["name"]
        checklist[checklistName] = response[0]

        return checklist    
    except:
        logging.error("Error in Checklist Template Retrieval...")
        return None

# Get Companies ID and Name
def getCompanyIDName(ticket, projectID):
    company = []
    try:
        url = "https://bim360field.autodesk.com/fieldapi/admin/v1/companies"
        data = {"ticket": ticket, "project_id": projectID}
        response = requests.post(url, data=data).json()
        for x in response:
            if x["name"] == getCompanyName():
                company.append(x["id"])
                company.append(x["name"])
        if len(company) == 0:
            logging.error("Company not found")
            return None

        return company
    except:
        logging.error("Error in Company Retrieval Try")
        return None

# Call custom fields @ start after retrieving the project id
# This is where the value for the toggle is located
def getCustomFields(ticket, projectID):
    
    try: 
        url = "https://bim360field.autodesk.com/api/custom_fields"
        data = {
            "ticket": ticket,
            "project_id": projectID,
        }
        response = requests.post(url, data = data)
        time.sleep(.5)
        if response.status_code == 200:
            jsonResponse = response.json()

            isMatch = False
            for json in jsonResponse:
                name = json["name"].lower().strip()
                
                # Regex acting weird for DKL L2(5) - NETA Checklist
                banks = re.compile("_test toggle_eee")
                # dkl = re.compile("l2(5) - neta checklist")
                # daRegex = re.compile("l2(5) - neta checklist")
                
                if banks.match(name) or "l2(5) - neta checklist" in name:
                    isMatch = True

                    valueFound = False
                    for value in json["possible_values"]:
                        if "submit" in value.lower():
                            valueFound = True
                            return json["custom_field_id"], value
                    
                    if valueFound == False:
                        logging.error("Submit not found in possible values")
                        print("Submit not found in possible values")
                        return None
                    
                    # For brekaing out of the json loop
                    break    
                
            if isMatch == False:
                logging.error("Regex match for Custom Field Name Failed")
                print("Regex match for Custom Field Name Failed")
                return None
                
        else:
            print("Custom Fields API call returned not 200")
            logging.error("Custom Fields API call returned not 200")
            return None

    except:
        print("Error in getting custom fields")
        logging.error("Custom Fields Try Block Error, might be a faulty api call.")
        return None

# Get Equipment for project then filter out, could be refactored to filter specific strings from excel in api call.
def getEquipment(ticket, projectID, id):
    try:
        url = "https://bim360field.autodesk.com/api/get_equipment/"
        data = {
                "ticket": ticket,
                "project_id": projectID,
                "details": "all",
                "equipment_ids": id,
                "ids_only": "1"
            }
        response = requests.post(url, data=data)
        if response.status_code == 200:
            jsonData = response.json()
            # return jsonData[0]
            return jsonData[0]
        else:
            logging.error("Equipment Area ID API Call Error")
            return None
    except:
        logging.error("Equipment Area ID Try Block Error, might be a faulty Equipment ID")
        return None

def post(data):
    # lock = Lock()
    # lock.acquire()
        
    url = "https://bim360field.autodesk.com/api/checklists"
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    headers["cache-control"] = "no-cache"
        
    response = requests.post(url, headers=headers, data=data)
    # lock.release()
        
    if response.status_code == 200:
        return True
    else:
        today = str(date.today()).split(" ")[0]
        file = open(f"{today} Failed Imports.txt", "a")
        file.write(f"Failed to import: Batch")
        file.close()
        return None

# Let's get if the checklist exists than attempt to attach an attachment to it
def checkIfChecklistExists(ticket, projectID, id):
    url = f"https://bim360field.autodesk.com/fieldapi/checklists/v1/{id}"
    data = {
        "ticket": ticket,
        "project_id": projectID
    }
    response = requests.get(url, data=data)
    return response

def formatAttachment(ticket, projectID, guid, filePath):
    now = datetime.datetime.now()

    dateTimeStr = now.strftime("%Y-%m-%d %H:%M:%S") + " -6:00"
    createdStr = datetime.datetime.fromtimestamp(os.path.getctime(filePath)).strftime("%Y-%m-%d %H:%M:%S") + " -6:00"
    modStr = datetime.datetime.fromtimestamp(os.path.getmtime(filePath)).strftime("%Y-%m-%d %H:%M:%S") + " -6:00"

    data = {
        "ticket": ticket,
        "project_id": projectID,
        "fcreate_date": createdStr,
        "created_at": dateTimeStr,  
        "fmod_date": modStr,
        "updated_at": dateTimeStr, 
        "size": str(os.path.getsize(filePath)), 
        "content_type": "application/pdf", 
        "filename": os.path.basename(filePath), 
        "container_id": guid, 
        "container_type": "CompletedChecklist"
    }

    return data

def postAttachment(data, filePath):
    # lock = Lock()
    url = "https://bim360field.autodesk.com/api/attachments"
    attachmentFile = open(filePath, "rb")

    files = {
            'attachment': (None, json.dumps(data), 'application/json'),
            "original": (os.path.basename(filePath), attachmentFile, "application/pdf")
    }

    # lock.acquire()
    response = requests.post(url, data=data, files=files)
    # lock.release()

    attachmentFile.close()

    # Don't remove this, the files fail to attach if you do
    # For some dumb reason the BIM 360 Field API needs the delay
    time.sleep(1)
    return response

# ERROR HANDLE IN HERE IF WE GET THE DELETE ATTACHMENT LOGIC TO WORK
def deleteAttachment(data, filePath):
    data["deleted"] = True
    # lock = Lock()
    url = "https://bim360field.autodesk.com/api/attachments"

    files = {
            'attachment': (None, json.dumps(data), 'application/json'),
            "original": (os.path.basename(filePath), open(filePath, "rb"), "application/pdf")
    }

    # lock.acquire()
    response = requests.post(url, data=data, files=files)
    # lock.release()

    if response.status_code == 200:
        print("Deleted")
    else:
        print("Uh oh")

def movePDF(currentPath, destinationPath):
    correctCurrentPath = currentPath.replace("\\", "/")
    fileName = correctCurrentPath.split("/")[-1]
    correctDestinationPath = f"{destinationPath}/{fileName}"
    os.rename(correctCurrentPath, correctDestinationPath)

def postSubmittedValue(ticket, projectID, jResObj, id, submitStr):
    custom_fields = jResObj["custom_field_values"]
    filteredObject = list(filter(lambda object: object["custom_field_definition_id"] == id, custom_fields))[0]
    
    if len(filteredObject) == 0:
        return None
    
    filteredObjectValue = filteredObject["value"].strip()
    
    url = "https://bim360field.autodesk.com/api/equipment"
    payload = {
            "ticket": ticket,
            "project_id": projectID,
        
            "equipment": json.dumps([{
                "id": jResObj["equipment_id"],
                "name": jResObj["name"],
                "description": jResObj["description"],
                "serial_number": jResObj["serial_number"],
                "created_by": jResObj["created_by"],
                "tag_number": jResObj["tag_number"],
                "barcode": jResObj["barcode"],
                "asset_identifier": jResObj["asset_identifier"],
                "purchase_order": jResObj["purchase_order"],
                "submittal": jResObj["submittal"],
                "purchase_date": jResObj["purchase_date"],
                "install_date": jResObj["install_date"],
                "warranty_start_date": jResObj["warranty_start_date"],
                "warranty_end_date": jResObj["warranty_end_date"],
                "expected_life": jResObj["expected_life"],
                "area_id": jResObj["area_id"],
                "bim_file_id": jResObj["bim_file_id"],
                "bim_object_identifier": jResObj["bim_object_identifier"],
                "source": "vfm",
                "equipment_type_id": jResObj["equipment_type_id"],
                "equipment_status_id": jResObj["equipment_status_id"],
                "custom_field_values": [{
                    "id": str(uuid.uuid4()),
                    "custom_field_definition_id": id,
                    "container_id": jResObj["equipment_id"],
                    "container_type": "Equipment",
                    "value": submitStr
                }]}
            ]) 
        }
    
    if filteredObjectValue == "" or filteredObjectValue == "Required" or filteredObjectValue == "N/A":
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            return True
        else:
            return None
    
def submittedLogic(ticket, projectID, customField, equipment):
    today = str(date.today()).split(" ")[0]
    file = open(f"{today} Submit Fields.txt", "a")
    name = equipment['name']

    if customField != None:
            submitResponse = postSubmittedValue(ticket, projectID, equipment, customField[0], customField[1])
            if submitResponse != None:
                file.write(f"{name}: Changed to 'Submitted'\n")
                return True
            else:
                print("Failed to update Submitted field")
                file.write(f"{name}: Still '{customField[1]}'\n")
    file.close()            

def till200(ticket, projectID, guid, data, filePath, folderPathActual, customField, equipmentJSON):
    count = 0
    while count != 3:
        checklistExistsReponse = checkIfChecklistExists(ticket, projectID, guid)
        if checklistExistsReponse.status_code == 200:
            count = 3
            break
        else:
            time.sleep(.25)
            count += 1
    attachmentResponse = postAttachment(data, filePath)
    time.sleep(1)
        
    if attachmentResponse.status_code == 200:
        print("Moving the file")
        movePDF(filePath, folderPathActual)
        
        if customField != None:
            submitResponse = postSubmittedValue(ticket, projectID, equipmentJSON, customField[0], customField[1])
            
            if submitResponse != None:
                return True
            else:
                print("Failed to updated Submitted field")
                today = str(date.today()).split(" ")[0]
                file = open(f"{today} Failed Imports.txt", "a")
                file.write(f"Failed to update Submitted field: {os.path.basename(filePath)} has value '{customField[1]}'\n")
                file.close()
    
    else:
        # Tried to delete the attachment did not work
        # deleteAttachment(data, filePath)
        # time.sleep(.5)
        print("Failed to import attachment")
        today = str(date.today()).split(" ")[0]
        file = open(f"{today} Failed Imports.txt", "a")
        file.write(f"Failed to import attachment (Submit value not updated): {os.path.basename(filePath)}\n")
        file.close()

def bimLogout(ticket):
    try:
        url = "https://bim360field.autodesk.com/api/logout"
        data = {"ticket": ticket}
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("Logged Out!")
            return 200
        else:
            logging.error("Failed To Log Out")
            return None
    except:
        logging.error("Error in Logout Try Block")
        return None


"""
You get a succesful, but the file that is attached is still corrupted
def till200(data, filePath, folderPathActual):
    count = 0
    while count != 3:
        response = postAttachment(data, filePath)
        time.sleep(1)
        
        if response.status_code == 200:
            print("Succesful")
            break
        else:
            deleteAttachment(data, filePath)
            print("Deleted failed attachment")
            time.sleep(.5)
            count += 1

    if count == 3:
        print("Error logged the file")
        today = str(date.today()).split(" ")[0]
        file = open(f"{today} Failed Imports.txt", "a")
        file.write(f"Failed to import attachment: {os.path.basename(filePath)}\n")
        file.close()
    else:
        print("Moving the file")
        # movePDF(filePath, folderPathActual)
        # self.postSubmittedValue(jsonObject, daID, daValue)
"""