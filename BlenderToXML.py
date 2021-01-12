from bpy import context

# from bs4 import BeautifulSoup

# User inputs
filename = "C:/output.xml"


# Returns origin, number of splines, curve name, and splines that make up curve from Blender
def getVars():
    objs = context.selected_objects
    obj = objs[0]
    origin = obj.location
    numSplines = len(obj.data.splines)
    curveName = str(obj.name)
    splines = obj.data.splines
    return origin, numSplines, curveName, splines


# Returns matrix of spline points
def getSplinePoints(spline):
    return [point.co for point in spline.points]
