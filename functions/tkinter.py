from tkinter import *
from tkinter import ttk, filedialog, messagebox
from tkinter.filedialog import askopenfile


# Formats the window
def formatWindow(window):
    messagebox.showinfo("Authentication", "Logged In!")
    window.deiconify()
    
    # Gets the requested values of the height and width.
    # get the screen dimension
    windowWidth = 700
    windowHeight = 350
    
    screenWidth = window.winfo_screenwidth()
    screenHeight = window.winfo_screenheight()
    centerX = int(screenWidth/2 - windowWidth / 2)
    centerY = int(screenHeight/2 - windowHeight / 2)

    window.geometry(f'{windowWidth}x{windowHeight}+{centerX}+{centerY}')
    
    # Add a Title Label widget
    label0 = Label(window, text="Click the Button to input the template .xlsx", font=('Georgia 13'))
    label0.pack(pady=10)
