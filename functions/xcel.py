import pandas as pd
import os

# Get the IDS to filter for out request call
def getIDs(workbook):
    try:
        return list(workbook["B3F ID"])
    except:
        print("File .xlsx not found")

# Check B3F IDs for duplicates
# If duplicate send error with populated dictionary
def checkDuplicates(dataFrame):
    isDuplicated = dataFrame.duplicated(subset="B3F ID")
    duplicatedDictionary = {}
    finalString = ""
    for index, value in isDuplicated.items():
        if value == True:
            id = dataFrame.iloc[index]["B3F ID"]
            if id in duplicatedDictionary.keys():
                duplicatedDictionary[id] += 1
            else:
                duplicatedDictionary[id] = 1
    
    if len(duplicatedDictionary) > 0:
        for key, value in duplicatedDictionary.items():
            finalString += f"{key}: {value}\n"
        return True, finalString
    else:
        return False, finalString

#TODO: Error handles return individual rows where the error occured
#TODO: Make sure all files are pdfs
def verifyFilePath(dataFrame):
    filesPass = False
    # Error Handeling if a file path is blank
    if dataFrame["File Path"].isnull().values.any():
        filesPass = "Empty"
        return filesPass
    
    for file in dataFrame["File Path"]:
        formattedFile = os.path.abspath(file)
        if not os.path.isfile(formattedFile):
            filesPass = "Invalid"
            return filesPass
    
    # Probably unnecessary with how I handle the error processing
    filesPass = True
    return filesPass
