from BlenderToXML import transformCoordinate

a = transformCoordinate([1, 2, 3])

assert(a == [0, 0, 0])
