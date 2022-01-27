import pandas as pd

# Get the IDS to filter for out request call
def getIDs(workbook):
    try:
        return list(workbook["B3F ID"])
    except:
        print("File .xlsx not found")