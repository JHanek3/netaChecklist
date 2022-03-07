import logging
import datetime
import os
import requests
from hiddenHook import *

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

# Get Equipment for project then filter out, could be refactored to filter specific strings from excel in api call.
def getEquipmentLocation(ticket, projectID, id):
    try:
        url = "https://bim360field.autodesk.com/api/get_equipment/"
        data = {
                "ticket": ticket,
                "project_id": projectID,
                "details": "none",
                "equipment_ids": id,
                "ids_only": "1"
            }
        response = requests.post(url, data=data)
        if response.status_code == 200:
            jsonData = response.json()
            return jsonData[0]["area_id"]
        else:
            logging.error("Equipment Area ID API Call Error")
            return None
    except:
        logging.error("Equipment Area ID Try Block Error, might be a faulty Equipment ID")
        return None

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