# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import re
import arcpy
import sys
import traceback
import tempfile
import os

__author__ = "Coen Jonker"


class ColumnParser(object):
    def __init__(self):
        self.non_alpha_pattern = re.compile(r'[^A-Za-z0-9_]')
        self.ending = re.compile(r'_$')
        self.beginning = re.compile(r'^_')
        self.doubles = re.compile(r'__')
        self.next_number = {}

    def parseColname(self, name_in):
        temp = re.sub(self.doubles, '_',
                      re.sub(self.ending, '',
                             re.sub(self.beginning, '',
                                    re.sub(self.non_alpha_pattern, '_', name_in)
                                    )
                             )
                      )
        if temp[0] in '0123456789':
            temp = "N" + temp

        if temp in self.next_number:
            nn = self.next_number[temp]
            temp += "_{0}".format(nn)
            nn += 1
        else:
            nn = 1

        self.next_number[temp] = nn

        return temp


if __name__ == "__main__":
    input_xlsx = arcpy.GetParameterAsText(0)
    sheetname = arcpy.GetParameterAsText(1)
    workspace = arcpy.GetParameterAsText(3)
    input_fc = arcpy.GetParameterAsText(2)
    arcpy.env.overwriteOutput = True
    arcpy.env.workspace = workspace
    temppath = tempfile.mkdtemp()
    output_csv = os.path.join(temppath, "tactisch_plan_schiphol_parsed.csv")

    try:
        # Data inladen
        data = pd.read_excel(input_xlsx, sheetname=sheetname, skiprows=1, header=0)

        # Parser instantieren
        parser = ColumnParser()

        # Kolomnamen parsen
        colnames = [parser.parseColname(x) for x in data.columns]

        # Nieuwe kolomnamen aan dataframe toevoegen
        data.columns = colnames

        # data["Projectnummer_str"] = data["Projectnummer"].astype(str).apply(lambda x: x.split('.')[0])
        # OUDE CODE, POGING OM TABEL RECHTSTREEKS WEG TE SCHRIJVEN
        """
        n_array = np.array(np.rec.fromrecords(data.values))
        names = data.dtypes.index.tolist()
        n_array.dtype.names = tuple(names)
        arcpy.AddMessage(names)
        arcpy.da.NumPyArrayToTable(n_array, "Tactischplan")
        """

        # CSV wegschrijven
        data.to_csv(output_csv, index=False, encoding='utf-8')

        arcpy.TableToTable_conversion(output_csv, workspace, "Tactischplan")
        arcpy.AddField_management("Tactischplan", "ProjectNR_STR", "TEXT")
        arcpy.CalculateField_management("Tactischplan", "ProjectNR_STR", "str(int(!Projectnummer!))")
        arcpy.CopyFeatures_management(input_fc, "ingetekendTactischplan")
        arcpy.JoinField_management("ingetekendTactischplan", "PROJECTNUMMER", "Tactischplan", "ProjectNR_STR")

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
