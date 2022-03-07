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
        self.window.geometry("700x350")
        self.window.withdraw()
        
        self.ticket = None
        self.projects = None
        self.projectID = None

        self.checklistData = None

        self.filePath = None
        self.filePathActual = ""
        self.browseButton = None
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
        self.browseButton.pack(pady=20)
        self.browseButton['command'] = self.openFile

        # Create the label to be altered
        self.filePath = ttk.Label(self.window, text="File: __________", font=('Georgia 13'))
        self.filePath.pack(pady=5)

        # Create the submit button
        self.submitButton = ttk.Button(self.window, text="Submit", state="disabled", command= lambda: self.submit())
        self.submitButton.pack(pady=10)

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

                # Checks if columns are formatted correctly
                if dataColumns != ['B3F ID', 'Name', 'Inspection Date', 'QAQC Authority', 'Inspection Attendees']:
                    messagebox.showerror("Improperly Formatted Header", "Desired Headers: B3F ID, Name, Inspection Date, QAQC Authority, Inspection Attendees")
                
                elif areThereDuplicates[0] == True:
                    messagebox.showerror("Duplicated Detected", areThereDuplicates[1])

                else:
                    prettyPrint = str(osFile)
                    self.filePathActual = prettyPrint
                    print(self.filePathActual)
                    self.filePath["text"] = "File: " + prettyPrint.split("\\")[-1]
                    self.submitButton["state"] = "enable"

    def finishClose(self, msg, bar):
        today = date.today()
        if os.path.exists(f"{today} Failed Imports.txt"):
            messagebox.showwarning("Failed Imports", f"Some Checklists failed to import.\nCheck '{today} Failed Imports.txt' for more info.")

        
        logout = bim.bimLogout(self.ticket)
        # Not really a problem
        if not logout:
            messagebox.showerror("Logging Out", "Failed to Logout.\nClosing App...")
            self.window.destroy()
        msg["text"] = "Logged Out..."
        bar["value"] += 10
        msg.destroy()
        bar.destroy()
        messagebox.showinfo("Authentication", "Succesfully Logged Out!\nClosing App...")
        self.window.destroy()
    
    def submit(self):
        self.submitButton["state"] = "disabled"
        progress = ttk.Progressbar(self.window, orient = HORIZONTAL, length = 200, mode = "determinate")
        progress.pack(pady = 5)
        
        progressMsg = ttk.Label(self.window, text="Reading File...", font=('Georgia 7'))
        progressMsg.pack(pady = 5)
        
        company = bim.getCompanyIDName(self.ticket, self.projectID)
        if not company:
            messagebox.showerror("Company Retrieval", "Failed to retrieve Company ID.\nClosing App...")
            self.window.destroy()
            
        progress["value"] = 5
        progressMsg["text"] = "Company ID retrieved..."
        self.window.update_idletasks()
        
        workbook = pd.read_excel(self.filePathActual)
        progress["value"] += 5
        progressMsg["text"] = "Opening File..."
        
        
        postProgressBar = 80 / len(workbook["B3F ID"])
        for id, name, date, qaqc, inspec in zip(workbook["B3F ID"], workbook["Name"], workbook["Inspection Date"], workbook["QAQC Authority"], workbook["Inspection Attendees"]):
            areaID = bim.getEquipmentLocation(self.ticket, self.projectID, id)
            if areaID == None:
                messagebox.showerror("Area ID", "Failed to retrieve Area ID, might be a faulty Equipment ID.\nClosing App...")
                self.window.destroy()
                break
            
            newPost = postRequest(self.ticket, self.projectID, self.checklistData, id, name, "", company, areaID, date, qaqc, inspec)
            newPost.formatPost()
            post = newPost.post()

            progressMsg["text"] = f"{post}"
            progress["value"] += postProgressBar
            self.window.update_idletasks()
            # LOL
            time.sleep(1)
        
        self.finishClose(progressMsg, progress)
        

if __name__ == "__main__":
    main()
