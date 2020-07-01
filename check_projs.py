import arcpy

# Set the workspace for ListFeatureClasses
arcpy.env.workspace = "G:\My Drive\GDC_Center_Files\Projects\SRC SeaGrant - Vulnerability Assessment\Santa Rosa County, FL\GIS Data\DataCleanUp.gdb"

# Use the ListFeatureClasses function to return a list of
#  shapefiles.
featureclasses = arcpy.ListFeatureClasses()

# Copy shapefiles to a file geodatabase
for fc in featureclasses:
    spatial_ref = arcpy.Describe(fc).spatialReference
    print("{} : {}".format(fc, spatial_ref.name))
    if spatial_ref.name != 'NAD_1983_StatePlane_Florida_North_FIPS_0903_Feet':
        print("reproj")
        arcpy.Project_management(fc, arcpy.Describe(fc).name+"0903", arcpy.SpatialReference("NAD 1983 StatePlane Florida North FIPS 0903 (US Feet)"))
            