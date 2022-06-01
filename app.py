from tkinter import *
from tkinter import ttk,  messagebox, filedialog
import functions.bim as bim
import functions.tkinter as tkFun
import functions.xcel as excel
import os
import pandas as pd
from postRequest import postRequest
from datetime import date
import time
from hiddenHook import * 
import sys
import json

# pyinstaller --noconsole --onefile --additional-hooks-dir=hiddenHook.py app.py
def main():
    # Create the entire GUI program
    program = Program()

    # Start the GUI event loop
    program.window.mainloop()
class Program:
    def __init__(self):
        # Create the window
        self.window = Tk()
        self.window.title("Checklist Automatic-O")
        self.window.withdraw()
        
        self.ticket = None
        self.projects = None
        self.projectID = None

        self.checklistData = None

        self.filePath = None
        self.filePathActual = ""
        self.MovePDFs = None
        self.folderPathActual = ""
        self.checkboxValue = None
        
        self.browseButton = None
        self.movePDFButton = None
        self.checkboxButton = None
        self.submitButton = None
        
        self.verifyTicket()
        self.setUpDropdowns()
        self.setUpLabels()

    def verifyTicket(self):
        self.ticket = bim.bimLogin(getUsername(), getPassword())
        self.projects = bim.getProjectID(self.ticket)

        if self.ticket and self.projects:
            tkFun.formatWindow(self.window)
        else:
            messagebox.showerror("Authentication", "Login Failed")
            self.window.destroy()
    
    def setUpDropdowns(self):
        def callback(*args):
            for x in self.projects.keys():
                if x == menu.get():
                    self.projectID = self.projects[x]
            
            checklist = bim.getChecklistTemplateIDName(self.ticket, self.projectID)
            if not checklist:
                messagebox.showerror("Checklist Template", "Error in Checklist Template Retrieval\nClosing App...")
                self.window.destroy()
            
            self.checklistData = checklist[getChecklistName()]
            self.browseButton.configure(state="normal")

        menu = StringVar(self.window)
        menu.set("Select a project")
        drop0 = OptionMenu(self.window, menu, *list(self.projects.keys()))
        drop0.pack(pady=5)
        menu.trace("w", callback) 


    def setUpLabels(self):
        # Create the Button
        self.browseButton = ttk.Button(self.window, text="Browse", state="disabled")
        self.browseButton.pack(pady=2.5)
        self.browseButton['command'] = self.openFile

        # Create the label to be altered for File Name
        self.filePath = ttk.Label(self.window, text="File: __________", font=('Georgia 13'))
        self.filePath.pack(pady=2.5)

        # No longer needed since attachment logic removed
        # self.movePDFButton = ttk.Button(self.window, text="Browse", state="disabled")
        # self.movePDFButton.pack(pady=2.5)
        # self.movePDFButton['command'] = self.getFolder

        # Create the label to be altered for movePDFS
        # self.MovePDFs = ttk.Label(self.window, text="Folder: ________", font=('Georgia 13'))
        # self.MovePDFs.pack(pady=2.5)

        # Create the checkmark for user to click whether or not they want Submitted value added to the Equipment
        self.checkboxValue = IntVar()
        self.checkboxButton = ttk.Checkbutton(self.window, text="Add Submitted Field?", variable=self.checkboxValue, onvalue=1, offvalue=0)
        self.checkboxButton.pack(pady=2.5)
        
        # Create the submit button
        """
        Added multithreading, but then the attachment started acting weird
        self.submitButton = ttk.Button(self.window, text="Submit", state="disabled", command= lambda: self.submit())
        t1 = threading.Thread(target=self.submit)
        t1.daemon = True
        self.submitButton = ttk.Button(self.window, text="Submit", state="disabled", command=t1.start)
        """
        self.submitButton = ttk.Button(self.window, text="Submit", state="disabled", command= lambda: self.submit())
        self.submitButton.pack(pady=5)

    # Gets the Excel File Window Path
    def openFile(self):
        file = filedialog.askopenfile(mode='r')
        if file:
            osFile = os.path.abspath(file.name)
            if str(osFile[-5:]) != ".xlsx":
                messagebox.showerror("Input .xlsx", "Not a .xlsx file, use templateLoadBanks.xlsx as a guide.")
            else:
                workbook = pd.read_excel(open(osFile, 'rb'), index_col=[0])
                dataColumns = list(workbook.columns)

                # Checks to make sure there are no duplicates
                areThereDuplicates = excel.checkDuplicates(workbook)

                # Checks to make sure all file paths are valid
                # validFilePaths = excel.verifyFilePath(workbook)

                # Checks if columns are formatted correctly
                # , 'File Path'
                if dataColumns != ['B3F ID', 'Name', "Description", 'Inspection Date', 'QAQC Authority', 'Inspection Attendees']:
                    messagebox.showerror("Improperly Formatted Header", "Desired Headers: B3F ID, Name, Inspection Date, QAQC Authority, Inspection Attendees")
                
                elif areThereDuplicates[0] == True:
                    messagebox.showerror("Duplicated Detected", areThereDuplicates[1])

                # elif validFilePaths == "Empty":
                #     messagebox.showerror("Error in File Paths", "Empty File Path")

                # elif validFilePaths == "Invalid":
                #     messagebox.showerror("Error in File Paths", "A File Path is not a valid file")

                else:
                    prettyPrint = str(osFile)
                    self.filePathActual = prettyPrint
                    self.filePath["text"] = "File: " + prettyPrint.split("\\")[-1]
                    # self.movePDFButton["state"] = "enable"
                    # self.browseButton["state"] = "disable"
                    self.submitButton["state"] = "enable"

    def getFolder(self):
        folder = filedialog.askdirectory()
        prettyPrint = str(folder)

        self.folderPathActual = prettyPrint
        self.MovePDFs["text"] = "Folder: " + prettyPrint.split("/")[-1]
        
        self.submitButton["state"] = "enable"

    def companyLogicAndFields(self, progress, progressMsg):
        company = bim.getCompanyIDName(self.ticket, self.projectID)
        if not company:
            messagebox.showerror("Company Retrieval", "Failed to retrieve Company ID.\nClosing App...")
            self.window.destroy()
            return None

        progress["value"] = 5
        progressMsg["text"] = "Company ID retrieved..."
        self.window.update()
        time.sleep(.25)
        
        return company
    
    def customFieldsLogicAndFields(self):
        if self.checkboxValue.get() == 1:
            customField = bim.getCustomFields(self.ticket, self.projectID)
            if not customField:
                messagebox.showerror("Custom Field Retrieval", "Failed to retrieve Custom Field NETA.\nClosing App...")
                self.window.destroy()
                return None
            return customField
        else:
            return None

    # The data call is way in the beginning @ dropdown
    def netaChecklistTemplateLogicAndFields(self, progress, progressMsg):
        progress["value"] += 5
        progressMsg["text"] = "NETA Checklist Field Found..."
        self.window.update()
        time.sleep(.25)
    
    def workbookLogicAndFields(self, progress, progressMsg):
        workbook = pd.read_excel(self.filePathActual)
        progress["value"] += 5
        progressMsg["text"] = "Excel Data Retrieved..."
        self.window.update()

        postProgressBar = 80 / len(workbook["B3F ID"])

        return workbook, postProgressBar

    def postLogicAndFields(self, workbook, company, progress, progressMsg, postProgressBar):
        
        data = {
            "project_id": self.projectID,
            "ticket": self.ticket,
            "application_version": "4.0",
            "checklists": []
        }

        equipmentData = []
        # , workbook["File Path"]
        for id, name, description, date, qaqc, inspec in zip(workbook["B3F ID"], workbook["Name"], workbook["Description"], workbook["Inspection Date"], 
                 workbook["QAQC Authority"], workbook["Inspection Attendees"]):
            
            equipmentJSON = bim.getEquipment(self.ticket, self.projectID, id)
            areaID = equipmentJSON["area_id"]
            
            if areaID == None:
                messagebox.showerror("Area ID", "Failed to retrieve Area ID, might be a faulty Equipment ID.\nClosing App...")
                self.window.destroy()
                break
            
            newPost = postRequest(self.ticket, self.projectID, self.checklistData, id, name, description, company, areaID, date, qaqc, inspec)
            checklistDataFormated = newPost.formatPost()

            data["checklists"].append(checklistDataFormated)
            equipmentData.append(equipmentJSON)
            
        data["checklists"] = json.dumps(data["checklists"])
        jsonData = json.dumps(data)
        postResponse = bim.post(jsonData)

        if postResponse:
            print("Batch uploaded")
            progressMsg["text"] = "Batch Uploaded..."
            progress["value"] += postProgressBar
            self.window.update()
            time.sleep(.75)
            return equipmentData
        else:
            messagebox.showerror("Error in Batch Upload", "The whole batch did not upload...")
            return None

    def postSubmitValues(self, progress, progressMsg, customField, equipmentData):
        if equipmentData == None:
            return None
        
        progressMsg["text"] = "Working on Submitted Fields..."
        self.window.update()
        
        for equipment in equipmentData:
            # print(equipment)
            bim.submittedLogic(self.ticket, self.projectID, customField, equipment)
        
        progressMsg["text"] = "Fields Uploaded..."
        print("Fields Uploaded")
        progress["value"] = 100
        self.window.update()
    
    def attachmentLogicAndFields(self, progress, progressMsg, postProgressBar, customField, attachmentData):

        if attachmentData == None:
            return None
        
        progressMsg["text"] = "Working on Attachments..."
        self.window.update()
        
        for attachment in attachmentData:
            guid = attachment[0]
            filePath = attachment[1]
            equipmentJSON = attachment[2]
            data = bim.formatAttachment(self.ticket, self.projectID, guid, filePath)

            bim.till200(self.ticket, self.projectID, guid, data, filePath, self.folderPathActual, customField, equipmentJSON)
        
        progressMsg["text"] = "Attachments Uploaded..."
        print("Attachments Uploaded")
        progress["value"] += postProgressBar
        self.window.update()

    def closeFileLogicAndFields(self, progress, progressMsg):
        today = date.today()
        if os.path.exists(f"{today} Failed Imports.txt"):
            messagebox.showwarning("Failed Imports", f"Some Checklists failed to import.\nCheck '{today} Failed Imports.txt' for more info.")

        
        logout = bim.bimLogout(self.ticket)
        
        # Not really a problem
        if not logout:
            messagebox.showerror("Logging Out", "Failed to Logout.\nClosing App...")
            self.window.destroy()
        
        progressMsg["text"] = "Logged Out..."
        progress["value"] += 10
        progressMsg.destroy()
        progress.destroy()
        
        messagebox.showinfo("Authentication", "Succesfully Logged Out!\nClosing App...")
        self.window.destroy()
        
        sys.exit()
   
    def submit(self):

        self.submitButton["state"] = "disabled"
        progress = ttk.Progressbar(self.window, orient = HORIZONTAL, length = 200, mode = "determinate")
        progress.pack(pady = 5)
        
        progressMsg = ttk.Label(self.window, text="Reading File...", font=('Georgia 7'))
        progressMsg.pack(pady = 5)
        
        company = self.companyLogicAndFields(progress, progressMsg)

        customField = self.customFieldsLogicAndFields()
        
        self.netaChecklistTemplateLogicAndFields(progress, progressMsg)

        workbook, postProgressBar = self.workbookLogicAndFields(progress, progressMsg)

        equipmentData = self.postLogicAndFields(workbook, company, progress, progressMsg, postProgressBar)

        self.postSubmitValues(progress, progressMsg, customField, equipmentData)
        # self.attachmentLogicAndFields(progress, progressMsg, postProgressBar, customField, attachmentGuids)
        
        self.closeFileLogicAndFields(progress, progressMsg)

if __name__ == "__main__":
    main()
