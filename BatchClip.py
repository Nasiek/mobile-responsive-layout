'''
                ###  BATCH WORKSPACE CLIP TOOL  ###

This tool will clip all input features that are in the same workspace
according to an input clip boundary.  There are options to use an SQL
query for the input clip boundary as well as using a buffer.

This tool accepts all shapefiles within the same folder as input clip
features, or all feature classes in a geodatabase as input clip features.
If feature datasets exist in the GDB, must use individual feature data-
sets as input.  The output clipped features are stored in a new file GDB.
'''

import arcpy, os, sys, traceback
from os import path as p
arcpy.env.overwriteOutput = True

# User Defined Variables
inft      = arcpy.GetParameterAsText(5)
clip_area = arcpy.GetParameterAsText(0) # Note:  It is frowned upon to have
ws        = arcpy.GetParameterAsText(3) # this many spaces between the 
gdb       = arcpy.GetParameterAsText(4) # variable and the '=' sign. This was 
query     = arcpy.GetParameterAsText(1) # done for display purposes.
buffdist  = arcpy.GetParameterAsText(2)
wildcard  = arcpy.GetParameterAsText(6)
Feature   = arcpy.GetParameterAsText(7)

# Constant Variable
clip_lyr = 'Clip_area_lyr'
outbuff = r'in_memory\out_buff_tmp'

try:

    # Define Clip Area 
    arcpy.MakeFeatureLayer_management(clip_area, clip_lyr, query)
    result = int(arcpy.GetCount_management(clip_lyr).getOutput(0))
    
    # Optional Buffer: If no buffer, original input clip boundary is used       
    if result:
        if ''.join([i for i in buffdist if i.isdigit()]) == '0':
            outbuff = clip_lyr                    
        else:
            arcpy.Buffer_analysis(clip_lyr, outbuff, buffdist)
            arcpy.AddMessage('\nBuffer Distance: '+ buffdist)   
        
        # Fix GDB Name  (just in case...)
        if not '.' in gdb:
            gdb = str(gdb).replace(' ', '_') + '.gdb'
        elif '.' in gdb:
            gdb = str(gdb).split('.')[0].replace(' ', '_') + '.gdb'  
            
        # Create New File GDB 
        arcpy.CreateFileGDB_management(ws, gdb, 'CURRENT')
        arcpy.AddMessage('\nCreated: ' + gdb + '\n')

        # Loop through workspace and clip all features
        arcpy.env.workspace = inft
        fclist = arcpy.ListFeatureClasses('%s' %wildcard, Feature)
        for fc in fclist:
            clipfc = p.join(ws, gdb, fc.split('.')[0])
            arcpy.Clip_analysis(fc, outbuff, clipfc)
            arcpy.AddMessage('Clipped: ' + fc)
            
        arcpy.AddMessage('\nBatch Clip Completed Successfully\n')
        
    else:
        arcpy.AddError('\nERROR:  Invalid SQL Statement:  No Selected Features')
        arcpy.AddError('ERROR:  Could not Clip Features (Invalid SQL Statement)')
        arcpy.AddError('\nBatch Clip Routine Failed\n')
                              
except:
    
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n     " +\
            str(sys.exc_type) + ": " + str(sys.exc_value) + "\n"
    msgs = "ARCPY ERRORS:\n" + arcpy.GetMessages(2) + "\n"
    arcpy.AddError(msgs)
    arcpy.AddError(pymsg)
    arcpy.AddMessage(arcpy.GetMessages(1))

