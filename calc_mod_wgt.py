import arcpy
from pandas import DataFrame

# Set the workspace for ListFeatureClasses
arcpy.env.workspace = "G:\My Drive\Projects\SRCFloodVulnerability\SRCFloodVulnerability.gdb"

#fishnet_pts or fishnet_clip_mod are really the results tables that we neet to consider
#replace fn_pts_fc with results_table
#results_table = "fishnet_pts"
results_table = "fishnet_clip_mod"
#results_table = arcpy.GetParameterAsText(1)

#Really need a third parameter that is the anlaysis method
#so far we have a near analysis and a tabulate intersection 
#method = "near_net"
method = "tab_intersect"
#method = arcpy.GetParameterAsText(2)


#print(input)
arcpy.AddMessage("analysis table is: {0}".format(analysis_table))

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
analysis_table_df = table_to_pandas_dataframe(analysis_table)
results_table_df = table_to_pandas_dataframe(results_table)


#2. Loop through fishnet points calculating the weight accordingly using our near net dataframe.
#https://pro.arcgis.com/en/pro-app/arcpy/functions/searchcursor.htm
#https://www.listendata.com/2019/07/how-to-filter-pandas-dataframe.html
#https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.iterrows.html
oid_field = "OBJECTID"
update_field = ["ORIG_FID", "{0}_wgt".format(analysis_table.split('_')[0])]
for results_table_df_index, results_table_df_row in results_table_df.iterrows():
    analysis_table_query_df = analysis_table_df.query('IN_FID == {0}'.format(results_table_df_row[oid_field]))
    if analysis_table_query_df.empty == True:
        print("{0} not near any hazard features".format(results_table_df_row[oid_field]))
    else:
        with arcpy.da.UpdateCursor(results_table, update_field, "OBJECTID={0}".format(results_table_df_row[oid_field])) as update_cursor:
            for update_row in update_cursor:
                print("update row {0} as it has {1} points near it".format(results_table_df_row[oid_field], len(analysis_table_query_df)))
                print("attempting to update {0} {1}".format(update_row[1], "{0}_wgt".format(analysis_table.split('_')[0])))
                #TODO: Handle null case, with 0 value
                if len(analysis_table_query_df)>=5:
                    print("5")
                    update_row[1] = '5'
                else:
                    print("{0}".format(str(len(analysis_table_query_df))))
                    update_row[1] = str(len(analysis_table_query_df))
                update_cursor.updateRow(update_row) 