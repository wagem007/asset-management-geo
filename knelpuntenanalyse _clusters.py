# *-* coding: utf-8 *-*

__author__ = "Coen Jonker"

import arcpy
import arcpy.da
import sys
import traceback
import copy



fl_in = arcpy.GetParameterAsText(0)
workspace = arcpy.GetParameterAsText(1)


fieldmapper = (
    ('OID@', 'OID', 'LONG'),
    ('Projectnummer', 'Projectnummer', 'TEXT'),
    ('Projectnaam', 'Projectnaam', 'TEXT'),
    ('Verdieping', 'Verdieping', 'LONG')
)

verdieping_field = 'Verdieping'

start_date_field = 'Begindatum'
end_date_field = 'Einddatum'

class Cluster(object):

    def __init__(self):
        self.shape = None
        self.verdieping = None
        self.rowlist = []

    def overlaps(self, query_shape, query_verdieping):
        if not self.shape:
            return True
        if self.shape.disjoint(query_shape):
            arcpy.AddMessage("NO OVERLAP!")
            return False
        return True

    def add(self, shape, row, verdieping):
        if self.shape:
            self.shape = self.shape.union(shape)
        else:
            self.shape = copy.deepcopy(shape)
            self.verdieping = verdieping
        self.rowlist.append(row)

class Clusterbuilder(object):

    def __init__(self, fl, workspace, fieldmapper, verdieping_field, fl_prefix='Projectcluster'):
        self.fl = fl
        self.workspace = workspace
        self.fl_prefix = fl_prefix
        self.search_meta, self.meta_fields, field_types = zip(*fieldmapper)

        if verdieping_field not in self.search_meta:
            self.search_meta += (verdieping_field, )

        self.verdieping_index = self.search_meta.index(verdieping_field)

        self.search_tuple = ['SHAPE@']
        self.search_tuple += self.search_meta

        self.fields_out = zip(self.meta_fields, field_types)

        self.meta_fields = ('SHAPE@', ) + self.meta_fields

        self.clusters = []

    def make_clusters(self):
        arcpy.AddMessage("Clustering projects...")
        count = 0
        arcpy.AddMessage("Searchtuple: {0}".format(self.search_tuple))
        for row in arcpy.da.SearchCursor(self.fl, self.search_tuple):
            shape = row[0]
            verdieping = row[self.verdieping_index]

            in_cluster = False
            for cluster in self.clusters:
                if cluster.overlaps(shape, verdieping) and not in_cluster:
                    in_cluster = True
                    cluster.add(shape, row, verdieping)
            if not in_cluster:
                new_cluster = Cluster()
                new_cluster.add(shape, row, verdieping)
                self.clusters.append(new_cluster)
            count += 1

        arcpy.AddMessage("Clustering done.")
        arcpy.AddMessage("{0} rows processed, {1} clusters created".format(count, len(self.clusters)))

    def write_data(self, cluster, fl):
        arcpy.AddMessage("Writing {1} rows of data to feature layer: {0}".format(fl, len(cluster.rowlist)))
        row_printed = 0
        with arcpy.da.InsertCursor(fl, self.meta_fields) as cursor:
            for row in cluster.rowlist:
                if row_printed < 3:
                    row_printed += 1
                    arcpy.AddMessage("Row = {0}\nFields = {1}".format(row, self.meta_fields))
                cursor.insertRow(row)

    def create_feature_layers(self):
        arcpy.AddMessage("Creating {0} feature layers in workspace: {1}".format(len(self.clusters), self.workspace))

        # Create a feature layer for each cluster
        for i, cluster in enumerate(self.clusters):
            fl_name = "{1}_{0:0>5}".format(i, self.fl_prefix)
            arcpy.CreateFeatureclass_management(self.workspace, fl_name, 'POLYGON')
            for field, ftype in self.fields_out:
                arcpy.AddMessage("Adding field {0} of type {1} to {2}".format(field, ftype, fl_name))
                arcpy.AddField_management(fl_name, field, ftype)
            self.write_data(cluster, fl_name)

        arcpy.AddMessage("Feature layers created")

    def run(self):
        self.make_clusters()
        self.create_feature_layers()

if __name__ == "__main__":
    try:
        arcpy.env.workspace = workspace

        builder = Clusterbuilder(fl_in, workspace, fieldmapper, verdieping_field)
        builder.run()
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
