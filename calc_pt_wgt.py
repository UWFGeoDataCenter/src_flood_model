import arcpy
from pandas import DataFrame

# Set the workspace for ListFeatureClasses
arcpy.env.workspace = "G:\My Drive\Projects\SRCFloodVulnerability\SRCFloodVulnerability.gdb"

in_near_net = "rls_near_net"
#in_near_net = arcpy.GetParameterAsText(0)
fn_pts_fc = "fishnet_pts"



print(input)
arcpy.AddMessage("{0} input".format(in_near_net))

def get_field_names(table):
    """
    Get a list of field names not inclusive of the geometry and object id fields.
    :param table: Table readable by ArcGIS
    :return: List of field names.
    source: https://joelmccune.com/arcgis-to-pandas-data-frame-using-a-search-cursor/
    """
    # list to store values
    field_list = []
    # iterate the fields
    for field in arcpy.ListFields(table):
        # if the field is not geometry nor object id, add it as is
        #if field.type != 'Geometry' and field.type != 'OID':
        if field.type != 'Geometry':
            field_list.append(field.name)
        # if geomtery is present, add both shape x and y for the centroid
        elif field.type == 'Geometry':
            field_list.append('SHAPE@XY')
    # return the field list
    return field_list

def table_to_pandas_dataframe(table, field_names=None):
    """
    Load data into a Pandas Data Frame for subsequent analysis.
    :param table: Table readable by ArcGIS.
    :param field_names: List of fields.
    :return: Pandas DataFrame object
    source: https://joelmccune.com/arcgis-to-pandas-data-frame-using-a-search-cursor/.
    """
    # if field names are not specified
    if not field_names:
        # get a list of field names
        field_names = get_field_names(table)
    # create a pandas data frame
    dataframe = DataFrame(columns=field_names, dtype=str)
    # use a search cursor to iterate rows
    with arcpy.da.SearchCursor(table, field_names) as search_cursor:
        # iterate the rows
        for row in search_cursor:
            # combine the field names and row items together, and append them
            dataframe = dataframe.append(
                dict(zip(field_names, row), dtype=str), 
                ignore_index=True
            )
    # return the pandas data frame
    return dataframe

#1. Populate our dataframe from the featureclass
in_near_net_df = table_to_pandas_dataframe(in_near_net)
fn_pts_fc_df = table_to_pandas_dataframe(fn_pts_fc)
#will tell you the types of a dataframe
#fn_pts_fc_df.dtypes 
#in_near_net_df.dtypes


#2. Add the weight colument to the fishnet points
#AddField(in_table, field_name, field_type, {field_precision}, {field_scale}, {field_length}, {field_alias}, {field_is_nullable}, {field_is_required}, {field_domain})
field_names = [f.name for f in arcpy.ListFields(fn_pts_fc)]
print(field_names)
print(in_near_net.split('_')[0])
if ("{0}_wgt".format(in_near_net.split('_')[0]) not in field_names): 
    arcpy.AddField_management(fn_pts_fc, "{0}_wgt".format(in_near_net.split('_')[0]), "TEXT", field_alias="{0}_wgt".format(in_near_net.split('_')[0]), field_is_nullable="NULLABLE")
else:
    print("field already created")

#3. Loop through fishnet points calculating the weight accordingly using our near net dataframe.
#https://pro.arcgis.com/en/pro-app/arcpy/functions/searchcursor.htm
#https://www.listendata.com/2019/07/how-to-filter-pandas-dataframe.html
#https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.iterrows.html
oid_field = "OBJECTID"
update_fields = ["ORIG_FID", "{0}_wgt".format(in_near_net.split('_')[0])]

for fn_pts_fc_df_index, fn_pts_fc_df_row in fn_pts_fc_df.iterrows():
    in_near_net_query_df = in_near_net_df.query('IN_FID == {0}'.format(fn_pts_fc_df_row[oid_field]))
    if in_near_net_query_df.empty == True:
        print("{0} not near any hazard features".format(fn_pts_fc_df_row[oid_field]))
    else:
        #print("got here")
        with arcpy.da.UpdateCursor(fn_pts_fc, update_fields, "OBJECTID={0}".format(fn_pts_fc_df_row[oid_field])) as update_cursor:
            for update_row in update_cursor:
                print("update row {0} as it has {1} points near it".format(fn_pts_fc_df_row[oid_field], len(in_near_net_query_df)))
                print("attempting to update {0} {1}".format(update_row[1], "{0}_wgt".format(in_near_net.split('_')[0])))
                #TODO: Handle null case, with 0 value
                if len(in_near_net_query_df)>=5:
                    print("5")
                    update_row[1] = '5'
                else:
                    print("{0}".format(str(len(in_near_net_query_df))))
                    update_row[1] = str(len(in_near_net_query_df))
                update_cursor.updateRow(update_row) 