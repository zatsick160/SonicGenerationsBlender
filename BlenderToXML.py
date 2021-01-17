import copy
import xml.etree.ElementTree as ET
from xml.dom import minidom

import numpy as np
from bpy import context

xmlPath = 'C:/SonicGenerations.xml'


def getBlenderObjVars(obj):
    origin = copy.deepcopy(obj.location)
    numSplines = len(obj.data.splines)
    curveName = str(obj.name)
    splines = obj.data.splines
    return origin, numSplines, curveName, splines


def processBlenderObjects():
    objs = context.selected_objects
    blenderVars = []
    for obj in objs:
        blenderVars.append(getBlenderObjVars(obj))
    return blenderVars


def getSplinePoints(spline):
    return copy.deepcopy([point.co for point in spline.points])


# Transforms a coordinate (multiply Y by negative 1 and swap Y and Z positions)
def transformCoordinate(spline_origin):
    spline_origin[1] = spline_origin[1] * -1
    spline_origin[1], spline_origin[2] = spline_origin[2], spline_origin[1]
    return spline_origin


# Transforms a spline points matrix into Invec, Outvec, and Point matrices
def transformMatrix(spline_points, translate):
    # Converting array to a variable
    points = np.array(spline_points)

    # Get rows and columns from raw data
    num_rows, num_cols = points.shape

    # CALCULATE POINTS: Multiply Y by negative 1 and swap Y and Z positions and apply translations
    for i in range(num_rows):
        points[i, 1] = points[i, 1] * -1
        points[i, 1], points[i, 2] = points[i, 2], points[i, 1]
        points[i, 0] = points[i, 0]
        points[i, 1] = points[i, 1]
        points[i, 2] = points[i, 2]

    # CALCULATE INVECS: Apply math to points
    invecs = np.zeros([num_rows, num_cols])
    for i in range(num_rows):
        if (i == 0):
            invecs[i, 0] = points[i, 0]
            invecs[i, 1] = points[i, 1]
            invecs[i, 2] = points[i, 2]
        else:
            invecs[i, 0] = points[i, 0] - (1 / 3) * (points[i, 0] - points[i - 1, 0])
            invecs[i, 1] = points[i, 1] - (1 / 3) * (points[i, 1] - points[i - 1, 1])
            invecs[i, 2] = points[i, 2] - (1 / 3) * (points[i, 2] - points[i - 1, 2])

    # CALCULATE OUTVECS: Apply math to points
    outvecs = np.zeros([num_rows, num_cols])
    for i in range(num_rows):
        if i == num_rows - 1:
            outvecs[i, 0] = points[i, 0]
            outvecs[i, 1] = points[i, 1]
            outvecs[i, 2] = points[i, 2]
        else:
            outvecs[i, 0] = points[i, 0] + (1 / 3) * (points[i + 1, 0] - points[i, 0])
            outvecs[i, 1] = points[i, 1] + (1 / 3) * (points[i + 1, 1] - points[i, 1])
            outvecs[i, 2] = points[i, 2] + (1 / 3) * (points[i + 1, 2] - points[i, 2])

    # Returning values
    return invecs, outvecs, points


def stringCreator(value1, value2, value3):
    string1, string2, string3 = '%.5f' % value1, '%.5f' % value2, '%.5f' % value3
    string = string1 + " " + string2 + " " + string3
    return string


def generateXMLHeader():
    # XML header
    root = ET.Element("SonicPath")

    # XML Geometry
    lib = ET.Element("library", type="GEOMETRY")
    root.append(lib)

    return root, lib


def generateXMLBody(root, lib, num_splines, curve_name, invec_right, outvec_right, point_right, invec_left, outvec_left, point_left, translate):

    geo = ET.Element("geometry", id=curve_name + "-geometry", name=curve_name + "-geometry")
    lib.append(geo)
    spl = ET.Element("spline", count=str(num_splines), width="0")
    geo.append(spl)

    num_rows, num_cols = invec_right.shape

    spl3d = ET.Element("spline3d", count=str(num_rows))
    spl.append(spl3d)

    for i in range(num_rows):
        knot = ET.Element("knot", type="corner")
        spl3d.append(knot)
        inv = ET.SubElement(knot, "invec")
        inv_string = stringCreator(invec_right[i, 0], invec_right[i, 1], invec_right[i, 2])
        inv.text = inv_string
        out = ET.SubElement(knot, "outvec")
        out_string = stringCreator(outvec_right[i, 0], outvec_right[i, 1], outvec_right[i, 2])
        out.text = out_string
        pnt = ET.SubElement(knot, "point")
        pnt_string = stringCreator(point_right[i, 0], point_right[i, 1], point_right[i, 2])
        pnt.text = pnt_string

    if num_splines == 2:

        spl3d = ET.Element("spline3d", count=str(num_rows))
        spl.append(spl3d)

        for i in range(num_rows):
            knot = ET.Element("knot", type="corner")
            spl3d.append(knot)
            inv = ET.SubElement(knot, "invec")
            inv_string = stringCreator(invec_left[i, 0], invec_left[i, 1], invec_left[i, 2])
            inv.text = inv_string
            out = ET.SubElement(knot, "outvec")
            out_string = stringCreator(outvec_left[i, 0], outvec_left[i, 1], outvec_left[i, 2])
            out.text = out_string
            pnt = ET.SubElement(knot, "point")
            pnt_string = stringCreator(point_left[i, 0], point_left[i, 1], point_left[i, 2])
            pnt.text = pnt_string

    scene = ET.Element("scene", id="DefaultScene")
    root.append(scene)

    node = ET.Element("node", id=curve_name, name=curve_name)
    scene.append(node)

    trans = ET.SubElement(node, "translate")
    trans_string = stringCreator(translate[0], translate[1], translate[2])
    trans.text = trans_string

    scale = ET.SubElement(node, "scale")
    scale.text = "1 1 1"

    rotate = ET.SubElement(node, "rotate")
    rotate.text = "0 0 0 1"

    instance = ET.Element("instance", url="#" + curve_name + "-geometry")
    node.append(instance)


def writeXML(outputPath, root):

    # Writing root to XML file
    xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="     ")

    with open(outputPath, "w") as f:
        f.write(xmlstr)


def processData():

    outputPath = xmlPath

    # Get parameters from Blender curves
    blenderVars = processBlenderObjects()

    root, lib = generateXMLHeader()

    for i in range(blenderVars):
        spline_origin, num_splines, curve_name, splines = getBlenderObjVars(blenderVars[i])
        translate = transformCoordinate(spline_origin)

        # Process data
        if num_splines == 1:
            center = getSplinePoints(splines[0])
            invec_center, outvec_center, point_center = transformMatrix(center, translate)
            generateXMLBody(root, lib, num_splines, curve_name, invec_center, outvec_center, point_center, 0, 0, 0, translate)
        elif num_splines == 2:
            right = getSplinePoints(splines[0])
            invec_right, outvec_right, point_right = transformMatrix(right, translate)
            left = getSplinePoints(splines[1])
            invec_left, outvec_left, point_left = transformMatrix(left, translate)
            generateXMLBody(root, lib, num_splines, curve_name, invec_right, outvec_right, point_right, invec_left, outvec_left, point_left, translate)

    writeXML(outputPath, root)


if __name__ == "__main__":
    processData()
