# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import shapefile
import bokeh.plotting as bpl
import matplotlib.cm as mpc
import pdb
import matplotlib.pyplot as plt


# read the shapefile and initialize the map
def initialize_map(filename, plot_width):

    # Read the shapefile
    dat = shapefile.Reader(filename, plot_width)
    
    # Create the list of regions
    # Get list of regions
    regions = set([i[2] for i in dat.iterRecords()])
    region_names = {
            '1': "Höfuðborgarsvæði",
            '2': "Vesturland",
            '3': "Vestfirðir",
            '4': "Norðurland vestra",
            '5': "Norðurland eystra",
            '6': "Austurland",
            '7': "Suðurland",
            '8': "Suðurland",
            '9': "Höfuðborgarsvæði",
            }

    #nRegions = len(regions)
    #colormap = mpc.autumn
    #show_colormap(colormap,2)
    #pdb.set_trace()
    #bpl.output_file(filename + '.html')

    # some basic tools
    #TOOLS = "pan,wheel_zoom, box_zoom, reset, previewsave"
    TOOLS = "previewsave"
    ice_map = bpl.figure(title = 'Map of Iceland',tools=TOOLS, plot_width = plot_width)
    i = 0 
    for region in regions:
        data = getDict(region,dat)
        ice_map.patches(data[region]['lat_list'],data[region]['lng_list'], line_color='black', name="map_regions")
        i += 1

    return ice_map, 

# Given a shapeObject return a list of list for latitude and longitudes values
#       - Handle scenarios where there are multiple parts to a shapeObj
def getParts ( shapeObj ):

    points = []

    num_parts = len( shapeObj.parts )
    end = len( shapeObj.points ) - 1
    segments = list( shapeObj.parts ) + [ end ]


    for i in range( num_parts ):
        points.append( shapeObj.points[ segments[i]:segments[i+1] ] )


    return points


# Return a dict with three elements
#        - state_name
#        - total_area
#        - list of list representing latitudes
#        - list of list representing longitudes
#
#  Input: State Name & ShapeFile Object

def getDict ( state_name, shapefile ):

    stateDict = {state_name: {} }

    rec = []
    shp = []
    points = []


    # Select only the records representing the
    # "state_name" and discard all other
    for i in shapefile.shapeRecords( ):

        if i.record[2] == state_name:
            rec.append(i.record)
            shp.append(i.shape)

    # In a multi record state for calculating total area
    # sum up the area of all the individual records
    #        - first record element represents area in cms^2
    total_area = sum( [float(i[0]) for i in rec] ) / (1000*1000)


    # For each selected shape object get
    # list of points while considering the cases where there may be
    # multiple parts  in a single record
    for j in shp:
        for i in getParts(j):
            points.append(i)

    # Prepare the dictionary
    # Seperate the points into two separate lists of lists (easier for bokeh to consume)
    #      - one representing latitudes
    #      - second representing longitudes

    lat = []
    lng = []
    for i in points:
        lat.append( [j[0] for j in i] )
        lng.append( [j[1] for j in i] )


    stateDict[state_name]['lat_list'] = lat
    stateDict[state_name]['lng_list'] = lng
    stateDict[state_name]['total_area'] = total_area

    return stateDict
