# *-* coding: utf-8 *-*

__author__ = "Coen Jonker"

import arcpy
import arcpy.da


fl_in = arcpy.GetParameterAsText(0)
fl_intersect = arcpy.GetParameterAsText(1)

searchtuple = ('OID@', 'SHAPE@', 'Projectnaam')

meta_fields_int = ['OID', 'Projectnr', 'Projectnaam']
fields_int = ['SHAPE@']
fields_int += ['{0}_{1}'.format(x, y) for y in [1, 2] for x in meta_fields_int]

with arcpy.da.InsertCursor(fl_intersect, ) as cursor_int:
    for row0 in arcpy.da.SearchCursor(fl_in, searchtuple):
        for row1 in arcpy.da.SearchCursor(fl_in, searchtuple):
            if row0[1].overlaps(row1[1]) and row0[0] != row1[0]:

                arcpy.AddMessage("Overlap: {0} -> {2} met {1} -> {3}".format(row0[0], row1[0], row0[2], row1[2]))
