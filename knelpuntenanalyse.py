# *-* coding: utf-8 *-*

__author__ = "Coen Jonker"

import arcpy
import arcpy.da
import sys
import traceback

fl_in = arcpy.GetParameterAsText(0)
fl_intersect = arcpy.GetParameterAsText(1)

searchtuple = ('SHAPE@', 'OID@', 'Projectnummer', 'Projectnaam', 'Verdieping')

meta_fields_int = ['OID', 'Projectnr', 'Projectnaam', 'Verdieping']
fields_int = ['SHAPE@']
fields_int += ['{0}_{1}'.format(x, y) for y in [1, 2] for x in meta_fields_int]

count = 0
line_printed = False
try:
    cursor_int = arcpy.da.InsertCursor(fl_intersect, fields_int)
    for row0 in arcpy.da.SearchCursor(fl_in, searchtuple):
        for row1 in arcpy.da.SearchCursor(fl_in, searchtuple):
            if not row0[0].disjoint(row1[0]) and row0[1] != row1[1]:
                intersection = row0[0].intersect(row1[0], 4)
                row = (intersection, row0[1], row0[2], row0[3], row0[4], row1[1], row1[2], row1[3], row1[4])
                cursor_int.insertRow(row)
                count += 1
                if not line_printed:
                    arcpy.AddMessage("Metafields: {0}".format(meta_fields_int))
                    arcpy.AddMessage("Row insert:\n")
                    for (f, v) in zip(fields_int, row):
                        arcpy.AddMessage("{0} -> {1}".format(f,v))
                    line_printed = True
    del cursor_int

    arcpy.AddMessage("{0} shapes should have been added".format(count))

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
