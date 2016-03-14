import arcpy
import os
import sys

from arcpy import env

try:
    env.workspace = "C:/temp/Tactisch Plan"
    homeGDB = "C:/Users/Marco/Documents/ArcGIS/Projects/JumpstartDay/JumpstartDay.gdb"
    arcpy.TableToTable_conversion("tactisch_plan.csv", homeGDB, "tp")

except arcpy.ExecuteError:
    msgs = arcpy.GetMessages(2)
    print(msgs)

except:
    # Get the traceback object
    #
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]

    # Concatenate information together concerning the error into a message string
    #
    pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
    msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"

    # Return python error messages for use in script tool or Python Window
    #
    arcpy.AddError(pymsg)
    arcpy.AddError(msgs)

    # Print Python error messages for use in Python / Python Window
    #
    print(pymsg)
    print(msgs)
